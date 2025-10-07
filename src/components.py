import asyncio, os
import flet as ft
from typing import Optional
from loader import CONFIG_DIR, CONFIG_ROOT, LOG_FILE, LOG_DIR


# === COMPONENT PRESETS ===
def simple_icon_button(
    icon: ft.IconDataOrControl,
    icon_color: ft.ColorValue = ft.Colors.PRIMARY,
    on_click: Optional[ft.ControlEventHandler[ft.IconButton]] = None
) -> ft.IconButton:
    return ft.IconButton(
        icon=icon, icon_color=icon_color, on_click=on_click
    )

def simple_popup_menu_item(
    text: str,
    color: ft.ColorValue,
    icon: ft.IconData,
    on_click: Optional[ft.ControlEventHandler[ft.PopupMenuItem]] = None,
    checked: Optional[bool] = None
) -> ft.PopupMenuItem:
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


# === PRE-ASSEMBLED COMPONENTS ===
# | Buttons |
def fullscreen_button(page: ft.Page) -> ft.IconButton:
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
    btn = simple_icon_button(
        icon=set_icon(), on_click=on_click
    )
    return btn

def minimize_button(page: ft.Page) -> ft.IconButton:
    def on_click(_):
        page.window.minimized = True
    return simple_icon_button(
        icon=ft.Icons.MINIMIZE, on_click=on_click
    )

def theme_button(page: ft.Page) -> ft.AnimatedSwitcher:
    def swap_theme(_):
        icon_btn: ft.IconButton = btn.content
        if page.theme_mode == ft.ThemeMode.DARK:
            page.theme_mode = ft.ThemeMode.LIGHT
            icon_btn.icon = ft.Icons.LIGHT_MODE
        else:
            page.theme_mode = ft.ThemeMode.DARK
            icon_btn.icon = ft.Icons.DARK_MODE
        icon_btn.update()
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

def exit_button(
    page: ft.Page,
    on_click: Optional[ft.ControlEventHandler[ft.IconButton]] = None
) -> ft.IconButton:
    if on_click is None:
        on_click = lambda _: asyncio.create_task(
            coro=page.window.close(),
            name="Exit Button -> Closing Window"
        )
    return simple_icon_button(
        icon=ft.Icons.CLOSE,
        on_click=on_click
    )

def preset_popup_menu_button(new_menu_items: list[ft.PopupMenuItem]) -> ft.PopupMenuButton:
    return ft.PopupMenuButton(
        items=[
            simple_popup_menu_item(
                text="Edit Config", icon=ft.Icons.FILE_OPEN,
                on_click=lambda _: os.startfile(CONFIG_DIR),
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
    return ft.AppBar(
        title=ft.WindowDragArea(
            content=ft.Text(value=title, color=ft.Colors.PRIMARY),
            maximizable=False
        ),
        actions=actions,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        actions_padding=4, title_spacing=4,
        shape=ft.RoundedRectangleBorder(radius=5),
        leading_width=8, leading=ft.Container()
    )