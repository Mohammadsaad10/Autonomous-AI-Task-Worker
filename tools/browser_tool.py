"""
Browser Tool - Web browser automation using Playwright.
"""
from __future__ import annotations

from typing import Optional, Dict, Any
from .base import BaseTool, ToolResult


class BrowserTool(BaseTool):
    name = "browser"
    description = (
        "Interact with web pages using a browser. Can navigate to URLs, "
        "read page content, click elements, fill forms, and take screenshots. "
        "Use this for any task that requires interacting with a website."
    )
    parameters_schema = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "Browser action to perform",
                "enum": [
                    "navigate",
                    "read_page",
                    "click",
                    "fill_form",
                    "screenshot",
                    "get_text",
                    "find_element",
                ],
            },
            "url": {
                "type": "string",
                "description": "URL to navigate to (required for navigate action)",
            },
            "selector": {
                "type": "string",
                "description": "CSS selector for elements (required for click, get_text, find_element)",
            },
            "form_data": {
                "type": "object",
                "description": "Dictionary of {selector: value} to fill a form (required for fill_form action)",
            },
            "file_path": {
                "type": "string",
                "description": "Path to save screenshot (optional, default: screenshot.png)",
            },
        },
        "required": ["action"],
    }

    def __init__(self, headless: bool = False, slow_mo: int = 500):
        self._headless = headless
        self._slow_mo = slow_mo
        self._playwright = None
        self._browser = None
        self._page = None

    async def initialize(self):
        """Launch the browser if not already running."""
        if self._page is not None:
            return

        from playwright.async_api import async_playwright

        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=self._headless,
            slow_mo=self._slow_mo,
        )
        context = await self._browser.new_context(
            viewport={"width": 1280, "height": 800}
        )
        self._page = await context.new_page()

    async def cleanup(self):
        """Close the browser."""
        if self._browser:
            await self._browser.close()
            self._browser = None
            self._page = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None

    async def execute(self, action: str, **kwargs) -> ToolResult:
        try:
            await self.initialize()
            if not self._page:
                return ToolResult(
                    success=False, output="", error="Browser initialization failed"
                )

            if action == "navigate":
                url = kwargs.get("url")
                if not url:
                    return ToolResult(
                        success=False, output="", error="url is required for navigate"
                    )
                await self._page.goto(url, wait_until="domcontentloaded", timeout=15000)
                title = await self._page.title()
                return ToolResult(
                    success=True,
                    output=f"Navigated to {url}. Page title: {title}",
                )

            elif action == "read_page":
                text = await self._page.evaluate("document.body.innerText")
                # Truncate very long pages
                if len(text) > 3000:
                    text = text[:3000] + "\n... [truncated]"
                return ToolResult(success=True, output=text)

            elif action == "click":
                selector = kwargs.get("selector")
                if not selector:
                    return ToolResult(
                        success=False,
                        output="",
                        error="selector is required for click",
                    )
                await self._page.click(selector, timeout=5000)
                return ToolResult(success=True, output=f"Clicked on '{selector}'")

            elif action == "fill_form":
                form_data = kwargs.get("form_data", {})
                if not form_data:
                    return ToolResult(
                        success=False,
                        output="",
                        error="form_data is required for fill_form",
                    )
                filled = []
                for selector, value in form_data.items():
                    await self._page.fill(selector, str(value))
                    filled.append(f"{selector}={value}")
                return ToolResult(
                    success=True,
                    output=f"Filled form fields: {', '.join(filled)}",
                )

            elif action == "screenshot":
                file_path = kwargs.get("file_path", "screenshot.png")
                await self._page.screenshot(path=file_path, full_page=True)
                return ToolResult(
                    success=True, output=f"Screenshot saved to {file_path}"
                )

            elif action == "get_text":
                selector = kwargs.get("selector")
                if not selector:
                    return ToolResult(
                        success=False,
                        output="",
                        error="selector is required for get_text",
                    )
                text = await self._page.inner_text(selector)
                return ToolResult(success=True, output=text)

            elif action == "find_element":
                selector = kwargs.get("selector")
                if not selector:
                    return ToolResult(
                        success=False,
                        output="",
                        error="selector is required for find_element",
                    )
                elements = await self._page.query_selector_all(selector)
                texts = []
                for el in elements[:10]:  # Limit to 10 elements
                    text = await el.inner_text()
                    texts.append(text.strip())
                return ToolResult(
                    success=True,
                    output=f"Found {len(elements)} elements. Text: {texts}",
                )

            else:
                return ToolResult(
                    success=False, output="", error=f"Unknown action: {action}"
                )

        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))
