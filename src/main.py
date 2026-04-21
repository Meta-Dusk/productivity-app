import flet as ft
from main_ui import main_ui
from setup import before_main_ui


def before_main(page: ft.Page):
    before_main_ui(page)

async def main(page: ft.Page):
    await main_ui(page)
    
    
ft.run(main, before_main)