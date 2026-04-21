import flet as ft
import os
from typing import Optional
from dataclasses import field

from managers.loader import CONFIG_PATH, CONFIG_ROOT, LOG_FILE, LOG_DIR


# === PRESETS ===
@ft.control
class PrimaryIconButton(ft.IconButton):
    """Literally just an `IconButton` with a default `icon_color`."""
    icon_color: Optional[ft.ColorValue] = ft.Colors.PRIMARY


# === WINDOW CONTROLS ===
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

@ft.control
class MinimizeButton(PrimaryIconButton):
    """Handles the window minimizing functionality."""
    icon: Optional[ft.IconDataOrControl] = ft.Icons.MINIMIZE
    
    def init(self):
        self.on_click = self._on_click
    
    def _on_click(self, e: ft.Event[ft.IconButton]) -> None:
        e.page.window.minimized = True

@ft.control
class FullscreenButton(PrimaryIconButton):
    """Handles the window maximizing functionality."""
    icon: Optional[ft.IconDataOrControl] = ft.Icons.FULLSCREEN
    
    def init(self):
        self.on_click = self._on_click
    
    def did_mount(self):
        self.page.on_resize = lambda _: self.update_icon()
        self.update_icon()
    
    def update_icon(self) -> None:
        self.icon = self.get_icon()
        try: self.update()
        except RuntimeError: pass
    
    def get_icon(self) -> ft.IconData:
        if self.page.window.full_screen:
            return ft.Icons.FULLSCREEN
        return ft.Icons.FULLSCREEN_EXIT
    
    def _on_click(self, e: ft.Event[ft.IconButton]) -> None:
        e.page.window.full_screen = not e.page.window.full_screen

@ft.control
class ThemeToggleButton(ft.AnimatedSwitcher):
    content: ft.Control = field(default_factory=lambda: ft.Container())
    duration: ft.DurationValue = 500
    reverse_duration: ft.DurationValue = 200
    switch_in_curve: ft.AnimationCurve = ft.AnimationCurve.BOUNCE_OUT
    switch_out_curve: ft.AnimationCurve = ft.AnimationCurve.BOUNCE_IN
    transition: ft.AnimatedSwitcherTransition = ft.AnimatedSwitcherTransition.SCALE
    
    def init(self):
        self.content = PrimaryIconButton(ft.Icons.DARK_MODE, on_click=self.swap_theme)
    
    def did_mount(self):
        icon: ft.IconButton = self.content
        icon.icon = (
            ft.Icons.DARK_MODE if
            self.page.theme_mode == ft.ThemeMode.DARK
            else ft.Icons.LIGHT_MODE
        )
        try: icon.update()
        except RuntimeError: pass
    
    def swap_theme(self, e: ft.Event[ft.IconButton]):
        print(f"Clicked: {e}")
        if e.page.theme_mode == ft.ThemeMode.DARK:
            e.page.theme_mode = ft.ThemeMode.LIGHT
            e.control.icon = ft.Icons.LIGHT_MODE
        else:
            e.page.theme_mode = ft.ThemeMode.DARK
            e.control.icon = ft.Icons.DARK_MODE
        e.page.update()

# === SETTINGS ===
@ft.control
class SimplePopupMenuItem(ft.PopupMenuItem):
    text: str = ""
    color: ft.ColorValue = ft.Colors.PRIMARY
    
    def init(self) -> None:
        if self.on_click is None:
            self.on_click = self._on_click
        self.content = ft.Text(self.text, color=self.color)
        
        if not self.icon: return
        if isinstance(self.icon, ft.Icon):
            self.icon.color = self.color
        else:
            self.icon = ft.Icon(self.icon, self.color)
    
    def _on_click(self, e: ft.Event[ft.PopupMenuItem]) -> None:
        e.control.checked = e.data
        e.control.update()

@ft.control
class PresetPopupMenuButton(ft.PopupMenuButton):
    """
    A pre-configured `PopupMenuButton` that has all the buttons that are not toggleable.
    `new_menu_items` can be added, which will be inserted in the middle section of the
    menu. Usually, you will put the toggleable menu items there.
    """
    icon_color: Optional[ft.ColorValue] = ft.Colors.PRIMARY
    new_menu_items: list[ft.PopupMenuItem] = field(default_factory=list)
    
    def init(self):
        self.items = [
            SimplePopupMenuItem(
                text="Edit Config", icon=ft.Icons.FILE_OPEN,
                on_click=lambda _: os.startfile(CONFIG_PATH)
            ),
            SimplePopupMenuItem(
                text="Open Config Directory", icon=ft.Icons.FOLDER_OPEN,
                on_click=lambda _: os.startfile(CONFIG_ROOT)
            ),
            *self.new_menu_items,
            SimplePopupMenuItem(
                text="Open Log File", icon=ft.Icons.FILE_OPEN,
                on_click=lambda _: os.startfile(LOG_FILE),
                color=ft.Colors.SECONDARY
            ),
            SimplePopupMenuItem(
                text="Open Log Directory", icon=ft.Icons.FOLDER_OPEN,
                on_click=lambda _: os.startfile(LOG_DIR),
                color=ft.Colors.SECONDARY
            )
        ]
