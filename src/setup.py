import flet as ft
import asyncio
from typing import Optional


WINDOW_WIDTH: Optional[ft.Number] = 550
WINDOW_HEIGHT: Optional[ft.Number] = 400


def before_main_ui(page: ft.Page):
    """Use for the `before_main` in `run()`."""
    page.title = "Anti-Slacking Monitor"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.decoration = ft.BoxDecoration(border=ft.Border.all(2, ft.Colors.SURFACE_CONTAINER_HIGHEST))
    page.theme_mode = ft.ThemeMode.DARK
    
    page.window.width = WINDOW_WIDTH
    page.window.height = WINDOW_HEIGHT
    page.window.min_width = WINDOW_WIDTH
    page.window.min_height = WINDOW_HEIGHT
    page.window.title_bar_hidden = True
    page.window.prevent_close = False
    page.window.maximized = False
    
    page.on_close = lambda e: print(e)
    page.on_resize = lambda e: print(e)
    page.window.on_event = lambda e: print(e)
    page.update()
    
async def fix_stretched_window(
    page: ft.Page, *,
    center_page: bool = False
):
    """
    When launching a Flet desktop app, sometimes the window appears to be stretched.
    The fix? Just resize it. So, that's exactly what this does.
    """
    page.window.width = WINDOW_WIDTH * 1.1
    page.window.height = WINDOW_HEIGHT * 1.1
    page.window.update()
    await asyncio.sleep(1)
    page.window.width = WINDOW_WIDTH
    page.window.height = WINDOW_HEIGHT
    page.window.update()
    if center_page:
        await page.window.center()