import flet as ft
from typing import Optional
from dataclasses import field

from components.layouts import CenteredColumn

@ft.control
class LoadingIndicator(ft.ProgressRing):
    color: Optional[ft.ColorValue] = ft.Colors.PRIMARY
    stroke_width: Optional[ft.Number] = 4
    width: Optional[ft.Number] = 100
    height: Optional[ft.Number] = 100

@ft.control
class LoadingScreen(ft.WindowDragArea):
    content: ft.Control = field(default_factory=lambda: ft.Container())
    loading_text: ft.Text = field(default_factory=lambda: ft.Text("Loading..."))
    loading_indicator: ft.ProgressRing = field(default_factory=lambda: LoadingIndicator())
    
    def init(self):
        self.content = ft.Container(
            CenteredColumn(
                controls=[self.loading_text, self.loading_indicator],
                spacing=16, run_alignment=16
            ),
            expand=True, alignment=ft.Alignment.CENTER, padding=8
        )
        self.maximizable = False
        self.expand = True