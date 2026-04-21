import flet as ft
from typing import Optional
from dataclasses import field

@ft.control
class PresetColumn(ft.Column):
    spacing: ft.Number = 4
    horizontal_alignment: ft.CrossAxisAlignment = ft.CrossAxisAlignment.CENTER

@ft.control
class PresetWindowDragArea(ft.WindowDragArea):
    def init(self):
        self.maximizable = False
        self.expand = True
        self.opacity = 0
        self.offset = ft.Offset(0, -1)
        self.animate_opacity = ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT)
        self.animate_offset = ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT)

@ft.control
class CenteredColumn(ft.Column):
    alignment: ft.MainAxisAlignment = ft.MainAxisAlignment.CENTER
    horizontal_alignment: ft.CrossAxisAlignment = ft.CrossAxisAlignment.CENTER