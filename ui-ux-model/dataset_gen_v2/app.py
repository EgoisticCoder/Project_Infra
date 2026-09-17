"""
app.py — CLI + terminal UI for the UI/UX dataset generator.

Usage:
    python3 app.py                                   # fully interactive
    python3 app.py --limit 500 --provider groq       # pre-fill, still asks for key/model in-app
    python3 app.py --limit 50 --provider openrouter --model "qwen/qwen3.6-27b" --output run1.jsonl

API keys are NEVER accepted as a CLI flag on purpose — typing them in the TUI
each session keeps them out of shell history, process lists, and .bash_history.

Screens:
  MenuScreen    -> pick "Generate samples" or "Merge datasets"
  SetupScreen   -> configure provider(s) + optional screenshot stage, then Run
  RunScreen     -> live generation progress (1 or 2 concurrent workers)
  PrepareScreen -> merge your own dataset.jsonl with external datasets (WebSight
                   etc.) into one training file — the GUI front-end for
                   prepare_training_data.run_merge(), so you don't need the CLI
                   for this step unless you want it.

CHANGE LOG (this revision):
- Fixed a race condition: Provider B's worker could read self._client_a before
  Provider A's worker had set it. Both clients are now built up front on the
  main thread in on_mount(), before either worker thread starts.
- Screenshot stage now covers all three query types (rate/improve/recreate),
  matching pipeline.py's extended run_pipeline_for_sample — checkbox label and
  cost hint updated accordingly (now ~4 extra calls/sample, not 2).
- Added MenuScreen + PrepareScreen for combining your own dataset with the
  external ones (WebSight recommended-on, Screen2Words recommended-off) right
  from the GUI, instead of requiring a separate prepare_training_data.py CLI run.
"""

import argparse
import json
import threading
from pathlib import Path

from textual import work
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import (
    Header, Footer, Label, Input, Select, Button, Checkbox, DataTable, RichLog, ProgressBar,
)

from pipeline import (
    PROVIDER_PRESETS, build_client, build_sample_matrix, split_matrix,
    run_pipeline_for_sample, FatalProviderError, Sample,
)
import prepare_training_data as ptd


# ------------------------------------------------------------------ #
# Menu screen — choose generate vs merge
# ------------------------------------------------------------------ #
class MenuScreen(Screen):
    BINDINGS = [("q", "app.quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(id="menu"):
            yield Label("UI/UX Dataset Generator", id="title")
            yield Label("What do you want to do?", classes="hint")
            yield Button("Generate new samples", id="menu_generate", variant="primary")
            yield Button("Merge datasets into a training file", id="menu_merge")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "menu_generate":
            self.app.push_screen(SetupScreen(self.app.cli_defaults))
        elif event.button.id == "menu_merge":
            self.app.push_screen(PrepareScreen())


# ------------------------------------------------------------------ #
# Setup screen — pick provider(s) / model(s) / key(s) / limit / output file
# ------------------------------------------------------------------ #
class SetupScreen(Screen):
    BINDINGS = [("q", "app.quit", "Quit")]

    def __init__(self, cli_defaults: dict):
        super().__init__()
        self.cli_defaults = cli_defaults

    def compose(self) -> ComposeResult:
        d = self.cli_defaults
        preset_options = [(f"{name}  ({url})", name) for name, url in PROVIDER_PRESETS.items()]
        preset_options.append(("custom — type base_url below", "custom"))

        yield Header()
        with VerticalScroll(id="setup_form"):
            yield Label("UI/UX Dataset Generator — Setup", id="title")

            yield Label("── Provider A (required) ──", classes="section")
            yield Label("Provider preset:")
            yield Select(preset_options, id="provider_select",
                         value=d.get("provider") or "groq", allow_blank=False)
            yield Label("Base URL (auto-filled from preset, editable):")
            yield Input(value=PROVIDER_PRESETS.get(d.get("provider") or "groq", ""), id="base_url")
            yield Label("API key (typed only, never saved to disk):")
            yield Input(password=True, placeholder="sk-...", id="api_key")
            yield Label("Model name:")
            yield Input(value=d.get("model") or "", placeholder="e.g. llama-3.1-8b-instant", id="model")

            yield Label("── Provider B (optional — leave Base URL blank to skip) ──", classes="section")
            yield Label("Runs concurrently with Provider A, splitting the sample matrix "
                         "roughly in half to cut total time.", classes="hint")
            yield Label("Provider preset:")
            yield Select(preset_options, id="provider_select_b", value="custom", allow_blank=False)
            yield Label("Base URL:")
            yield Input(value="", id="base_url_b")
            yield Label("API key:")
            yield Input(password=True, placeholder="sk-... (leave blank to disable Provider B)", id="api_key_b")
            yield Label("Model name:")
            yield Input(value="", id="model_b")

            yield Label("── Optional: screenshot stage (rate + improve + recreate) ──", classes="section")
            yield Label("Adds implement -> render -> {rate, improve, recreate} after each sample. "
                         "Slower and pricier (one extra render + ~4 extra API calls per sample) but "
                         "teaches the model the actual deployed task: a user uploads their current "
                         "site and asks to rate it, improve it, or get a recreated version. Both "
                         "model names below are called via Provider A's credentials.",
                         classes="hint")
            yield Checkbox("Enable screenshot stage", id="enable_screenshot", value=False)
            yield Label("Code model (must be capable of writing HTML/CSS):")
            yield Input(value="", placeholder="e.g. qwen/qwen3-coder-30b", id="code_model")
            yield Label("Vision model (must accept image input):")
            yield Input(value="", placeholder="e.g. qwen/qwen3-vl-8b-instruct", id="vision_model")

            yield Label("── Run settings ──", classes="section")
            yield Label("Number of samples (--limit):")
            yield Input(value=str(d.get("limit") or 20), id="limit")
            yield Label("Output file (JSONL, appended):")
            yield Input(value=d.get("output") or "dataset.jsonl", id="output")
            yield Label("", id="form_error")
            yield Button("Start generating", id="start", variant="primary")
            yield Button("Back to menu", id="back")
        yield Footer()

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "provider_select" and event.value != "custom":
            self.query_one("#base_url", Input).value = PROVIDER_PRESETS.get(str(event.value), "")
        elif event.select.id == "provider_select_b" and event.value != "custom":
            self.query_one("#base_url_b", Input).value = PROVIDER_PRESETS.get(str(event.value), "")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()
            return
        if event.button.id != "start":
            return
        base_url = self.query_one("#base_url", Input).value.strip()
        api_key = self.query_one("#api_key", Input).value.strip()
        model = self.query_one("#model", Input).value.strip()
        provider_name = str(self.query_one("#provider_select", Select).value)

        base_url_b = self.query_one("#base_url_b", Input).value.strip()
        api_key_b = self.query_one("#api_key_b", Input).value.strip()
        model_b = self.query_one("#model_b", Input).value.strip()
        provider_name_b = str(self.query_one("#provider_select_b", Select).value)

        enable_screenshot = self.query_one("#enable_screenshot", Checkbox).value
        code_model = self.query_one("#code_model", Input).value.strip()
        vision_model = self.query_one("#vision_model", Input).value.strip()

        limit_raw = self.query_one("#limit", Input).value.strip()
        output = self.query_one("#output", Input).value.strip()
        error_label = self.query_one("#form_error", Label)

        if not base_url or not api_key or not model or not output:
            error_label.update("[red]All Provider A fields and output are required.[/red]")
            return

        provider_b_configured = bool(base_url_b)
        if provider_b_configured and not (api_key_b and model_b):
            error_label.update("[red]Provider B: fill in API key and model too, or clear "
                                "Base URL to disable it.[/red]")
            return

        if enable_screenshot and not (code_model and vision_model):
            error_label.update("[red]Screenshot stage is checked — fill in both the code "
                                "model and vision model names.[/red]")
            return

        try:
            limit = int(limit_raw)
            if limit <= 0:
                raise ValueError
        except ValueError:
            error_label.update("[red]Limit must be a positive whole number.[/red]")
            return

        error_label.update("")
        self.app.push_screen(RunScreen(
            base_url=base_url, api_key=api_key, model=model, provider_name=provider_name,
            base_url_b=base_url_b if provider_b_configured else "",
            api_key_b=api_key_b, model_b=model_b, provider_name_b=provider_name_b,
            enable_screenshot=enable_screenshot, code_model=code_model, vision_model=vision_model,
            limit=limit, output=output,
        ))


# ------------------------------------------------------------------ #
# Run screen — live table + log while generation happens in worker thread(s)
# ------------------------------------------------------------------ #
class RunScreen(Screen):
    BINDINGS = [("q", "quit_run", "Quit")]

    def __init__(self, base_url: str, api_key: str, model: str, provider_name: str,
                 base_url_b: str, api_key_b: str, model_b: str, provider_name_b: str,
                 enable_screenshot: bool, code_model: str, vision_model: str,
                 limit: int, output: str):
        super().__init__()
        self.base_url, self.api_key, self.model, self.provider_name = base_url, api_key, model, provider_name
        self.base_url_b, self.api_key_b, self.model_b, self.provider_name_b = (
            base_url_b, api_key_b, model_b, provider_name_b)
        self.provider_b_configured = bool(base_url_b)
        self.enable_screenshot = enable_screenshot
        self.code_model, self.vision_model = code_model, vision_model
        self.limit = limit
        self.output_path = Path(output)

        self.rows: dict = {}   # global idx -> dict of current row values, table redrawn from this
        self.done_count = 0
        self.fail_count = 0
        self._write_lock = threading.Lock()
        self._counts_lock = threading.Lock()
        self._active_lock = threading.Lock()
        self._active_workers = 0
        self._client_a = None  # built on the main thread in on_mount, before any worker starts

    def compose(self) -> ComposeResult:
        yield Header()
        yield ProgressBar(total=self.limit, id="progress")
        yield DataTable(id="table")
        yield RichLog(id="log", wrap=True, markup=True)
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#table", DataTable)
        table.add_columns("#", "Provider", "App Type", "Context", "Status", "Preview")
        log = self.query_one("#log", RichLog)
        log.write(f"[bold]Provider A:[/bold] {self.provider_name} / {self.model}")
        if self.provider_b_configured:
            log.write(f"[bold]Provider B:[/bold] {self.provider_name_b} / {self.model_b}  "
                      f"[dim](running concurrently)[/dim]")
        if self.enable_screenshot:
            log.write(f"[bold]Screenshot stage:[/bold] on (rate+improve+recreate) — "
                      f"code={self.code_model}, vision={self.vision_model} (via Provider A creds)")
        log.write(f"[bold]Output:[/bold] {self.output_path.resolve()}   "
                   f"[bold]Samples:[/bold] {self.limit}")
        log.write("Press 'q' at any time to stop — samples already written stay on disk.\n")

        # Build BOTH clients up front, on the main thread, before any worker
        # thread starts — this is what fixes the earlier race condition where
        # Provider B's worker could read self._client_a before it existed.
        try:
            self._client_a = build_client(self.base_url, self.api_key)
        except Exception as e:
            log.write(f"[red]Could not create Provider A client: {e}[/red]")
            return
        client_b = None
        if self.provider_b_configured:
            try:
                client_b = build_client(self.base_url_b, self.api_key_b)
            except Exception as e:
                log.write(f"[red]Could not create Provider B client: {e} — continuing with "
                          f"Provider A only.[/red]")
                self.provider_b_configured = False

        full_matrix = build_sample_matrix(self.limit)
        already_done = 0
        if self.output_path.exists():
            with self.output_path.open("r", encoding="utf-8") as f:
                already_done = sum(1 for _ in f)
        if already_done > 0:
            log.write(f"[cyan]Resuming — {already_done} sample(s) already in "
                      f"{self.output_path.name}, continuing from #{already_done + 1}.[/cyan]")
            self.query_one("#progress", ProgressBar).update(progress=min(already_done, self.limit))
            self.done_count = already_done

        remaining = full_matrix[already_done:]
        indexed_remaining = [(already_done + i + 1, app_type, seed_hint)
                              for i, (app_type, seed_hint) in enumerate(remaining)]

        n_workers = 2 if self.provider_b_configured else 1
        chunks = split_matrix(indexed_remaining, n_workers)
        self._active_workers = n_workers

        self.generate_worker_a(self._client_a, chunks[0])
        if self.provider_b_configured:
            self.generate_worker_b(client_b, chunks[1])

    def action_quit_run(self) -> None:
        self.app.exit()

    def _redraw_table(self) -> None:
        table = self.query_one("#table", DataTable)
        table.clear()
        for idx in sorted(self.rows):
            r = self.rows[idx]
            table.add_row(str(idx), r["provider"], r["app_type"], r["context"], r["status"], r["preview"])

    def _on_sample_update(self, idx: int, provider_label: str, sample: Sample) -> None:
        """Called (via call_from_thread) every time a sample's stage changes."""
        preview = (sample.final or sample.draft or "")[:50].replace("\n", " ")
        self.rows[idx] = {
            "provider": provider_label, "app_type": sample.app_type, "context": sample.seed_hint,
            "status": sample.status, "preview": preview,
        }
        self._redraw_table()

    def _write_sample(self, sample: Sample) -> None:
        with self._write_lock:
            with self.output_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(sample.to_json_dict(), ensure_ascii=False) + "\n")

    def _run_worker(self, provider_label: str, client, model: str, provider_name: str, items: list) -> None:
        """
        Core loop, shared by both worker methods below. Runs inside whichever
        thread called it — not itself @work-decorated, so it's reusable without
        Textual trying to schedule it as a separate worker.
        """
        log = self.query_one("#log", RichLog)
        progress = self.query_one("#progress", ProgressBar)

        # The screenshot stage always routes through Provider A's client — see
        # the module docstring for why (one shared vision/code model config,
        # regardless of which provider drafted the underlying text sample).
        code_client = self._client_a
        vision_client = self._client_a

        for idx, app_type, seed_hint in items:
            def cb(sample: Sample, idx=idx, provider_label=provider_label):
                self.app.call_from_thread(self._on_sample_update, idx, provider_label, sample)

            try:
                sample = run_pipeline_for_sample(
                    client, model, app_type, seed_hint, provider_name, status_cb=cb,
                    enable_screenshot=self.enable_screenshot,
                    code_client=code_client, code_model=self.code_model,
                    vision_client=vision_client, vision_model=self.vision_model,
                )
            except FatalProviderError as e:
                self.app.call_from_thread(
                    log.write, f"[red bold]Provider {provider_label} STOPPED — {e}[/red bold]\n"
                               f"Its remaining samples were not attempted — relaunch to resume them."
                )
                self._finish_worker()
                return

            self._write_sample(sample)
            self.app.call_from_thread(progress.advance, 1)

            with self._counts_lock:
                if sample.status == "done":
                    self.done_count += 1
                else:
                    self.fail_count += 1

            if sample.status == "done":
                self.app.call_from_thread(
                    log.write, f"[green]#{idx} ({provider_label}) done[/green] — {app_type} / {seed_hint}")
            else:
                self.app.call_from_thread(
                    log.write, f"[yellow]#{idx} ({provider_label}) failed[/yellow] — "
                               f"{app_type} / {seed_hint}: {sample.error}")

        self._finish_worker()

    def _finish_worker(self) -> None:
        with self._active_lock:
            self._active_workers -= 1
            remaining = self._active_workers
        if remaining == 0:
            log = self.query_one("#log", RichLog)
            self.app.call_from_thread(
                log.write,
                f"\n[bold]All workers finished.[/bold] {self.done_count} done, {self.fail_count} failed. "
                f"Written to {self.output_path.resolve()}. Press 'q' to quit."
            )

    @work(thread=True, exclusive=False)
    def generate_worker_a(self, client, items: list) -> None:
        self._run_worker("A", client, self.model, self.provider_name, items)

    @work(thread=True, exclusive=False)
    def generate_worker_b(self, client, items: list) -> None:
        self._run_worker("B", client, self.model_b, self.provider_name_b, items)


# ------------------------------------------------------------------ #
# Prepare screen — merge own dataset + external datasets into a training file
# ------------------------------------------------------------------ #
class PrepareScreen(Screen):
    BINDINGS = [("q", "app.quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(id="prep_form"):
            yield Label("Merge Datasets", id="title")
            yield Label("Combines your own generated samples with external datasets into one "
                        "training file — the GUI version of prepare_training_data.py.",
                        classes="hint")

            yield Label("Your dataset (from the Generate screen):")
            yield Input(value="dataset.jsonl", id="own_path")
            yield Label("Include the rate/improve/recreate screenshot examples, if present:")
            yield Checkbox("Include vision examples", id="include_vision", value=True)

            yield Label("── WebSight (recommended — real code+screenshot pairs) ──", classes="section")
            yield Checkbox("Include WebSight", id="include_websight",
                           value=ptd.RECOMMENDED_DEFAULTS["websight"])
            yield Label("Row limit (0 = use all 823k — see hint):")
            yield Input(value="0", id="websight_limit")
            yield Label("0 uses the entire dataset. With ~15-19k of your own samples, that's a "
                        "~98/2 split — fine if you oversample your own data at TRAIN time; "
                        "otherwise set a cap here (2000-5000 is a reasonable start).",
                        classes="hint")

            yield Label("── Screen2Words (NOT recommended — reverse task) ──", classes="section")
            yield Checkbox("Include Screen2Words", id="include_screen2words",
                           value=ptd.RECOMMENDED_DEFAULTS["screen2words"])
            yield Label("Row limit (0 = use all):")
            yield Input(value="0", id="screen2words_limit")
            yield Label("Screen-captioning is the reverse of your design-generation task. Only "
                        "turn this on if you have a specific reason to.", classes="hint")

            yield Label("Output file:")
            yield Input(value="train_merged.jsonl", id="merge_output")
            yield Label("", id="prep_error")
            yield Button("Run merge", id="run_merge", variant="primary")
            yield Button("Back to menu", id="back")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()
            return
        if event.button.id != "run_merge":
            return

        own_path = self.query_one("#own_path", Input).value.strip()
        output_path = self.query_one("#merge_output", Input).value.strip()
        error_label = self.query_one("#prep_error", Label)

        if not own_path or not output_path:
            error_label.update("[red]Both the dataset path and output path are required.[/red]")
            return
        if not Path(own_path).exists():
            error_label.update(f"[red]{own_path} doesn't exist yet — run Generate first.[/red]")
            return

        def _int_or(id_: str, default: int = 0) -> int:
            raw = self.query_one(f"#{id_}", Input).value.strip()
            try:
                return int(raw)
            except ValueError:
                return default

        error_label.update("")
        self.merge_worker(
            own_path=own_path, output_path=output_path,
            include_vision=self.query_one("#include_vision", Checkbox).value,
            include_websight=self.query_one("#include_websight", Checkbox).value,
            websight_limit=_int_or("websight_limit"),
            include_screen2words=self.query_one("#include_screen2words", Checkbox).value,
            screen2words_limit=_int_or("screen2words_limit"),
        )

    @work(thread=True, exclusive=True)
    def merge_worker(self, own_path: str, output_path: str, include_vision: bool,
                      include_websight: bool, websight_limit: int,
                      include_screen2words: bool, screen2words_limit: int) -> None:
        log = RichLog(id="merge_log", wrap=True, markup=True)
        # RichLog needs to be mounted before it can be written to from a thread;
        # mount it once, on the main thread, then log through call_from_thread.
        def mount_log():
            self.mount(log)
        self.app.call_from_thread(mount_log)

        def cb(msg: str):
            self.app.call_from_thread(log.write, msg)

        try:
            counts = ptd.run_merge(
                own_dataset_path=own_path, output_path=output_path,
                include_websight=include_websight, websight_limit=websight_limit,
                include_screen2words=include_screen2words, screen2words_limit=screen2words_limit,
                include_vision_examples=include_vision, progress_cb=cb,
            )
        except Exception as e:
            self.app.call_from_thread(log.write, f"[red bold]Merge failed: {e}[/red bold]")
            return

        self.app.call_from_thread(log.write, "\n[bold]Source mix:[/bold]")
        for source, count in sorted(counts.items()):
            if source != "_total":
                self.app.call_from_thread(log.write, f"  {source}: {count}")
        self.app.call_from_thread(
            log.write, f"\n[bold green]TOTAL: {counts['_total']}[/bold green] — written to {output_path}"
        )


# ------------------------------------------------------------------ #
# App shell
# ------------------------------------------------------------------ #
class DatasetGenApp(App):
    CSS = """
    #setup_form, #prep_form, #menu { padding: 1 2; }
    #title { text-style: bold; padding-bottom: 1; }
    .section { text-style: bold; padding-top: 1; color: $accent; }
    .hint { color: $text-muted; padding-bottom: 1; }
    #form_error, #prep_error { color: red; padding-bottom: 1; }
    #table { height: 1fr; }
    #log, #merge_log { height: 12; border: solid grey; }
    """

    def __init__(self, cli_defaults: dict):
        super().__init__()
        self.cli_defaults = cli_defaults

    def on_mount(self) -> None:
        self.push_screen(MenuScreen())


def parse_args() -> dict:
    parser = argparse.ArgumentParser(
        description="Generate a UI/UX-design dataset via generate->ground->critique->revise, "
                    "with an optional rate/improve/recreate screenshot stage."
    )
    parser.add_argument("--limit", type=int, default=None,
                         help="Number of samples to generate (asked in-app if omitted).")
    parser.add_argument("--provider", choices=list(PROVIDER_PRESETS) + ["custom"], default=None,
                         help="Provider A preset (base_url pre-filled; still editable in-app).")
    parser.add_argument("--model", type=str, default=None,
                         help="Model name for Provider A.")
    parser.add_argument("--output", type=str, default=None,
                         help="Output JSONL path (default: dataset.jsonl).")
    args = parser.parse_args()
    return {"limit": args.limit, "provider": args.provider, "model": args.model, "output": args.output}


if __name__ == "__main__":
    defaults = parse_args()
    DatasetGenApp(defaults).run()
