import flet as ft
from typing import Optional
from dataclasses import field

@ft.control
class LoadingIndicator(ft.ProgressRing):
    color: Optional[ft.ColorValue] = ft.Colors.PRIMARY
    stroke_width: Optional[ft.Number] = 4
    width: Optional[ft.Number] = 100
    height: Optional[ft.Number] = 100

@ft.control
class LoadingScreen(ft.WindowDragArea):
    maximizable: bool = False
    expand: Optional[bool | int] = True
    loading_text: ft.Text = field(default_factory=ft.Text("Loading..."))
    
    def init(self):
        self.content = ft.Container(
            ft.Column(
                controls=[self.loading_text, LoadingIndicator()],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16, run_alignment=16
            ),
            expand=True, alignment=ft.Alignment.CENTER,
            padding=8
        )