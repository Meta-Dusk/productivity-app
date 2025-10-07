import flet as ft
from typing import Optional


def simple_notification(
    content: ft.StrOrControl, page: ft.Page,
    bgcolor: Optional[ft.ColorValue] = None,
    duration: int = 1000
):
    snackbar = ft.SnackBar(
        content=content, open=True,
        duration=duration, behavior=ft.SnackBarBehavior.FLOATING,
        on_dismiss=lambda e: page.overlay.remove(e.control),
        bgcolor=bgcolor
    )
    page.overlay.append(snackbar)