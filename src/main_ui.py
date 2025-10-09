import flet as ft
import asyncio
from loader import load_app_lists, ensure_config_exists, reset_config
from window import get_process_name, check_helper_dir, test_window_helper, WindowHelperManager
from data_types import WindowInfo, AppType
from utilities import safe_sleep, format_time
from components import (exit_button, theme_button, minimize_button, preset_popup_menu_button,
                        preset_appbar, simple_popup_menu_item, fullscreen_button,
                        loading_indicator, loading_screen_container)
from notifications import simple_notification
from smart_classifier import SmartClassifier


# === MAIN FLET APP ===
async def main_ui(page: ft.Page):
    """The main UI/UX of the app."""
    # | Initial Setup |
    title = "Anti-Slacking Monitor"
    loading_interval: float = 0.5
    await page.window.center()
    loading_text = ft.Text(
        value="Loading App Config...", size=16,
        text_align=ft.TextAlign.CENTER,
        color=ft.Colors.SECONDARY
    )
    progress_ring = loading_indicator()
    loading_controls = loading_screen_container(loading_text, progress_ring)
    page.add(loading_controls)
    page.appbar = preset_appbar(
        title=title, actions=[
            exit_button(page)
        ]
    )
    
    # Check important files
    try:
        ensure_config_exists()
        simple_notification("Loaded config files.", page)
    except Exception as e:
        error_msg = "Error ensuring config files!"
        print(f"[ERROR] {error_msg} {e}")
        simple_notification(
            content=ft.Text(error_msg, color=ft.Colors.ERROR),
            page=page, duration=2000, bgcolor=ft.Colors.ERROR_CONTAINER
        )
        
    await asyncio.sleep(loading_interval)
    loading_text.value = "Checking Window Helper Directory..."
    loading_text.update()
    
    # Check window helper availability
    try:
        if check_helper_dir():
            await asyncio.sleep(loading_interval)
            loading_text.value = "Loading Window Helper..."
            loading_text.update()
            # # This function still doesn't work properly, so I'll just comment it out for now.
            # if test_window_helper():
            #     simple_notification("Loaded `window_helper` executable.", page)
        else:
            error_msg = "Missing `window_helper` executable!"
            simple_notification(
                content=ft.Text(error_msg, color=ft.Colors.ERROR),
                page=page, duration=2000, bgcolor=ft.Colors.ERROR_CONTAINER
            )
    except Exception as e:
        error_msg = "Error testing `test_window_helper()`! Copied error to clipboard."
        await page.clipboard.set(e)
        print(f"[ERROR] {error_msg} {e}")
        simple_notification(
            content=ft.Text(error_msg, color=ft.Colors.ERROR),
            page=page, duration=4000, bgcolor=ft.Colors.ERROR_CONTAINER
        )
    await asyncio.sleep(loading_interval)
    loading_text.value = "Finished! Starting App."
    loading_text.color = ft.Colors.PRIMARY
    progress_ring.visible = False
    page.update()
    await asyncio.sleep(1)
    page.controls.clear()
    page.window.prevent_close = True
    
    
    # Variables
    window_names = load_app_lists()
    stop_event = asyncio.Event()
    classifier = SmartClassifier(window_names)
    window_manager = WindowHelperManager()
    window_manager.start()
    distraction_time: int = 0
    productive_time: int = 0
    
    
    # | Event Handlers |
    async def on_close(_):
        """
        Handles window closing + animations.
        """
        print("App is closing... Waiting for monitor to stop.")
        if not stop_event.is_set():
            stop_event.set()
        form.opacity = 0
        form.offset = ft.Offset(0, -1)
        form.update()
        await asyncio.sleep(1)
        page.window.prevent_close = False
        page.window.update()
        await page.window.close()
    
    async def on_event(e: ft.WindowEvent):
        match e.type:
            case ft.WindowEventType.CLOSE:
                await on_close(e)
            case _:
                pass
    
    def reset_config_btn_call(_):
        """
        Resets the config to its default values once called.
        """
        if reset_config():
            simple_notification(
                content=ft.Text("Successful reset of config file."),
                page=page, duration=1500
            )
        else:
            simple_notification(
                content=ft.Text(
                    value="Failed to reset config file!",
                    color=ft.Colors.ERROR
                ),
                page=page, duration=1500,
                bgcolor=ft.Colors.ERROR_CONTAINER
            )
    
    
    # | Events |
    async def match_app_type(app_type: AppType):
        """
        Event handler for detected window type from monitor task.
        """
        nonlocal distraction_time, productive_time
        match app_type:
            case AppType.PRODUCTIVE:
                productive_time += 1
                productive_counter_text.spans[1].text = format_time(productive_time)
                productive_counter_text.update()
                print(f"Incremented productive_time to: {format_time(productive_time)}")
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
                print(f"Incremented distraction_time to: {format_time(distraction_time)}")
                await safe_sleep(1, stop_event)
                
            case AppType.NEUTRAL | _:
                if page.window.always_on_top:
                    page.window.always_on_top = False
                    page.window.update()
                await safe_sleep(0.5, stop_event)
    
    async def monitor_focus_async():
        """
        This is the main looping function for window detection and classification.
        """
        nonlocal distraction_time
        prev_title = ""
        while not stop_event.is_set():
            # Run blocking call in a background thread with COM initialized
            info = await asyncio.to_thread(window_manager.get_latest_window_info)
            category = classifier.classify(win_info=info, process_getter=get_process_name)
            title = info.get(WindowInfo.NAME) or "Unknown Window"
            if title != prev_title:
                prev_title = title
                current_app_column: ft.Column = current_app.controls
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
        print("Monitor task stopped.")
    
    
    # | Controls |
    theme_btn = theme_button(page)
    close_btn = exit_button(page, on_close)
    minimize_btn = minimize_button(page)
    fullscreen_btn = fullscreen_button(page)
    
    popup_menu_item_fid = simple_popup_menu_item(
        text="Fullscreen if Distracted", color=ft.Colors.TERTIARY,
        icon=ft.Icons.FULLSCREEN, checked=False
    )
    popup_menu_item_csid = simple_popup_menu_item(
        text="Center Screen if Distracted", color=ft.Colors.TERTIARY,
        icon=ft.Icons.CENTER_FOCUS_STRONG, checked=True
    )
    popup_menu_item_btfid = simple_popup_menu_item(
        text="Bring to Front if Distracted", color=ft.Colors.TERTIARY,
        icon=ft.Icons.FLIP_TO_FRONT, checked=True
    )
    popup_menu_btn = preset_popup_menu_button([
        simple_popup_menu_item(
            text="Reset Config Contents", icon=ft.Icons.FILE_OPEN_OUTLINED,
            on_click=reset_config_btn_call,
            color=ft.Colors.PRIMARY
        ),
        popup_menu_item_fid, popup_menu_item_csid, popup_menu_item_btfid
    ])
    appbar = preset_appbar(
        title = title,
        actions=[
            theme_btn, popup_menu_btn,
            ft.Container(padding=8),
            minimize_btn, fullscreen_btn, close_btn
        ]
    )
    
    current_app = ft.Column(
        controls=[ft.Text("Detecting active window...", size=16, weight=ft.FontWeight.BOLD, data="editable_text")],
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
    controls = [
        distractions_counter_text,
        productive_counter_text,
        ft.Divider(height=16),
        ft.Text("Current Window:", size=16),
        current_app,
        ft.Divider(height=16),
        ft.Text("Status:", size=16),
        category_text,
    ]
    column = ft.Column(
        controls=controls,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=4
    )
    container = ft.Container(
        content=column,
        padding=16, border_radius=16, expand=True,
        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.SURFACE_CONTAINER),
        alignment=ft.Alignment.CENTER,
    )
    form = ft.WindowDragArea(
        content=container, maximizable=False, expand=True,
        opacity=0, offset=ft.Offset(0, -1),
        animate_opacity=ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT),
        animate_offset=ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT)
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
