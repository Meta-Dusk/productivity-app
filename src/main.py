import flet as ft
import psutil, asyncio
import uiautomation as auto

from enum import Enum
from typing import Optional

# === CONFIG ===
PRODUCTIVE_APPS = [
    "code.exe", "pycharm64.exe", "anki.exe", "obsidian.exe",
    "notepad.exe", "pdfreader.exe", "mspowerpoint.exe"
]
DISTRACTING_KEYWORDS = [
    "youtube", "facebook", "reddit", "twitter", "tiktok", "discord", "netflix"
]


# === TYPE CLASSES ===
class AppType(Enum):
    DISTRACTING = "distracting"
    NEUTRAL = "neutral"
    PRODUCTIVE = "productive"

class WindowInfo(Enum):
    NAME = "name"
    CLASS_NAME = "class_name"
    PROCESS_ID = "process_id"


# === BACKGROUND MONITOR FUNCTION ===
def get_active_window_info() -> dict[WindowInfo, Optional[str | int]]:
    """Returns dict with info about the currently focused window."""
    # Proper COM init for this thread
    with auto.UIAutomationInitializerInThread():
        ctrl = auto.GetForegroundControl()
        if ctrl is None:
            return {
                WindowInfo.NAME: None,
                WindowInfo.CLASS_NAME: None,
                WindowInfo.PROCESS_ID: 0,
            }
        return {
            WindowInfo.NAME: getattr(ctrl, "Name", None),
            WindowInfo.CLASS_NAME: getattr(ctrl, "ClassName", None),
            WindowInfo.PROCESS_ID: getattr(ctrl, "ProcessId", 0),
        }

def get_process_name(pid: int) -> str:
    try:
        return psutil.Process(pid).name()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, ValueError):
        return "unknown"

def classify_window(win_info: dict[WindowInfo, Optional[str | int]]) -> AppType:
    title = (win_info.get(WindowInfo.NAME) or "").lower()
    process = (get_process_name(win_info.get(WindowInfo.PROCESS_ID)) or "").lower()
    
    if any(app.lower() in process for app in PRODUCTIVE_APPS):
        return AppType.PRODUCTIVE
    elif any(word.lower() in title for word in DISTRACTING_KEYWORDS):
        return AppType.DISTRACTING
    else:
        return AppType.NEUTRAL


# === HELPERS ===
async def safe_sleep(duration: float, stop_event: asyncio.Event):
    try:
        await asyncio.wait_for(stop_event.wait(), timeout=duration)
    except asyncio.TimeoutError:
        pass


# === MAIN FLET APP ===
def before_main(page: ft.Page):
    page.title = "Anti-Slacking Monitor"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.decoration = ft.BoxDecoration(border=ft.Border.all(2, ft.Colors.SURFACE_CONTAINER_HIGHEST))
    page.theme_mode = ft.ThemeMode.DARK
    
    page.window.width = 500
    page.window.height = 400
    page.window.always_on_top = False
    page.window.frameless = True

async def main(page: ft.Page):
    # Setting up Appbar
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
        on_click=lambda _: asyncio.create_task(page.window.close())
    )
    minimize_btn = ft.IconButton(
        icon=ft.Icons.MINIMIZE, icon_color=ft.Colors.PRIMARY,
        on_click=minimize
    )
    
    page.appbar = ft.AppBar(
        title = "Anti-Slacking Monitor",
        actions=[minimize_btn, theme_btn, close_btn]
    )
    
    # Initial Setup
    await page.window.center()
    
    REFRESH_RATE = 0.1
    total_distractions = 0
    
    # Controls
    current_app = ft.Column(
        controls=[ft.Text("Detecting active window...", size=18, weight=ft.FontWeight.BOLD, data="editable_text")],
        scroll=ft.ScrollMode.ALWAYS, expand=True
    )
    category_text = ft.Text("Unknown", size=28, weight=ft.FontWeight.BOLD)
    distractions_counter_text = ft.Text(
        spans=[ft.TextSpan("Times Distracted: "), ft.TextSpan(total_distractions)],
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
    form = ft.WindowDragArea(content=container, maximizable=False, expand=True)
    page.add(form)
    
    # Events
    stop_event = asyncio.Event()

    async def monitor_focus_async():
        nonlocal total_distractions
        prev_title = ""
        
        while not stop_event.is_set():
            # Run blocking call in a background thread with COM initialized
            info = await asyncio.to_thread(get_active_window_info)
            category = classify_window(info)
            title = info.get(WindowInfo.NAME) or "Unknown Window"
            
            if category == AppType.DISTRACTING:
                await page.window.to_front()
            
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
            else:
                total_distractions += 1
                distractions_counter_text.spans[1].text = total_distractions
                distractions_counter_text.update()
                print(f"Incremented total_distractions to: {total_distractions}")
                await safe_sleep(2, stop_event)
        print("Monitor task stopped.")
    
    # Start monitoring task
    page.run_task(monitor_focus_async)
    
    # Stop it cleanly when window closes
    async def on_close(_):
        print("App is closing... Waiting for monitor to stop.")
        if not stop_event.is_set():
            stop_event.set()
    
    page.on_close = on_close


if __name__ == "__main__":
    ft.run(main=main, before_main=before_main)
