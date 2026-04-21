import flet as ft
from typing import Optional

@ft.control
class SimpleNotification(ft.SnackBar):
    duration: ft.DurationValue = 1000
    behavior: Optional[ft.SnackBarBehavior] = ft.SnackBarBehavior.FLOATING

@ft.control
class ErrorNotification(ft.SnackBar):
    text: str = "ERROR"
    duration: ft.DurationValue = 2000
    bgcolor: Optional[ft.ColorValue] = ft.Colors.ERROR_CONTAINER
    
    def init(self):
        self.content = ft.Text(self.text, color=ft.Colors.ERROR)
