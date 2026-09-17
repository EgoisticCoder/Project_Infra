"""
app.py — CLI + terminal UI for the UI/UX dataset generator.

Usage:
    python3 app.py                                   # fully interactive
    python3 app.py --limit 500 --provider groq       # pre-fill, still asks for key/model in-app
    python3 app.py --limit 50 --provider openrouter --model "qwen/qwen3.6-27b" --output run1.jsonl

API keys are NEVER accepted as a CLI flag on purpose — typing them in the TUI
each session keeps them out of shell history, process lists, and .bash_history.
"""

import argparse
import json
from pathlib import Path

from textual import work
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import (
    Header, Footer, Label, Input, Select, Button, DataTable, RichLog, ProgressBar,
)

from pipeline import (
    PROVIDER_PRESETS, build_client, build_sample_matrix, run_pipeline_for_sample,
    FatalProviderError, Sample,
)


# ------------------------------------------------------------------ #
# Setup screen — pick provider / model / key / limit / output file
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
            yield Label("Provider preset:")
            yield Select(preset_options, id="provider_select",
                         value=d.get("provider") or "groq", allow_blank=False)
            yield Label("Base URL (auto-filled from preset, editable):")
            yield Input(value=PROVIDER_PRESETS.get(d.get("provider") or "groq", ""), id="base_url")
            yield Label("API key (typed only, never saved to disk):")
            yield Input(password=True, placeholder="sk-...", id="api_key")
            yield Label("Model name:")
            yield Input(value=d.get("model") or "", placeholder="e.g. llama-3.1-8b-instant", id="model")
            yield Label("Number of samples (--limit):")
            yield Input(value=str(d.get("limit") or 20), id="limit")
            yield Label("Output file (JSONL, appended):")
            yield Input(value=d.get("output") or "dataset.jsonl", id="output")
            yield Label("", id="form_error")
            yield Button("Start generating", id="start", variant="primary")
        yield Footer()

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "provider_select" and event.value != "custom":
            self.query_one("#base_url", Input).value = PROVIDER_PRESETS.get(str(event.value), "")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id != "start":
            return
        base_url = self.query_one("#base_url", Input).value.strip()
        api_key = self.query_one("#api_key", Input).value.strip()
        model = self.query_one("#model", Input).value.strip()
        limit_raw = self.query_one("#limit", Input).value.strip()
        output = self.query_one("#output", Input).value.strip()
        provider_name = str(self.query_one("#provider_select", Select).value)

        error_label = self.query_one("#form_error", Label)

        if not base_url or not api_key or not model or not output:
            error_label.update("[red]All fields except limit are required.[/red]")
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
            base_url=base_url, api_key=api_key, model=model,
            limit=limit, output=output, provider_name=provider_name,
        ))


# ------------------------------------------------------------------ #
# Run screen — live table + log while generation happens in a worker
# ------------------------------------------------------------------ #
class RunScreen(Screen):
    BINDINGS = [("q", "quit_run", "Quit")]

    def __init__(self, base_url: str, api_key: str, model: str, limit: int,
                 output: str, provider_name: str):
        super().__init__()
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.limit = limit
        self.output_path = Path(output)
        self.provider_name = provider_name
        self.rows: dict = {}   # index -> dict of current row values, table is fully redrawn from this
        self.done_count = 0
        self.fail_count = 0

    def compose(self) -> ComposeResult:
        yield Header()
        yield ProgressBar(total=self.limit, id="progress")
        yield DataTable(id="table")
        yield RichLog(id="log", wrap=True, markup=True)
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#table", DataTable)
        table.add_columns("#", "App Type", "Style", "Status", "Preview")
        log = self.query_one("#log", RichLog)
        log.write(f"[bold]Provider:[/bold] {self.provider_name}   [bold]Model:[/bold] {self.model}")
        log.write(f"[bold]Output:[/bold] {self.output_path.resolve()}   "
                   f"[bold]Samples:[/bold] {self.limit}")
        log.write("Press 'q' at any time to stop — samples already written stay on disk.\n")
        self.generate_all()

    def action_quit_run(self) -> None:
        self.app.exit()

    def _redraw_table(self) -> None:
        table = self.query_one("#table", DataTable)
        table.clear()
        for idx in sorted(self.rows):
            r = self.rows[idx]
            table.add_row(str(idx), r["app_type"], r["style"], r["status"], r["preview"])

    def _on_sample_update(self, idx: int, sample: Sample) -> None:
        """Called (via call_from_thread) every time a sample's stage changes."""
        preview = (sample.final or sample.draft or "")[:60].replace("\n", " ")
        self.rows[idx] = {
            "app_type": sample.app_type, "style": sample.style,
            "status": sample.status, "preview": preview,
        }
        self._redraw_table()

    def _write_sample(self, sample: Sample) -> None:
        with self.output_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(sample.to_json_dict(), ensure_ascii=False) + "\n")

    @work(thread=True, exclusive=True)
    def generate_all(self) -> None:
        log = self.query_one("#log", RichLog)
        progress = self.query_one("#progress", ProgressBar)

        try:
            client = build_client(self.base_url, self.api_key)
        except Exception as e:
            self.app.call_from_thread(log.write, f"[red]Could not create client: {e}[/red]")
            return

        matrix = build_sample_matrix(self.limit)

        for idx, (app_type, style) in enumerate(matrix, start=1):
            def cb(sample: Sample, idx=idx):
                self.app.call_from_thread(self._on_sample_update, idx, sample)

            try:
                sample = run_pipeline_for_sample(
                    client, self.model, app_type, style, self.provider_name, status_cb=cb
                )
            except FatalProviderError as e:
                self.app.call_from_thread(
                    log.write, f"[red bold]STOPPED — {e}[/red bold]\n"
                               f"Check your API key and re-launch. "
                               f"{idx - 1} sample(s) were saved to {self.output_path}."
                )
                return

            self._write_sample(sample)
            self.app.call_from_thread(progress.advance, 1)

            if sample.status == "done":
                self.done_count += 1
                self.app.call_from_thread(
                    log.write, f"[green]#{idx} done[/green] — {app_type} / {style}"
                )
            else:
                self.fail_count += 1
                self.app.call_from_thread(
                    log.write, f"[yellow]#{idx} failed[/yellow] — {app_type} / {style}: {sample.error}"
                )

        self.app.call_from_thread(
            log.write,
            f"\n[bold]Run finished.[/bold] {self.done_count} done, {self.fail_count} failed. "
            f"Written to {self.output_path.resolve()}. Press 'q' to quit."
        )


# ------------------------------------------------------------------ #
# App shell
# ------------------------------------------------------------------ #
class DatasetGenApp(App):
    CSS = """
    #setup_form { padding: 1 2; }
    #title { text-style: bold; padding-bottom: 1; }
    #form_error { color: red; padding-bottom: 1; }
    #table { height: 1fr; }
    #log { height: 12; border: solid grey; }
    """

    def __init__(self, cli_defaults: dict):
        super().__init__()
        self.cli_defaults = cli_defaults

    def on_mount(self) -> None:
        self.push_screen(SetupScreen(self.cli_defaults))


def parse_args() -> dict:
    parser = argparse.ArgumentParser(
        description="Generate a UI/UX-design dataset via generate->ground->critique->revise."
    )
    parser.add_argument("--limit", type=int, default=None,
                         help="Number of samples to generate (asked in-app if omitted).")
    parser.add_argument("--provider", choices=list(PROVIDER_PRESETS) + ["custom"], default=None,
                         help="Provider preset (base_url pre-filled; still editable in-app).")
    parser.add_argument("--model", type=str, default=None,
                         help="Model name for the chosen provider.")
    parser.add_argument("--output", type=str, default=None,
                         help="Output JSONL path (default: dataset.jsonl).")
    args = parser.parse_args()
    return {"limit": args.limit, "provider": args.provider, "model": args.model, "output": args.output}


if __name__ == "__main__":
    defaults = parse_args()
    DatasetGenApp(defaults).run()
