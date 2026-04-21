import flet as ft
from typing import Optional

@ft.control
class DefaultText(ft.Text):
    """Default text usually used for loading screens."""
    size: Optional[ft.Number] = 16
    text_align: ft.TextAlign = ft.TextAlign.CENTER
    color: Optional[ft.ColorValue] = ft.Colors.SECONDARY

    def set_text(self, value: str) -> None:
        self.value = value
        try: self.update()
        except RuntimeError: pass
    
    def emphasize(
        self, new_value: Optional[str], *,
        new_size: Optional[int] = 24,
        new_weight: Optional[ft.FontWeight] = ft.FontWeight.BOLD,
        new_color: Optional[ft.ColorValue] = ft.Colors.PRIMARY
    ) -> None:
        self.value = new_value
        self.size = new_size
        self.weight = new_weight
        self.color = new_color
        try: self.update()
        except RuntimeError: pass