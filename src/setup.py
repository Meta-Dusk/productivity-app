import flet as ft


def before_main_ui(page: ft.Page):
    page.title = "Anti-Slacking Monitor"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.decoration = ft.BoxDecoration(border=ft.Border.all(2, ft.Colors.SURFACE_CONTAINER_HIGHEST))
    page.theme_mode = ft.ThemeMode.DARK
    
    page.window.width = 550
    page.window.height = 400
    page.window.title_bar_hidden = True
    page.window.prevent_close = True
    page.window.maximized = False
    
    page.on_close = lambda e: print(e)
    page.on_resize = lambda e: print(e)
    page.window.on_event = lambda e: print(e)
    page.update()