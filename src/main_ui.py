import flet as ft
import asyncio

from managers.loader import load_app_lists, reset_config, log
from managers.window import WindowHelperManager
from core.utilities import safe_sleep, format_time
from core.data_types import WindowInfo, AppType
from components.layouts import PresetColumn, PresetWindowDragArea
from components.appbar import PresetAppBar
from components.buttons import (
    ExitButton, MinimizeButton, PresetPopupMenuButton, SimplePopupMenuItem,
    FullscreenButton, ThemeToggleButton)
from components.text import DefaultText
from components.loading_screen import LoadingIndicator, LoadingScreen
from components.notifications import SimpleNotification, ErrorNotification
from managers.error_checking import check_app_integrity
from managers.smart_classifier import SmartClassifier


# === MAIN FLET APP ===
async def main_ui(page: ft.Page):
    """The main UI/UX of the app."""
    # | Initial Setup |
    title = "Anti-Slacking Monitor"
    window_names = load_app_lists()
    stop_event = asyncio.Event()
    distraction_time: int = 0
    productive_time: int = 0
    loading_interval: float = 0.5
    app_exiting: bool = False
    
    # Loading Controls
    loading_text = DefaultText("Setting Up App...")
    progress_ring = LoadingIndicator()
    loading_controls = LoadingScreen(loading_text=loading_text, loading_indicator=progress_ring)
    page.add(loading_controls)
    page.appbar = PresetAppBar(title=title, actions=[ExitButton()])
    
    await page.window.center()
    
    # Class Setups
    classifier = SmartClassifier(window_names)
    window_manager = WindowHelperManager()
    
    # Check important files
    await check_app_integrity(page, loading_text, window_manager, progress_ring, loading_interval)
    
    
    # | Event Handlers |
    async def on_close(_):
        """Handles window closing + animations."""
        nonlocal app_exiting
        if app_exiting:
            log("App closed.")
            return
        app_exiting = True
        log("App is closing... Waiting for monitor to stop.")
        page.show_dialog(SimpleNotification("Exiting the application..."))
        if not stop_event.is_set(): stop_event.set()
        window_manager.stop()
        form.opacity = 0
        form.offset = ft.Offset(0, -1)
        form.update()
        await asyncio.sleep(1)
        page.window.prevent_close = False
        page.window.update()
        await page.window.close()
    
    async def on_event(e: ft.WindowEvent):
        match e.type:
            case ft.WindowEventType.CLOSE: await on_close(e)
            case _: pass
    
    def reset_config_btn_call(_):
        """Resets the config to its default values once called."""
        if reset_config():
            notif = SimpleNotification("Successful reset of config file.", duration=1500)
        else:
            notif = ErrorNotification(text="Failed to reset config file!", duration=1500)
        page.show_dialog(notif)
    
    
    # | Events |
    async def match_app_type(app_type: AppType):
        """Event handler for detected window type from monitor task."""
        nonlocal distraction_time, productive_time
        match app_type:
            case AppType.PRODUCTIVE:
                productive_time += 1
                productive_counter_text.spans[1].text = format_time(productive_time)
                productive_counter_text.update()
                log(f"Incremented productive_time to: {format_time(productive_time)}")
                await safe_sleep(1, stop_event)
            
            case AppType.DISTRACTING:
                if popup_menu_item_csid.checked:
                    await page.window.center()
                if not page.window.always_on_top and popup_menu_item_btfid.checked:
                    page.window.always_on_top = True
                    page.window.update()
                if not page.window.maximized and popup_menu_item_fid.checked:
                    page.window.maximized = True
                    page.window.update()
                distraction_time += 1
                distractions_counter_text.spans[1].text = format_time(distraction_time)
                distractions_counter_text.update()
                log(f"Incremented distraction_time to: {format_time(distraction_time)}")
                await safe_sleep(1, stop_event)
                
            case AppType.NEUTRAL | _:
                if page.window.always_on_top:
                    page.window.always_on_top = False
                    page.window.update()
                await safe_sleep(0.5, stop_event)
    
    async def monitor_focus_async():
        """This is the main looping function for window detection and classification."""
        nonlocal distraction_time
        prev_title = ""
        while not stop_event.is_set():
            # Run blocking call in a background thread with COM initialized
            info = await asyncio.to_thread(window_manager.get_latest_window_info)
            category = classifier.classify(info)
            title = info.get(WindowInfo.NAME) or "Unknown Window"
            if title != prev_title:
                prev_title = title
                current_app_column: ft.Column = current_app_col.controls
                for ctrl in current_app_column:
                    if isinstance(ctrl, ft.Text) and ctrl.data == "editable_text":
                        current_app_text: ft.Text = ctrl
                        current_app_text.value = title
                category_text.value = category.value.title()
                category_text.color = (
                    ft.Colors.PRIMARY if category == AppType.PRODUCTIVE
                    else ft.Colors.ERROR if category == AppType.DISTRACTING
                    else ft.Colors.SECONDARY
                )
                page.update()
            await match_app_type(category)
        log("Monitor task stopped.")
    
    
    # | Controls |
    popup_menu_item_fid = SimplePopupMenuItem(
        text="Fullscreen if Distracted", color=ft.Colors.TERTIARY,
        icon=ft.Icons.FULLSCREEN, checked=False
    )
    popup_menu_item_csid = SimplePopupMenuItem(
        text="Center Screen if Distracted", color=ft.Colors.TERTIARY,
        icon=ft.Icons.CENTER_FOCUS_STRONG, checked=True
    )
    popup_menu_item_btfid = SimplePopupMenuItem(
        text="Bring to Front if Distracted", color=ft.Colors.TERTIARY,
        icon=ft.Icons.FLIP_TO_FRONT, checked=True
    )
    popup_menu_btn = PresetPopupMenuButton(
        new_menu_items=[
            SimplePopupMenuItem(
                text="Reset Config Contents", icon=ft.Icons.FILE_OPEN_OUTLINED,
                on_click=reset_config_btn_call,
            ),
            popup_menu_item_fid, popup_menu_item_csid, popup_menu_item_btfid
        ]
    )
    appbar = PresetAppBar(
        title = title,
        actions=[
            ThemeToggleButton(), popup_menu_btn,
            ft.Container(padding=8),
            MinimizeButton(), FullscreenButton(), ExitButton(on_click=on_close)
        ]
    )
    
    current_app_col = ft.Column(
        controls=[
            ft.Text(
                "Detecting active window...", size=16,
                weight=ft.FontWeight.BOLD, data="editable_text"
            )
        ],
        scroll=ft.ScrollMode.ALWAYS, expand=True
    )
    category_text = ft.Text("Unknown", size=24, weight=ft.FontWeight.BOLD)
    distractions_counter_text = ft.Text(
        spans=[
            ft.TextSpan("You Were Distracted for: "),
            ft.TextSpan(format_time(distraction_time))
        ],
        size=16, color=ft.Colors.ERROR
    )
    productive_counter_text = ft.Text(
        spans=[
            ft.TextSpan("You Were Productive for: "),
            ft.TextSpan(format_time(productive_time))
        ],
        size=16, color=ft.Colors.PRIMARY
    )
    
    
    # | Layouts |
    form_controls = [
        distractions_counter_text,
        productive_counter_text,
        ft.Divider(height=16),
        ft.Text("Current Window:", size=16),
        current_app_col,
        ft.Divider(height=16),
        ft.Text("Status:", size=16),
        category_text,
    ]
    form = PresetWindowDragArea(
        ft.Container(
            content=PresetColumn(form_controls),
            padding=16, border_radius=16, expand=True,
            bgcolor=ft.Colors.SURFACE_CONTAINER,
            alignment=ft.Alignment.CENTER,
        )
    )
    
    
    # | Page Stuff + Animation |
    page.add(form)
    page.appbar = appbar
    page.run_task(monitor_focus_async)
    page.on_close = on_close
    page.window.on_event = on_event
    await asyncio.sleep(0.1)
    form.opacity = 1
    form.offset = ft.Offset(0, 0)
    page.update()
