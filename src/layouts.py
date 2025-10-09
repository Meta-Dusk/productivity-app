import flet as ft


def preset_column(controls: list[ft.Control]) -> ft.Column:
    """A simple column with preset parameters."""
    return ft.Column(
        controls=controls, spacing=4,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
    
def preset_win_drag_area(content: ft.Control) -> ft.WindowDragArea:
    """The main window drag area that the main UI uses."""
    return ft.WindowDragArea(
        content=content, maximizable=False, expand=True,
        opacity=0, offset=ft.Offset(0, -1),
        animate_opacity=ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT),
        animate_offset=ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT)
    )