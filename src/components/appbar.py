import flet as ft
from typing import Optional
from dataclasses import field

@ft.control
class PresetAppBar(ft.AppBar):
    bgcolor: Optional[ft.ColorValue] = ft.Colors.SURFACE_CONTAINER_HIGHEST
    actions_padding: Optional[ft.PaddingValue] = 4
    title_spacing: Optional[ft.Number] = 4
    leading_width: Optional[ft.Number] = 8
    leading: Optional[ft.Control] = field(default_factory=ft.Container())
    
    def init(self):
        text: str = "Home"
        
        if isinstance(self.title, ft.Text):
            text = self.title.value
        elif isinstance(self.title, str):
            text = self.title
        
        self.title = ft.WindowDragArea(
            content=ft.Text(text, color=ft.Colors.PRIMARY),
            maximizable=False
        )