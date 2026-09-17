import asyncio
from app import DatasetGenApp

async def main():
    app = DatasetGenApp({"limit": None, "provider": None, "model": None, "output": None})
    async with app.run_test(size=(120, 400)) as pilot:
        # Should start on MenuScreen
        assert app.screen.__class__.__name__ == "MenuScreen", app.screen.__class__.__name__
        print("Mounted on MenuScreen OK")

        await pilot.click("#menu_generate")
        await pilot.pause()
        assert app.screen.__class__.__name__ == "SetupScreen", app.screen.__class__.__name__
        print("Navigated to SetupScreen OK")

        # Fill Provider A minimal fields and hit start with an empty form first (should error)
        await pilot.click("#start")
        await pilot.pause()
        err = app.screen.query_one("#form_error").content
        assert "required" in str(err), err
        print("Empty-form validation OK:", err)

        # Fill valid Provider A fields
        app.screen.query_one("#base_url", type(app.screen.query_one("#base_url")))
        base_url = app.screen.query_one("#base_url")
        base_url.value = "https://api.groq.com/openai/v1"
        api_key = app.screen.query_one("#api_key")
        api_key.value = "sk-test"
        model = app.screen.query_one("#model")
        model.value = "llama-3.1-8b-instant"
        limit = app.screen.query_one("#limit")
        limit.value = "3"
        output = app.screen.query_one("#output")
        output.value = "/tmp/smoke_test_dataset.jsonl"
        await pilot.pause()

        await pilot.click("#back")
        await pilot.pause()
        assert app.screen.__class__.__name__ == "MenuScreen", app.screen.__class__.__name__
        print("Back button returns to MenuScreen OK")

        await pilot.click("#menu_merge")
        await pilot.pause()
        assert app.screen.__class__.__name__ == "PrepareScreen", app.screen.__class__.__name__
        print("Navigated to PrepareScreen OK")

        # own_path doesn't exist -> should show an error, not crash
        await pilot.click("#run_merge")
        await pilot.pause()
        err2 = app.screen.query_one("#prep_error").content
        assert "doesn't exist" in str(err2), err2
        print("Missing-dataset validation OK:", err2)

    print("\nUI SMOKE TEST PASSED")

asyncio.run(main())
