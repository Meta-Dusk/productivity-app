import flet as ft
from typing import Optional


def simple_notification(
    page: ft.Page,
    content: ft.StrOrControl,
    duration: int = 1000,
    bgcolor: Optional[ft.ColorValue] = None,
) -> None:
    """
    Shows a `snackbar` by appending it to the `overlay`, then
    automatically removes itself after dismissal.
    """
    snackbar = ft.SnackBar(
        content=content, open=True,
        duration=duration, behavior=ft.SnackBarBehavior.FLOATING,
        on_dismiss=lambda e: page.overlay.remove(e.control),
        bgcolor=bgcolor
    )
    page.overlay.append(snackbar)

def error_notif(
    page: ft.Page,
    text: str = "ERROR",
    duration: int = 2000
) -> None:
    """A preset notification for showing errors."""
    simple_notification(
        content=ft.Text(text, color=ft.Colors.ERROR),
        page=page, duration=duration,
        bgcolor=ft.Colors.ERROR_CONTAINER
    )