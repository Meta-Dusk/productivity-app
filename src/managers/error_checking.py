import flet as ft
import asyncio
from typing import Callable

from components.text import DefaultText
from managers.loader import ensure_config_exists
from managers.window import WindowHelperManager

def error_check(
    msg: str,
    text_component: DefaultText,
    callable: Callable[[], bool]
) -> Exception | None:
    """Wraps a function in a try/except catch. Use with loading screens."""
    text_component.set_text(msg)
    try:
        if callable():
            text_component.set_text(f"{msg} OK")
        else:
            text_component.set_text(f"{msg} FAIL")
        return None
    except Exception as e:
        print(f"[ERROR] {e}")
        return e

async def error_check_delayed(
    msg: str,
    text_component: DefaultText,
    callable: Callable[[], bool],
    delay: float = 1
) -> Exception | None:
    await asyncio.sleep(delay)
    return error_check(msg, text_component, callable)

async def check_app_integrity(
    page: ft.Page,
    loading_text: DefaultText,
    window_manager: WindowHelperManager,
    progress_ring: ft.ProgressRing,
    loading_interval: float = 0.5
) -> None:
    """
    Handles the loading screen controls manipulation for showing the status of the
    error checkings for the entire app.
    """
    await error_check_delayed(
        msg="Loading App Config...", text_component=loading_text,
        callable=ensure_config_exists, delay=loading_interval
    )
    await error_check_delayed(
        msg="Starting WindowManager...", text_component=loading_text,
        callable=window_manager.start, delay=loading_interval
    )
    await error_check_delayed(
        msg="Checking Path of WindowManager...", text_component=loading_text,
        callable=window_manager.check_path, delay=loading_interval
    )
    loading_text.emphasize("Finished! Starting App.")
    progress_ring.visible = False
    progress_ring.update()
    await asyncio.sleep(loading_interval * 2)
    page.controls.clear()
    page.window.prevent_close = True # Re-enable since the app has an exit animation


def test(page: ft.Page):
    def test_function() -> bool:
        return True
    test_text = DefaultText("Testing")
    page.add(test_text)
    err_check = error_check(
        msg="Testing error_check()", text_component=test_text,
        callable=test_function
    )
    print(err_check)
    
if __name__ == "__main__":
    ft.run(test)