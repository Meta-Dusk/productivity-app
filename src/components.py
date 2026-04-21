import os
import flet as ft
from typing import Optional
from loader import CONFIG_PATH, CONFIG_ROOT, LOG_FILE, LOG_DIR


# === COMPONENT PRESETS ===
@ft.control
class PrimaryIconButton(ft.IconButton):
    """Literally just an `IconButton` with a default `icon_color`."""
    icon_color: Optional[ft.ColorValue] = ft.Colors.PRIMARY

def simple_popup_menu_item(
    text: str, color: ft.ColorValue, icon: ft.IconData,
    on_click: Optional[ft.ControlEventHandler[ft.PopupMenuItem]] = None,
    checked: Optional[bool] = None
) -> ft.PopupMenuItem:
    """
    A preset popup menu item. Use inside the `items` of a `PopupMenuButton`.
    If `on_click` is `None` and `checked` is either `False` or `True`,
    it will be set to a function that toggles its `checked` state.
    
    Args:
        text (str): The displayed value of the text component.
        color (ColorValue): The color of both the text and the `icon`.
        on_click (ControlEventHandler): The function to be called if the menu item is clicked.
        checked (bool): The `checked` state of the `PopupMenuItem`.
    
    Returns:
        PopupMenuItem: A `PopupMenuItem` with an applied preset.
    """
    def default_on_click(e: ft.ControlEventHandler[ft.PopupMenuItem]):
        """`e` only has `name="click"` and `data: bool`"""
        popup_menu_item.checked = e.data
        popup_menu_item.update()
        
    if checked is not None and on_click is None:
        on_click=default_on_click
    popup_menu_item = ft.PopupMenuItem(
        content=ft.Text(value=text, color=color),
        icon=ft.Icon(icon=icon, color=color),
        on_click=on_click, checked=checked
    )
    return popup_menu_item

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


# === PRE-ASSEMBLED COMPONENTS ===
# | Buttons |
def fullscreen_button(page: ft.Page) -> ft.IconButton:
    """Handles the window maximizing functionality."""
    def update_icon():
        nonlocal btn
        btn.icon = set_icon()
        btn.update()
        
    def set_icon() -> ft.IconData:
        if page.window.full_screen:
            icon = ft.Icons.FULLSCREEN
        else:
            icon = ft.Icons.FULLSCREEN_EXIT
        return icon
    
    def on_click(_):
        page.window.full_screen = not page.window.full_screen
        
    page.on_resize = lambda _: update_icon()
    btn = PrimaryIconButton(set_icon(), on_click=on_click)
    return btn

@ft.control
class WindowMinimizeButton(PrimaryIconButton):
    """Handles the window minimizing functionality."""
    icon: Optional[ft.IconDataOrControl] = ft.Icons.MINIMIZE
    
    def init(self):
        self.on_click = self._on_click
    
    def _on_click(self, e: ft.Event[ft.IconButton]) -> None:
        e.page.window.minimized = True

def theme_button(page: ft.Page) -> ft.AnimatedSwitcher:
    """An animated theme-swapping button."""
    def swap_theme(_):
        icon_btn: ft.IconButton = btn.content
        if page.theme_mode == ft.ThemeMode.DARK:
            page.theme_mode = ft.ThemeMode.LIGHT
            icon_btn.icon = ft.Icons.LIGHT_MODE
        else:
            page.theme_mode = ft.ThemeMode.DARK
            icon_btn.icon = ft.Icons.DARK_MODE
        page.update()
        
    if page.theme_mode == ft.ThemeMode.DARK:
        icon = ft.Icons.DARK_MODE
    else:
        icon = ft.Icons.LIGHT_MODE
        
    btn = ft.AnimatedSwitcher(
        content=ft.IconButton(
            icon=icon, icon_color=ft.Colors.PRIMARY,
            on_click=swap_theme
        ),
        transition=ft.AnimatedSwitcherTransition.SCALE,
        switch_in_curve=ft.AnimationCurve.BOUNCE_OUT,
        switch_out_curve=ft.AnimationCurve.BOUNCE_IN,
        duration=500, reverse_duration=200
    )
    return btn

@ft.control
class ExitButton(PrimaryIconButton):
    """
    A simple exit button. If `on_click` is `None`, then it will be set
    to a function that calls the `close()` method from the `page`'s
    `window`.
    """
    icon: Optional[ft.IconDataOrControl] = ft.Icons.CLOSE
    
    def init(self):
        if self.on_click is None:
            self.on_click = self.close_window
    
    async def close_window(e: ft.Event[ft.IconButton]):
        await e.page.window.close()

def preset_popup_menu_button(new_menu_items: list[ft.PopupMenuItem]) -> ft.PopupMenuButton:
    """
    A pre-configured `PopupMenuButton` that has all the buttons that are not toggleable.
    `new_menu_items` can be added, which will be inserted in the middle section of the
    menu. Usually, you will put the toggleable menu items there.
    
    Args:
        new_menu_items (list): A list of `PopupMenuItem`s.
    
    Returns:
        PopupMenuButton: A pre-configured `PopupMenuButton`.
    """
    return ft.PopupMenuButton(
        items=[
            simple_popup_menu_item(
                text="Edit Config", icon=ft.Icons.FILE_OPEN,
                on_click=lambda _: os.startfile(CONFIG_PATH),
                color=ft.Colors.PRIMARY
            ),
            simple_popup_menu_item(
                text="Open Config Directory", icon=ft.Icons.FOLDER_OPEN,
                on_click=lambda _: os.startfile(CONFIG_ROOT),
                color=ft.Colors.PRIMARY
            ),
            *new_menu_items,
            simple_popup_menu_item(
                text="Open Log File", icon=ft.Icons.FILE_OPEN,
                on_click=lambda _: os.startfile(LOG_FILE),
                color=ft.Colors.SECONDARY
            ),
            simple_popup_menu_item(
                text="Open Log Directory", icon=ft.Icons.FOLDER_OPEN,
                on_click=lambda _: os.startfile(LOG_DIR),
                color=ft.Colors.SECONDARY
            )
        ], icon_color=ft.Colors.PRIMARY
    )

# | App Bar |
def preset_appbar(title: str, actions: list[ft.Control]) -> ft.AppBar:
    """
    An `AppBar` that has its `title` component wrapped in a `WindowDragArea`.
    """
    return ft.AppBar(
        title=ft.WindowDragArea(
            content=ft.Text(value=title, color=ft.Colors.PRIMARY),
            maximizable=False
        ),
        actions=actions,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        actions_padding=4, title_spacing=4,
        # shape=ft.RoundedRectangleBorder(radius=5),
        leading_width=8, leading=ft.Container()
    )
    
# | Loading Screen |
def loading_indicator() -> ft.ProgressRing:
    return ft.ProgressRing(
        color=ft.Colors.PRIMARY,
        stroke_width=4, width=100, height=100
    )

def loading_screen_container(
    loading_text: ft.Text, progress_ring: ft.ProgressRing
) -> ft.WindowDragArea:
    loading_controls = ft.WindowDragArea(
        content=ft.Container(
            content=ft.Column(
                controls=[loading_text, progress_ring],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16, run_alignment=16
            ),
            expand=True, alignment=ft.Alignment.CENTER,
            padding=8
        ),
        maximizable=False, expand=True
    )
    return loading_controls