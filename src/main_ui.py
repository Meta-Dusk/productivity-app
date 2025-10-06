import flet as ft
import asyncio, os

from loader import load_app_lists, CONFIG_FILE, CONFIG_ROOT, ensure_config_exists, _LOG_FILE
from window import get_active_window_info, classify_window
from data_types import WindowInfo, AppType
from utilities import safe_sleep, format_time


# === MAIN FLET APP ===
async def main_ui(page: ft.Page):
    # Initial Setup
    title = "Anti-Slacking Monitor"
    try:
        ensure_config_exists()
    except Exception:
        print("Error ensuring config files")
        title = "ERROR: Config Not Ensured"
        pass
    productive_apps, distracting_keywords = load_app_lists()
    REFRESH_RATE = 0.2
    distraction_time = 0
    stop_event = asyncio.Event()
    
    await page.window.center()
    
    # Event Handlers
    async def on_close(_):
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
    
    def swap_theme(_):
        icon_btn: ft.IconButton = theme_btn.content
        if page.theme_mode == ft.ThemeMode.DARK:
            page.theme_mode = ft.ThemeMode.LIGHT
            icon_btn.icon = ft.Icons.LIGHT_MODE
        else:
            page.theme_mode = ft.ThemeMode.DARK
            icon_btn.icon = ft.Icons.DARK_MODE
        icon_btn.update()
    
    def minimize(_):
        page.window.minimized = True
    
    async def on_event(e: ft.WindowEvent):
        if e.type == ft.WindowEventType.CLOSE:
            await on_close(e)
    
    # Events
    async def monitor_focus_async():
        nonlocal distraction_time
        prev_title = ""
        
        while not stop_event.is_set():
            # Run blocking call in a background thread with COM initialized
            info = await asyncio.to_thread(get_active_window_info)
            category = classify_window(info, productive_apps, distracting_keywords)
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
            
            if category != AppType.DISTRACTING:
                await safe_sleep(REFRESH_RATE, stop_event)
                if page.window.always_on_top:
                    page.window.always_on_top = False
                    page.window.update()
            else:
                if not page.window.always_on_top:
                    page.window.always_on_top = True
                    page.window.update()
                    await page.window.center()
                distraction_time += 1
                distractions_counter_text.spans[1].text = format_time(distraction_time)
                distractions_counter_text.update()
                print(f"Incremented distraction_time to: {format_time(distraction_time)}")
                await safe_sleep(1, stop_event)
        print("Monitor task stopped.")
    
    # Controls
    theme_btn = ft.AnimatedSwitcher(
        content=ft.IconButton(
            icon=ft.Icons.DARK_MODE, on_click=swap_theme,
            icon_color=ft.Colors.PRIMARY
        ),
        transition=ft.AnimatedSwitcherTransition.ROTATION,
        duration=500, reverse_duration=100
    )
    close_btn = ft.IconButton(
        icon=ft.Icons.CLOSE, icon_color=ft.Colors.PRIMARY,
        on_click=on_close
    )
    minimize_btn = ft.IconButton(
        icon=ft.Icons.MINIMIZE, icon_color=ft.Colors.PRIMARY,
        on_click=minimize
    )
    # TODO: Add buttons for opening log file and directory + Make some factory functions
    popup_menu_btn = ft.PopupMenuButton(
        items=[
            ft.PopupMenuItem(
                content="Edit Config", icon=ft.Icon(ft.Icons.FILE_OPEN, ft.Colors.PRIMARY),
                on_click=lambda _: os.startfile(CONFIG_FILE)
            ),
            ft.PopupMenuItem(
                content="Open Config Directory", icon=ft.Icon(ft.Icons.FOLDER_OPEN, ft.Colors.PRIMARY),
                on_click=lambda _: os.startfile(CONFIG_ROOT)
            ),
            ft.PopupMenuItem(
                content="Open Log", icon=ft.Icon(ft.Icons.FILE_OPEN, ft.Colors.SECONDARY),
                on_click=lambda _: os.startfile(_LOG_FILE)
            )
            # <- Insert "Open Log Directory" button
        ], icon_color=ft.Colors.PRIMARY
    )
    appbar = ft.AppBar(
        title = title,
        actions=[
            theme_btn, popup_menu_btn,
            ft.Container(padding=8),
            minimize_btn, close_btn
        ]
    )
    
    current_app = ft.Column(
        controls=[ft.Text("Detecting active window...", size=18, weight=ft.FontWeight.BOLD, data="editable_text")],
        scroll=ft.ScrollMode.ALWAYS, expand=True
    )
    category_text = ft.Text("Unknown", size=28, weight=ft.FontWeight.BOLD)
    distractions_counter_text = ft.Text(
        spans=[
            ft.TextSpan("You Were Distracted for: "),
            ft.TextSpan(format_time(distraction_time))
        ],
        size=18, color=ft.Colors.ERROR
    )
    
    controls = [
        distractions_counter_text,
        ft.Divider(height=20),
        ft.Text("Current Window:", size=14),
        current_app,
        ft.Divider(height=20),
        ft.Text("Status:", size=14),
        category_text,
    ]
    column = ft.Column(
        controls=controls,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=5
    )
    container = ft.Container(
        content=column,
        padding=20, border_radius=16, expand=True,
        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.SURFACE_CONTAINER),
        alignment=ft.Alignment.CENTER,
    )
    form = ft.WindowDragArea(
        content=container, maximizable=False, expand=True,
        opacity=0, offset=ft.Offset(0, -1),
        animate_opacity=ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT),
        animate_offset=ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT)
    )
    
    page.add(form)
    page.appbar = appbar
    page.run_task(monitor_focus_async)
    page.on_close = on_close
    page.window.on_event = on_event
    await asyncio.sleep(0.1)
    form.opacity = 1
    form.offset = ft.Offset(0, 0)
    page.update()
