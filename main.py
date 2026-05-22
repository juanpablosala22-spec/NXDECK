"""
Nintendo Switch Home Menu — Réplica exacta
Fondo gris claro, tiles grandes, dock circular inferior
"""

import datetime
import subprocess
import os
import platform
import webbrowser
import math
import shutil
import json

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.slider import Slider
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.graphics import (
    Color, RoundedRectangle, Rectangle, Line,
    Ellipse, Triangle
)
from kivy.properties import NumericProperty, BooleanProperty, StringProperty
from kivy.utils import get_color_from_hex
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior

IS_PC = platform.system() in ("Windows", "Darwin", "Linux")

# Pantalla completa solo en PC (en Android se deja al sistema)
if IS_PC:
    Window.fullscreen = "auto"
    Window.borderless = True


APP_DIR = os.path.dirname(__file__)
ICON_DIR = os.path.join(APP_DIR, "assets", "icons")
_ICON_TEX_CACHE = {}


def _icon_texture(name):
    if not name:
        return None
    if name in _ICON_TEX_CACHE:
        return _ICON_TEX_CACHE[name]

    try:
        for ext in (".png", ".jpg", ".jpeg"):
            p = os.path.join(ICON_DIR, f"{name}{ext}")
            if os.path.exists(p):
                tex = CoreImage(p).texture
                _ICON_TEX_CACHE[name] = tex
                return tex
    except Exception:
        pass

    _ICON_TEX_CACHE[name] = None
    return None


def _get_app_config():
    try:
        app = App.get_running_app()
        if app and hasattr(app, "config_data"):
            return app.config_data or {}
    except Exception:
        pass
    return {}


def is_pc_mode():
    cfg = _get_app_config()
    force = (cfg.get("force_mode") or "auto").lower()
    if force == "pc":
        return True
    if force in ("android", "celular", "mobile"):
        return False
    return IS_PC


def apply_theme_from_config():
    cfg = _get_app_config()
    dark_mode = bool(cfg.get("dark_mode", False))

    global BG, BG2, TOPBAR_COL, DOCK_BG, DOCK_SEL, TILE_SHADOW, SEL_BLUE, WHITE, BLACK, DARK, MID, LIGHT
    global NRED, NBLU, NGRN, NYLW, NORG, NPUR

    if not dark_mode:
        BG          = get_color_from_hex("#e8e8e8")
        BG2         = get_color_from_hex("#d8d8d8")
        TOPBAR_COL  = get_color_from_hex("#e8e8e8")
        DOCK_BG     = get_color_from_hex("#ffffff")
        DOCK_SEL    = get_color_from_hex("#e60012")
        TILE_SHADOW = (0, 0, 0, 0.18)
        SEL_BLUE    = get_color_from_hex("#0ab9e6")
        WHITE       = (1, 1, 1, 1)
        BLACK       = (0, 0, 0, 1)
        DARK        = get_color_from_hex("#1a1a1a")
        MID         = get_color_from_hex("#555555")
        LIGHT       = get_color_from_hex("#888888")
    else:
        BG          = get_color_from_hex("#101216")
        BG2         = get_color_from_hex("#171a20")
        TOPBAR_COL  = get_color_from_hex("#101216")
        DOCK_BG     = get_color_from_hex("#151820")
        DOCK_SEL    = get_color_from_hex("#e60012")
        TILE_SHADOW = (0, 0, 0, 0.45)
        SEL_BLUE    = get_color_from_hex("#0ab9e6")
        WHITE       = (1, 1, 1, 1)
        BLACK       = (0, 0, 0, 1)
        DARK        = get_color_from_hex("#f2f2f2")
        MID         = get_color_from_hex("#c2c5cc")
        LIGHT       = get_color_from_hex("#8b8f99")

    NRED        = get_color_from_hex("#e60012")
    NBLU        = get_color_from_hex("#0ab9e6")
    NGRN        = get_color_from_hex("#00c851")
    NYLW        = get_color_from_hex("#ffcc00")
    NORG        = get_color_from_hex("#ff6600")
    NPUR        = get_color_from_hex("#6633cc")

    try:
        Window.clearcolor = BG
    except Exception:
        pass

# ── Paleta Switch real (fondo gris claro) ─────────────────────────────────────
BG          = get_color_from_hex("#e8e8e8")   # gris claro fondo
BG2         = get_color_from_hex("#d8d8d8")   # gris más oscuro
TOPBAR_COL  = get_color_from_hex("#e8e8e8")   # top bar misma que fondo
DOCK_BG     = get_color_from_hex("#ffffff")   # fondo dock blanco
DOCK_SEL    = get_color_from_hex("#e60012")   # rojo seleccionado (Nintendo red)
TILE_SHADOW = (0, 0, 0, 0.18)
SEL_BLUE    = get_color_from_hex("#0ab9e6")   # azul selección tile
WHITE       = (1, 1, 1, 1)
BLACK       = (0, 0, 0, 1)
DARK        = get_color_from_hex("#1a1a1a")
MID         = get_color_from_hex("#555555")
LIGHT       = get_color_from_hex("#888888")
NRED        = get_color_from_hex("#e60012")   # Nintendo red
NBLU        = get_color_from_hex("#0ab9e6")   # Nintendo blue
NGRN        = get_color_from_hex("#00c851")
NYLW        = get_color_from_hex("#ffcc00")
NORG        = get_color_from_hex("#ff6600")
NPUR        = get_color_from_hex("#6633cc")


# ─────────────────────────────────────────────────────────────────────────────
# LANZADOR
# ─────────────────────────────────────────────────────────────────────────────

def _first_existing_path(paths):
    for p in paths:
        if not p:
            continue
        try:
            if os.path.isabs(p) and os.path.exists(p):
                return p
        except Exception:
            pass
    return None


def _which_any(names):
    for n in names:
        if not n:
            continue
        try:
            p = shutil.which(n)
            if p:
                return p
        except Exception:
            pass
    return None


PC_APPS = {
    "retroarch": {
        "paths": [
            r"C:\Program Files\RetroArch\retroarch.exe",
            r"C:\Program Files (x86)\RetroArch\retroarch.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\RetroArch\retroarch.exe"),
        ],
        "which": ["retroarch", "retroarch.exe"],
        "url": "https://www.retroarch.com/",
    },
    "dolphin": {
        "paths": [
            r"C:\Program Files\Dolphin Emulator\Dolphin.exe",
            r"C:\Program Files (x86)\Dolphin Emulator\Dolphin.exe",
        ],
        "which": ["dolphin-emu", "dolphin", "Dolphin.exe"],
        "url": "https://dolphin-emu.org/",
    },
    "ppsspp": {
        "paths": [
            r"C:\Program Files\PPSSPP\PPSSPPWindows64.exe",
            r"C:\Program Files\PPSSPP\PPSSPPWindows.exe",
            r"C:\Program Files (x86)\PPSSPP\PPSSPPWindows.exe",
        ],
        "which": ["ppsspp", "PPSSPPWindows64.exe", "PPSSPPWindows.exe"],
        "url": "https://www.ppsspp.org/",
    },
    "mupen": {
        "paths": [],
        "which": ["mupen64plus-ui-console", "mupen64plus"],
        "url": "https://mupen64plus.org/",
    },
    "mgba": {
        "paths": [
            r"C:\Program Files\mGBA\mGBA.exe",
            r"C:\Program Files (x86)\mGBA\mGBA.exe",
        ],
        "which": ["mgba", "mGBA.exe"],
        "url": "https://mgba.io/",
    },
    # DraStic no tiene build oficial para PC: en PC se abre la web.
    "drastic": {
        "paths": [],
        "which": [],
        "url": "https://www.drastic-ds.com/",
    },
    "yuzu": {
        "paths": [
            os.path.expandvars(r"%LOCALAPPDATA%\yuzu\yuzu-windows-msvc\yuzu.exe"),
            os.path.expandvars(r"%APPDATA%\yuzu\yuzu-windows-msvc\yuzu.exe"),
        ],
        "which": ["yuzu", "yuzu.exe"],
        "url": "https://yuzu-emu.org/",
    },
    "steamlink": {
        "paths": [],
        "which": ["steam", "steam.exe"],
        "url": "https://store.steampowered.com/remoteplay",
    },
    "moonlight": {
        "paths": [
            r"C:\Program Files\Moonlight Game Streaming\Moonlight.exe",
            r"C:\Program Files (x86)\Moonlight Game Streaming\Moonlight.exe",
        ],
        "which": ["moonlight", "moonlight.exe", "moonlight-qt"],
        "url": "https://moonlight-stream.org/",
    },
}


def _launch_pc_app(app_key):
    spec = PC_APPS.get(app_key) or {}
    exe = _first_existing_path(spec.get("paths", [])) or _which_any(spec.get("which", []))
    if exe:
        try:
            subprocess.Popen([exe])
            return True
        except Exception:
            pass
    url = spec.get("url")
    if url:
        try:
            webbrowser.open(url)
            return True
        except Exception:
            pass
    return False


def launch(data):
    action = data.get("action")
    if action:
        try:
            app = App.get_running_app()
            if app and hasattr(app, "handle_action"):
                if app.handle_action(action, data):
                    return
        except Exception:
            pass

    pc = data.get("pc")
    if is_pc_mode():
        if not pc:
            return
        if pc.startswith("http"):
            webbrowser.open(pc)
        elif pc in PC_APPS:
            _launch_pc_app(pc)
        elif pc == "chrome":
            paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                "/usr/bin/google-chrome", "/usr/bin/chromium-browser",
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            ]
            for p in paths:
                if os.path.exists(p):
                    subprocess.Popen([p]); return
            webbrowser.open("https://google.com")
        elif pc == "discord":
            paths = [
                os.path.expandvars(r"%LOCALAPPDATA%\Discord\Update.exe"),
                "/usr/bin/discord",
                "/Applications/Discord.app/Contents/MacOS/Discord",
            ]
            for p in paths:
                if os.path.exists(p):
                    if "Update.exe" in p:
                        subprocess.Popen([p, "--processStart", "Discord.exe"])
                    else:
                        subprocess.Popen([p])
                    return
        elif pc == "explorer":
            if platform.system() == "Windows": subprocess.Popen(["explorer"])
            elif platform.system() == "Darwin": subprocess.Popen(["open", os.path.expanduser("~")])
            else: subprocess.Popen(["xdg-open", os.path.expanduser("~")])
    else:
        pkg = data.get("pkg")
        if pkg:
            try:
                subprocess.Popen(["am", "start", "-n", pkg],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass


# ─────────────────────────────────────────────────────────────────────────────
# ÍCONOS CANVAS
# ─────────────────────────────────────────────────────────────────────────────

def draw_icon_on(canvas, name, cx, cy, size, light=False):
    """Dibuja ícono. light=True para fondo claro (dock)."""
    s = size
    h = s * 0.50
    q = s * 0.25
    e = s * 0.11
    fg = (0.25, 0.25, 0.25, 1) if light else WHITE
    tex = _icon_texture(name)

    def _badge_circle(bg):
        Color(0, 0, 0, 0.14)
        Ellipse(pos=(cx-h+dp(2), cy-h-dp(2)), size=(s, s))
        Color(*bg)
        Ellipse(pos=(cx-h, cy-h), size=(s, s))
        Color(1, 1, 1, 0.14)
        Ellipse(pos=(cx-h*0.75, cy-h*0.10), size=(s*0.55, s*0.55))

    def _badge_round(bg, r=dp(12)):
        Color(0, 0, 0, 0.14)
        RoundedRectangle(pos=(cx-h+dp(2), cy-h-dp(2)), size=(s, s), radius=[r])
        Color(*bg)
        RoundedRectangle(pos=(cx-h, cy-h), size=(s, s), radius=[r])
        Color(1, 1, 1, 0.14)
        RoundedRectangle(pos=(cx-h*0.78, cy-h*0.10), size=(s*0.55, s*0.55), radius=[r])

    with canvas:
        if tex is not None:
            Color(1, 1, 1, 1)
            Rectangle(texture=tex, pos=(cx - h, cy - h), size=(s, s))
            return

        if name == "retroarch":
            _badge_circle((0.10, 0.40, 0.95, 1))
            Color(*WHITE)
            Triangle(points=[cx-q*0.55, cy-h*0.55, cx-q*0.55, cy+h*0.55, cx+h*0.62, cy])
            Color(1, 1, 1, 0.25)
            Line(points=[cx-q*0.40, cy-h*0.25, cx+h*0.42, cy], width=dp(2.0))

        elif name == "dolphin":
            _badge_circle((0.07, 0.55, 0.90, 1))
            Color(*WHITE)
            Ellipse(pos=(cx-q*0.95, cy-e*0.95), size=(s*0.58, e*2.0))
            Color(0.07, 0.55, 0.90, 1)
            Ellipse(pos=(cx-q*0.52, cy-e*0.55), size=(s*0.32, e*1.1))
            Color(*WHITE)
            Line(points=[cx-q*0.10, cy-e*0.15, cx+h*0.45, cy+e*0.45], width=dp(2.0))

        elif name == "ppsspp":
            _badge_round((0.00, 0.30, 0.75, 1), r=dp(14))
            Color(*WHITE)
            for xo in [-q*0.85, 0, q*0.85]:
                Rectangle(pos=(cx+xo-e, cy-h*0.45), size=(e*2, s*0.55))
            Rectangle(pos=(cx-q*0.85, cy+e*0.8), size=(s*0.50, e*1.4))
            Rectangle(pos=(cx-q*0.85+e*2, cy-e*0.3), size=(s*0.25, e*1.4))

        elif name == "mupen":
            _badge_round((0.12, 0.12, 0.12, 1), r=dp(14))
            Color(0.85, 0.05, 0.05, 1)
            Ellipse(pos=(cx-e, cy-e*0.3), size=(e*2, e*2))
            Color(*WHITE)
            Ellipse(pos=(cx-h*0.65, cy+e*0.5), size=(e*1.8, e*1.8))
            Ellipse(pos=(cx+h*0.30, cy+e*0.5), size=(e*1.8, e*1.8))

        elif name == "mgba":
            _badge_round((0.40, 0.30, 0.85, 1), r=dp(14))
            Color(*WHITE)
            Rectangle(pos=(cx-q*0.7, cy-e*0.3), size=(s*0.42, e*1.4))
            Color(0.00, 0.70, 0.20, 1)
            Ellipse(pos=(cx+q*0.20, cy-e*1.4), size=(e*2.4, e*2.4))

        elif name == "drastic":
            _badge_round((0.18, 0.18, 0.25, 1), r=dp(14))
            Color(0.00, 0.70, 0.90, 1)
            RoundedRectangle(pos=(cx-h+e*2, cy+e*1.2), size=(s-e*4, h*0.62), radius=[dp(6)])
            RoundedRectangle(pos=(cx-h+e*2, cy-h*0.58), size=(s-e*4, h*0.62), radius=[dp(6)])
            Color(1, 1, 1, 0.22)
            Line(points=[cx-h+e*3, cy+e*1.2+h*0.46, cx+h-e*3, cy+e*1.2+h*0.46], width=dp(1.6))

        elif name == "yuzu":
            _badge_round((0.85, 0.00, 0.08, 1), r=dp(14))
            Color(*WHITE)
            Line(circle=(cx-q*0.30, cy, q*0.68), width=dp(2.5))
            Line(circle=(cx+q*0.30, cy, q*0.68), width=dp(2.5))
            Color(1, 1, 1, 0.22)
            Line(points=[cx, cy-h*0.35, cx, cy+h*0.35], width=dp(2.0))

        elif name == "steam":
            _badge_circle((0.17, 0.22, 0.35, 1))
            Color(*WHITE)
            Ellipse(pos=(cx-q*0.78, cy-q*0.78), size=(s*0.52, s*0.52))
            Color(0.17, 0.22, 0.35, 1)
            Ellipse(pos=(cx-q*0.40, cy-q*0.40), size=(s*0.26, s*0.26))
            Color(*WHITE)
            Line(points=[cx-q*0.02, cy+q*0.10, cx+h*0.40, cy+h*0.20], width=dp(3.0))
            Ellipse(pos=(cx+h*0.18, cy+h*0.04), size=(s*0.20, s*0.20))
            Color(0.17, 0.22, 0.35, 1)
            Ellipse(pos=(cx+h*0.23, cy+h*0.09), size=(s*0.10, s*0.10))

        elif name == "moonlight":
            _badge_circle((0.10, 0.10, 0.28, 1))
            Color(0.90, 0.85, 0.30, 1)
            Ellipse(pos=(cx-q*0.85, cy-q*0.85), size=(s*0.52, s*0.52))
            Color(0.10, 0.10, 0.28, 1)
            Ellipse(pos=(cx-q*0.25, cy-q*0.88), size=(s*0.50, s*0.50))
            Color(1, 1, 1, 0.20)
            Line(circle=(cx, cy, h*0.62), width=dp(1.8))

        elif name == "discord":
            _badge_round((0.35, 0.40, 0.87, 1), r=dp(14))
            Color(*WHITE)
            Ellipse(pos=(cx-q*0.90, cy-e*0.4), size=(e*2.6, e*2.6))
            Ellipse(pos=(cx+q*0.20, cy-e*0.4), size=(e*2.6, e*2.6))

        elif name == "youtube":
            _badge_round((0.88, 0.00, 0.00, 1), r=dp(14))
            Color(*WHITE)
            Triangle(points=[cx-q*0.48, cy-h*0.38, cx-q*0.48, cy+h*0.38, cx+h*0.55, cy])

        elif name == "chrome":
            Color(0.95, 0.95, 0.95, 1)
            Ellipse(pos=(cx-h, cy-h), size=(s, s))
            Color(0.85, 0.20, 0.10, 1)
            Triangle(points=[cx, cy, cx-h, cy+h, cx+h, cy+h])
            Color(0.10, 0.65, 0.20, 1)
            Triangle(points=[cx, cy, cx+h, cy+h, cx+h, cy-h])
            Color(0.95, 0.80, 0.10, 1)
            Triangle(points=[cx, cy, cx-h, cy+h, cx-h, cy-h])
            Color(0.20, 0.45, 0.90, 1)
            Ellipse(pos=(cx-q*0.68, cy-q*0.68), size=(s*0.45, s*0.45))
            Color(0.95, 0.95, 0.95, 1)
            Ellipse(pos=(cx-q*0.45, cy-q*0.45), size=(s*0.30, s*0.30))

        elif name == "settings":
            Color(*fg)
            Ellipse(pos=(cx-h, cy-h), size=(s, s))
            col_bg = (0.91, 0.91, 0.91, 1) if light else (0.15, 0.15, 0.15, 1)
            Color(*col_bg)
            Ellipse(pos=(cx-q*0.65, cy-q*0.65), size=(s*0.42, s*0.42))
            Color(*fg)
            for ang in range(0, 360, 45):
                r = math.radians(ang)
                tx = cx + math.cos(r) * h * 0.82
                ty = cy + math.sin(r) * h * 0.82
                Ellipse(pos=(tx-e, ty-e), size=(e*2.2, e*2.2))

        elif name == "gallery":
            Color(0.35, 0.10, 0.55, 1)
            RoundedRectangle(pos=(cx-h, cy-h), size=(s, s), radius=[dp(6)])
            Color(*WHITE)
            RoundedRectangle(pos=(cx-h+e*2, cy-h+e*2), size=(s-e*4, s-e*4), radius=[dp(3)])
            Color(0.35, 0.10, 0.55, 1)
            Ellipse(pos=(cx-h+e*4, cy+e*2), size=(e*4, e*4))
            Triangle(points=[cx-h+e*2, cy-e, cx, cy+e*4, cx+e*5, cy-e])
            Triangle(points=[cx, cy-e, cx+e*4, cy+e*3, cx+h-e*2, cy-e])

        # ── Íconos del dock Switch ───────────────────────────────────────

        elif name == "switch_online":
            # Nintendo Switch Online — círculo rojo con silueta Switch
            Color(*NRED)
            Ellipse(pos=(cx-h, cy-h), size=(s, s))
            Color(*WHITE)
            RoundedRectangle(pos=(cx-q*0.9, cy-q*0.7), size=(s*0.55, s*0.42), radius=[dp(3)])
            Color(*NRED)
            Ellipse(pos=(cx-q*0.6, cy-e), size=(e*2.2, e*2.2))

        elif name == "news":
            # Noticias — pantalla con antena
            Color(*fg)
            RoundedRectangle(pos=(cx-h*0.85, cy-h*0.65), size=(s*0.70, s*0.55), radius=[dp(3)])
            col_bg = (0.91, 0.91, 0.91, 1) if light else (0.15, 0.15, 0.15, 1)
            Color(*col_bg)
            RoundedRectangle(pos=(cx-h*0.72, cy-h*0.52), size=(s*0.45, s*0.30), radius=[dp(2)])
            Color(*fg)
            Line(points=[cx, cy+h*0.30, cx, cy+h*0.65], width=dp(2))
            Line(points=[cx-q*0.7, cy+h*0.65, cx+q*0.7, cy+h*0.65], width=dp(2))

        elif name == "eshop":
            # eShop — bolsa naranja
            Color(*NORG)
            RoundedRectangle(pos=(cx-h*0.75, cy-h*0.75), size=(s*0.75, s*0.75), radius=[dp(6)])
            Color(*WHITE)
            Line(points=[cx-q*0.4, cy+h*0.10, cx-q*0.4, cy+h*0.55,
                         cx+q*0.4, cy+h*0.55, cx+q*0.4, cy+h*0.10], width=dp(2.5))

        elif name == "album":
            # Álbum — marco de foto
            Color(*fg)
            RoundedRectangle(pos=(cx-h*0.80, cy-h*0.80), size=(s*0.80, s*0.80), radius=[dp(5)])
            col_bg = (0.91, 0.91, 0.91, 1) if light else (0.15, 0.15, 0.15, 1)
            Color(*col_bg)
            Rectangle(pos=(cx-h*0.65, cy-h*0.65), size=(s*0.50, s*0.50))
            Color(0.55, 0.75, 0.95, 1)
            Rectangle(pos=(cx-h*0.65, cy-h*0.65), size=(s*0.50, s*0.30))
            Color(*fg)
            Ellipse(pos=(cx-h*0.35, cy+e), size=(e*2.5, e*2.5))

        elif name == "controllers":
            # Controladores — Joy-Con izq + der
            Color(*NRED)
            RoundedRectangle(pos=(cx-h*0.90, cy-h*0.72), size=(h*0.72, s*0.72), radius=[dp(8), 0, 0, dp(8)])
            Color(*NBLU)
            RoundedRectangle(pos=(cx+h*0.18, cy-h*0.72), size=(h*0.72, s*0.72), radius=[0, dp(8), dp(8), 0])
            Color(*WHITE)
            Ellipse(pos=(cx-h*0.62, cy+e), size=(e*2, e*2))
            Ellipse(pos=(cx+h*0.28, cy+e), size=(e*2, e*2))

        elif name == "power":
            # Encender/apagar
            Color(*fg)
            Line(circle=(cx, cy, h*0.72), width=dp(2.5))
            Line(points=[cx, cy-h*0.10, cx, cy+h*0.75], width=dp(2.5))

        elif name == "vlc":
            Color(1.00, 0.62, 0.00, 1)
            Triangle(points=[cx-h, cy-h, cx+h, cy-h, cx, cy+h])
            Color(*WHITE)
            Triangle(points=[cx-q, cy-q*0.6, cx+q, cy-q*0.6, cx, cy+q*0.8])

        else:
            Color(*fg)
            RoundedRectangle(pos=(cx-h, cy-h), size=(s, s), radius=[dp(6)])


# ─────────────────────────────────────────────────────────────────────────────
# DATOS
# ─────────────────────────────────────────────────────────────────────────────

GAMES = [
    {"name": "RetroArch",  "icon": "retroarch", "color": [0.10, 0.35, 0.80, 1],
     "pkg": "com.retroarch/.browser.retroactivity.RetroActivityFuture", "pc": "retroarch"},
    {"name": "Dolphin",    "icon": "dolphin",   "color": [0.10, 0.45, 0.75, 1],
     "pkg": "org.dolphinemu.dolphinemu/.activities.MainActivity",         "pc": "dolphin"},
    {"name": "PPSSPP",     "icon": "ppsspp",    "color": [0.00, 0.25, 0.65, 1],
     "pkg": "org.ppsspp.ppsspp/.PpssppActivity",                          "pc": "ppsspp"},
    {"name": "Mupen64",    "icon": "mupen",     "color": [0.20, 0.20, 0.20, 1],
     "pkg": "org.mupen64plusae/.activity.StartActivity",                  "pc": "mupen"},
    {"name": "mGBA",       "icon": "mgba",      "color": [0.35, 0.28, 0.75, 1],
     "pkg": "io.mgba.App/.ui.activities.MainActivity",                    "pc": "mgba"},
    {"name": "DraStic",    "icon": "drastic",   "color": [0.15, 0.15, 0.22, 1],
     "pkg": "com.dsemu.drastic/.DraSticActivity",                         "pc": "drastic"},
    {"name": "Yuzu",       "icon": "yuzu",      "color": [0.75, 0.00, 0.08, 1],
     "pkg": "org.yuzu.yuzu_emu/.ui.main.MainActivity",                    "pc": "yuzu"},
    {"name": "Steam Link", "icon": "steam",     "color": [0.10, 0.17, 0.27, 1],
     "pkg": "com.valvesoftware.steamlink/.SteamLink",                     "pc": "steamlink"},
    {"name": "Moonlight",  "icon": "moonlight", "color": [0.08, 0.08, 0.22, 1],
     "pkg": "com.limelight/.Game",                                        "pc": "moonlight"},
    {"name": "Discord",    "icon": "discord",   "color": [0.32, 0.37, 0.85, 1],
     "pkg": "com.discord/.app.AppActivity$AppActivity",                   "pc": "discord"},
]

DOCK = [
    {"name": "Online",       "icon": "switch_online", "color": [0.90, 0.00, 0.07, 1], "pkg": None, "pc": None},
    {"name": "YouTube",      "icon": "youtube",       "color": [0.88, 0.00, 0.00, 1], "pkg": "com.google.android.youtube/.HomeActivity", "pc": "https://youtube.com"},
    {"name": "eShop",        "icon": "eshop",         "color": [1.00, 0.40, 0.00, 1], "pkg": None, "pc": None},
    {"name": "Álbum",        "icon": "album",         "color": [0.30, 0.30, 0.35, 1], "pkg": None, "pc": "explorer"},
    {"name": "Chrome",       "icon": "chrome",        "color": [0.20, 0.20, 0.20, 1], "pkg": "com.android.chrome/com.google.android.apps.chrome.Main", "pc": "chrome"},
    {"name": "Ajustes",      "icon": "settings",      "color": [0.30, 0.30, 0.35, 1], "pkg": "com.android.settings/.Settings", "pc": None, "action": "settings"},
    {"name": "Apagar",       "icon": "power",         "color": [0.30, 0.30, 0.35, 1], "pkg": None, "pc": None, "action": "quit"},
]


# ─────────────────────────────────────────────────────────────────────────────
# GAME TILE — fiel a la foto: tile grande con color, más grande si seleccionado
# ─────────────────────────────────────────────────────────────────────────────

class GameTile(ButtonBehavior, Widget):
    selected = BooleanProperty(False)

    BASE_W = dp(185)
    BASE_H = dp(240)
    SEL_W  = dp(220)
    SEL_H  = dp(270)

    def __init__(self, data, **kwargs):
        super().__init__(**kwargs)
        self.data = data
        self.size_hint = (None, None)
        self.size = (self.BASE_W, self.BASE_H)
        self._lbl = Label(text=data["name"], font_size=dp(11), bold=True,
                          color=(0.2, 0.2, 0.2, 1), halign="center",
                          text_size=(self.BASE_W - dp(8), None))
        self.add_widget(self._lbl)
        self.bind(pos=self._redraw, size=self._redraw, selected=self._redraw)

    def _redraw(self, *a):
        self.canvas.before.clear()
        cx = self.center_x
        cy = self.center_y + dp(12)
        with self.canvas.before:
            # Sombra
            Color(0, 0, 0, 0.15)
            RoundedRectangle(pos=(self.x+dp(4), self.y-dp(4)),
                             size=(self.width, self.height), radius=[dp(10)])
            # Fondo tile
            Color(*self.data["color"])
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])
            # Borde azul si seleccionado
            if self.selected:
                Color(*NBLU)
                Line(rounded_rectangle=[self.x+2, self.y+2,
                     self.width-4, self.height-4, dp(10)], width=dp(3))
            # Ícono centrado
            draw_icon_on(self.canvas.before, self.data["icon"], cx, cy,
                         size=min(self.width, self.height) * 0.45)

        # Etiqueta nombre
        self._lbl.pos  = (self.x, self.y + dp(4))
        self._lbl.size = (self.width, dp(22))
        self._lbl.text_size = (self.width - dp(8), None)

    def on_selected(self, *a):
        if self.selected:
            Animation(size=(self.SEL_W, self.SEL_H), duration=0.12, t="out_back").start(self)
        else:
            Animation(size=(self.BASE_W, self.BASE_H), duration=0.08).start(self)

    def on_press(self):
        launch(self.data)


# ─────────────────────────────────────────────────────────────────────────────
# DOCK ICON — circulito blanco estilo Switch real
# ─────────────────────────────────────────────────────────────────────────────

class DockIcon(ButtonBehavior, Widget):
    selected = BooleanProperty(False)

    def __init__(self, data, **kwargs):
        super().__init__(**kwargs)
        self.data = data
        self.size_hint = (None, None)
        self.size = (dp(58), dp(80))
        self._lbl = Label(text=data["name"], font_size=dp(8),
                          color=(0.3, 0.3, 0.3, 1), halign="center")
        self.add_widget(self._lbl)
        self.bind(pos=self._redraw, size=self._redraw, selected=self._redraw)

    def _redraw(self, *a):
        self.canvas.before.clear()
        r  = dp(24)
        cx = self.center_x
        cy = self.y + dp(52)
        with self.canvas.before:
            # Sombra
            Color(0, 0, 0, 0.12)
            Ellipse(pos=(cx-r+dp(2), cy-r-dp(2)), size=(r*2, r*2))
            # Círculo blanco fondo
            Color(1, 1, 1, 1)
            Ellipse(pos=(cx-r, cy-r), size=(r*2, r*2))
            # Anillo rojo si seleccionado
            if self.selected:
                Color(*NRED)
                Line(circle=(cx, cy, r+dp(2.5)), width=dp(2.5))
            # Ícono (light=True porque fondo es blanco)
            draw_icon_on(self.canvas.before, self.data["icon"], cx, cy,
                         size=r*1.05, light=True)
        # Etiqueta
        col = (0.90, 0.00, 0.07, 1) if self.selected else (0.35, 0.35, 0.35, 1)
        self._lbl.color = col
        self._lbl.bold  = self.selected
        self._lbl.pos   = (self.x, self.y)
        self._lbl.size  = (self.width, dp(20))

    def on_press(self):
        launch(self.data)


# ─────────────────────────────────────────────────────────────────────────────
# HOME SCREEN
# ─────────────────────────────────────────────────────────────────────────────

class HomeScreen(Screen):
    game_sel = NumericProperty(0)
    dock_sel = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._gtiles = []
        self._dicons = []
        self._focus  = "games"   # "games" o "dock"
        self._root = None
        self._build()
        Window.bind(on_key_down=self._key)
        Window.bind(size=lambda *a: self._reflow())

    def _build(self):
        W = Window.width
        H = Window.height
        root = FloatLayout()
        self._root = root

        # ── Fondo gris claro ──────────────────────────────────────────────────
        with root.canvas.before:
            self._bg_col = Color(*BG)
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda *a: setattr(self._bg, "pos", root.pos),
                  size=lambda *a: setattr(self._bg, "size", root.size))



        # ── TOP BAR ───────────────────────────────────────────────────────────
        self._build_topbar(root, W, H)

        # ── ZONA DE JUEGOS (centro) ───────────────────────────────────────────
        TOP_H  = dp(52)
        DOCK_H = dp(100)
        MID_H  = H - TOP_H - DOCK_H

        # ScrollView horizontal con los tiles
        self.scroll = ScrollView(
            size_hint=(None, None),
            size=(W, MID_H),
            pos=(0, DOCK_H),
            do_scroll_x=True, do_scroll_y=False,
            bar_width=0,
        )
        self.grid = GridLayout(
            rows=1, spacing=dp(12),
            padding=[dp(48), dp(20), dp(48), dp(20)],
            size_hint=(None, 1),
        )
        self.grid.bind(minimum_width=self.grid.setter("width"))

        for g in GAMES:
            t = GameTile(data=g)
            t.bind(on_press=lambda tile=t: self._game_press(tile))
            self._gtiles.append(t)
            self.grid.add_widget(t)

        self.scroll.add_widget(self.grid)
        root.add_widget(self.scroll)

        # ── DOCK ──────────────────────────────────────────────────────────────
        self._build_dock(root, W, H)

        # ── BOTTOM HINTS ──────────────────────────────────────────────────────
        self._ahint = Label(
            text="A  OK",
            font_size=dp(11), bold=True,
            color=(0.25, 0.25, 0.25, 1),
            pos=(W - dp(70), dp(6)),
            size=(dp(60), dp(20)),
        )
        root.add_widget(self._ahint)

        # Ícono consola abajo izq
        self._conlbl = Label(
            text="[Switch]", font_size=dp(8), color=(0.5, 0.5, 0.5, 1),
            pos=(dp(8), dp(6)), size=(dp(60), dp(20)),
        )
        root.add_widget(self._conlbl)

        self.add_widget(root)
        self._update_games()
        self._update_dock()
        self._reflow()

    def _reflow(self):
        if not self._root:
            return

        W = Window.width
        H = Window.height
        TOP_H  = dp(52)
        DOCK_H = dp(100)
        MID_H  = max(H - TOP_H - DOCK_H, dp(10))

        if hasattr(self, "scroll"):
            self.scroll.size = (W, MID_H)
            self.scroll.pos = (0, DOCK_H)

        if hasattr(self, "_tb"):
            self._tb.size = (W, TOP_H)
            self._tb.pos = (0, H - TOP_H)
            try:
                self._tb.canvas.before.clear()
                with self._tb.canvas.before:
                    Color(*BG)
                    Rectangle(pos=self._tb.pos, size=self._tb.size)
            except Exception:
                pass

        if hasattr(self, "_avatar"):
            self._avatar.pos = (dp(14), H - TOP_H + dp(7))
        if hasattr(self, "_clk"):
            self._clk.pos = (W - dp(140), H - TOP_H + dp(18))
        if hasattr(self, "_dat"):
            self._dat.pos = (W - dp(90), H - TOP_H + dp(8))
        if hasattr(self, "_wifi_w"):
            self._wifi_w.pos = (W - dp(85), H - TOP_H + dp(20))
        if hasattr(self, "_bat_w"):
            self._bat_w.pos = (W - dp(58), H - TOP_H + dp(20))

        if hasattr(self, "_dock_bg"):
            self._dock_bg.size = (W, DOCK_H)
            self._dock_bg.pos = (0, 0)
            try:
                self._dock_bg.canvas.before.clear()
                with self._dock_bg.canvas.before:
                    Color(0.75, 0.75, 0.75, 1)
                    Line(points=[0, DOCK_H, W, DOCK_H], width=dp(1))
                    Color(*DOCK_BG[:3], 0.55)
                    Rectangle(pos=(0, 0), size=(W, DOCK_H))
            except Exception:
                pass

        if self._dicons:
            n = len(self._dicons)
            gap = dp(72)
            x0 = W/2 - (n-1)*gap/2
            for i, ic in enumerate(self._dicons):
                ic.pos = (x0 + i*gap - dp(29), dp(6))

        if hasattr(self, "_ahint"):
            self._ahint.pos = (W - dp(70), dp(6))
        if hasattr(self, "_conlbl"):
            self._conlbl.pos = (dp(8), dp(6))

    def _build_topbar(self, root, W, H):
        TOP_H = dp(52)
        tb = Widget(size_hint=(None, None), size=(W, TOP_H),
                    pos=(0, H - TOP_H))
        self._tb = tb
        with tb.canvas.before:
            Color(*BG)
            Rectangle(pos=tb.pos, size=tb.size)

        # Avatar (círculo amarillo con cara)
        self._avatar = Widget(size_hint=(None, None), size=(dp(38), dp(38)),
                              pos=(dp(14), H - TOP_H + dp(7)))
        with self._avatar.canvas:
            Color(*NYLW)
            Ellipse(pos=self._avatar.pos, size=self._avatar.size)
            Color(0.85, 0.55, 0.10, 1)
            # Cara simple
            cx = self._avatar.x + dp(19)
            cy = self._avatar.y + dp(19)
            Color(0.20, 0.10, 0.00, 1)
            Ellipse(pos=(cx-dp(5), cy+dp(2)), size=(dp(4), dp(4)))
            Ellipse(pos=(cx+dp(2), cy+dp(2)), size=(dp(4), dp(4)))
            Line(points=[cx-dp(5), cy-dp(4), cx-dp(2), cy-dp(7), cx+dp(2), cy-dp(7), cx+dp(5), cy-dp(4)], width=dp(1.5))

        root.add_widget(tb)
        root.add_widget(self._avatar)

        # Reloj + wifi + batería — derecha
        self._clk = Label(text="00:00", font_size=dp(16), bold=True,
                          color=DARK, pos=(W - dp(140), H - TOP_H + dp(18)),
                          size=(dp(50), dp(20)))
        self._dat = Label(text="", font_size=dp(9), color=MID,
                          pos=(W - dp(90), H - TOP_H + dp(8)),
                          size=(dp(80), dp(16)))

        # WiFi icon (canvas)
        self._wifi_w = Widget(size_hint=(None,None), size=(dp(22), dp(18)),
                              pos=(W - dp(85), H - TOP_H + dp(20)))
        with self._wifi_w.canvas:
            Color(*MID)
            Line(circle=(self._wifi_w.center_x, self._wifi_w.y+dp(4), dp(14)), width=dp(1.5),
                 angle_start=20, angle_end=160)
            Line(circle=(self._wifi_w.center_x, self._wifi_w.y+dp(4), dp(9)), width=dp(1.5),
                 angle_start=25, angle_end=155)
            Line(circle=(self._wifi_w.center_x, self._wifi_w.y+dp(4), dp(4)), width=dp(1.5),
                 angle_start=30, angle_end=150)
            Ellipse(pos=(self._wifi_w.center_x-dp(2), self._wifi_w.y), size=(dp(4), dp(4)))

        # Batería
        self._bat_w = Widget(size_hint=(None,None), size=(dp(28), dp(16)),
                             pos=(W - dp(58), H - TOP_H + dp(20)))
        with self._bat_w.canvas:
            Color(*MID)
            Line(rounded_rectangle=[self._bat_w.x, self._bat_w.y+dp(2),
                                     dp(22), dp(12), dp(2)], width=dp(1.5))
            Rectangle(pos=(self._bat_w.x+dp(22), self._bat_w.y+dp(5)), size=(dp(3), dp(6)))
            Color(0.10, 0.75, 0.20, 1)
            RoundedRectangle(pos=(self._bat_w.x+dp(2), self._bat_w.y+dp(4)),
                             size=(dp(16), dp(8)), radius=[dp(1)])

        for w in [self._clk, self._dat, self._wifi_w, self._bat_w]:
            root.add_widget(w)

        Clock.schedule_interval(self._tick, 1)
        self._tick(0)

    def _tick(self, dt):
        now = datetime.datetime.now()
        self._clk.text = now.strftime("%H:%M")
        dias  = ["Lun","Mar","Mié","Jue","Vie","Sáb","Dom"]
        meses = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
        self._dat.text = f"{dias[now.weekday()]} {now.day} {meses[now.month-1]}"

    def _build_dock(self, root, W, H):
        DOCK_H = dp(100)

        # Fondo dock — línea separadora + fondo blanco semitransparente
        dock_bg = Widget(size_hint=(None,None), size=(W, DOCK_H), pos=(0, 0))
        self._dock_bg = dock_bg
        with dock_bg.canvas.before:
            Color(0.75, 0.75, 0.75, 1)
            Line(points=[0, DOCK_H, W, DOCK_H], width=dp(1))
            Color(1, 1, 1, 0.55)
            Rectangle(pos=(0, 0), size=(W, DOCK_H))
        root.add_widget(dock_bg)

        n   = len(DOCK)
        gap = dp(72)
        x0  = W/2 - (n-1)*gap/2

        for i, d in enumerate(DOCK):
            ic = DockIcon(data=d)
            ic.pos = (x0 + i*gap - dp(29), dp(6))
            ic.bind(on_press=lambda ico=ic: self._dock_press(ico))
            self._dicons.append(ic)
            root.add_widget(ic)

    # ── Selección ─────────────────────────────────────────────────────────────

    def _update_games(self):
        for i, t in enumerate(self._gtiles):
            t.selected = (i == self.game_sel) and (self._focus == "games")
        # Auto-scroll para centrar el tile seleccionado
        tile_w = GameTile.BASE_W + dp(12)
        total  = len(GAMES) * tile_w + dp(96)
        vis    = self.scroll.width
        if total > vis:
            target = self.game_sel * tile_w
            sv = min(max(target / (total - vis), 0), 1.0)
            Animation(scroll_x=sv, duration=0.18).start(self.scroll)

    def _update_dock(self):
        for i, ic in enumerate(self._dicons):
            ic.selected = (i == self.dock_sel) and (self._focus == "dock")

    def _game_press(self, tile):
        self.game_sel = self._gtiles.index(tile)
        self._focus = "games"
        self._update_games()
        launch(tile.data)

    def _dock_press(self, icon):
        self.dock_sel = self._dicons.index(icon)
        self._focus = "dock"
        self._update_dock()

    # ── Teclado / Mando ───────────────────────────────────────────────────────

    def _key(self, window, key, scancode, codepoint, modifier):
        if self._focus == "games":
            if   key in (275, ord('d')): self.game_sel = min(self.game_sel+1, len(GAMES)-1)
            elif key in (276, ord('a')): self.game_sel = max(self.game_sel-1, 0)
            elif key in (274, ord('s')):
                self._focus = "dock"; self._update_games(); self._update_dock(); return True
            elif key in (13, ord('z'), ord(' ')):
                launch(self._gtiles[self.game_sel].data); return True
            elif key in (27,): return True
            else: return False
            self._update_games()

        else:  # dock
            if   key in (275, ord('d')): self.dock_sel = min(self.dock_sel+1, len(DOCK)-1)
            elif key in (276, ord('a')): self.dock_sel = max(self.dock_sel-1, 0)
            elif key in (273, ord('w')):
                self._focus = "games"; self._update_games(); self._update_dock(); return True
            elif key in (13, ord('z'), ord(' ')):
                launch(self._dicons[self.dock_sel].data); return True
            elif key in (27,): return True
            else: return False
            self._update_dock()

        return True

    def on_enter(self):
        self.opacity = 0
        Animation(opacity=1, duration=0.5).start(self)


    def apply_theme(self):
        try:
            self._bg_col.rgba = BG
        except Exception:
            pass
        try:
            for t in self._gtiles:
                t._redraw()
            for ic in self._dicons:
                ic._redraw()
        except Exception:
            pass
        self._reflow()


class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._cat = "internet"
        self._toast = None
        self._tb = None
        self._title = None
        self._btn_back = None
        self._body = None
        self._left = None
        self._right = None
        self._cat_buttons = {}
        self._build()
        Window.bind(size=lambda *a: self._reflow())

    def _build(self):
        root = FloatLayout()

        with root.canvas.before:
            self._bg_col = Color(*BG)
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda *a: setattr(self._bg, "pos", root.pos),
                  size=lambda *a: setattr(self._bg, "size", root.size))

        # UI tipo Nintendo Switch: categorías (izq) + detalle (der)
        TOP_H = dp(52)
        self._tb = Widget(size_hint=(1, None), height=TOP_H, pos=(0, Window.height - TOP_H))
        with self._tb.canvas.before:
            self._tb_col = Color(*BG)
            self._tb_bg = Rectangle(pos=self._tb.pos, size=self._tb.size)
        self._tb.bind(pos=lambda *a: setattr(self._tb_bg, "pos", self._tb.pos),
                      size=lambda *a: setattr(self._tb_bg, "size", self._tb.size))
        root.add_widget(self._tb)

        self._title = Label(text="Configuración", font_size=dp(18), bold=True, color=DARK,
                            size_hint=(None, None), size=(dp(260), TOP_H),
                            pos=(dp(20), Window.height - TOP_H + dp(6)))
        root.add_widget(self._title)

        self._btn_back = Button(text="Volver", size_hint=(None, None), size=(dp(110), dp(36)),
                                pos=(Window.width - dp(130), Window.height - TOP_H + dp(8)))
        self._btn_back.bind(on_release=lambda *a: self._go_back())
        root.add_widget(self._btn_back)

        self._body = BoxLayout(orientation="horizontal", spacing=dp(14),
                               padding=[dp(20), dp(18), dp(20), dp(20)],
                               size_hint=(1, None))
        root.add_widget(self._body)

        self._left = BoxLayout(orientation="vertical", spacing=dp(8), size_hint=(None, 1), width=dp(260))
        with self._left.canvas.before:
            self._left_col = Color(1, 1, 1, 0.20 if _get_app_config().get("dark_mode") else 0.55)
            self._left_bg = RoundedRectangle(pos=self._left.pos, size=self._left.size, radius=[dp(12)])
        self._left.bind(pos=lambda *a: setattr(self._left_bg, "pos", self._left.pos),
                        size=lambda *a: setattr(self._left_bg, "size", self._left.size))
        self._body.add_widget(self._left)

        self._right = BoxLayout(orientation="vertical", spacing=dp(10), padding=[dp(14), dp(14), dp(14), dp(14)])
        with self._right.canvas.before:
            self._right_col = Color(1, 1, 1, 0.20 if _get_app_config().get("dark_mode") else 0.55)
            self._right_bg = RoundedRectangle(pos=self._right.pos, size=self._right.size, radius=[dp(12)])
        self._right.bind(pos=lambda *a: setattr(self._right_bg, "pos", self._right.pos),
                         size=lambda *a: setattr(self._right_bg, "size", self._right.size))
        self._body.add_widget(self._right)

        self._cat_buttons = {}
        for key, label in [
            ("internet", "Internet (Wi‑Fi)"),
            ("bluetooth", "Bluetooth"),
            ("sonido", "Sonido"),
            ("pantalla", "Pantalla"),
            ("sistema", "Sistema"),
            ("launcher", "Launcher"),
        ]:
            b = Button(text=label, size_hint=(1, None), height=dp(44))
            b.bind(on_release=lambda btn, k=key: self._select_cat(k))
            self._left.add_widget(b)
            self._cat_buttons[key] = b

        self._toast = Label(text="", font_size=dp(12), color=WHITE,
                            size_hint=(None, None), size=(dp(520), dp(32)),
                            pos=(Window.width/2 - dp(260), dp(14)),
                            opacity=0)
        with self._toast.canvas.before:
            Color(0, 0, 0, 0.60)
            self._toast_bg = RoundedRectangle(pos=self._toast.pos, size=self._toast.size, radius=[dp(8)])
        self._toast.bind(pos=lambda *a: setattr(self._toast_bg, "pos", self._toast.pos),
                         size=lambda *a: setattr(self._toast_bg, "size", self._toast.size))
        root.add_widget(self._toast)

        self.add_widget(root)
        self._select_cat(self._cat)
        self._reflow()
        return

        panel = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=[dp(20), dp(20), dp(20), dp(20)],
            size_hint=(None, None),
        )
        root.add_widget(panel)
        self._panel = panel

        title = Label(text="Configuración", font_size=dp(22), bold=True, color=DARK,
                      size_hint=(1, None), height=dp(34))
        panel.add_widget(title)

        row_mode = BoxLayout(orientation="horizontal", size_hint=(1, None), height=dp(40), spacing=dp(10))
        row_mode.add_widget(Label(text="Modo:", font_size=dp(14), color=DARK, size_hint=(None, 1), width=dp(90)))
        self._btn_auto = Button(text="Auto", size_hint=(1, 1))
        self._btn_pc = Button(text="PC", size_hint=(1, 1))
        self._btn_android = Button(text="Celular", size_hint=(1, 1))
        row_mode.add_widget(self._btn_auto)
        row_mode.add_widget(self._btn_pc)
        row_mode.add_widget(self._btn_android)
        panel.add_widget(row_mode)

        row_dark = BoxLayout(orientation="horizontal", size_hint=(1, None), height=dp(36), spacing=dp(10))
        row_dark.add_widget(Label(text="Modo oscuro:", font_size=dp(14), color=DARK, size_hint=(1, 1)))
        self._chk_dark = CheckBox(size_hint=(None, None), size=(dp(28), dp(28)))
        row_dark.add_widget(self._chk_dark)
        panel.add_widget(row_dark)

        row_btn = BoxLayout(orientation="horizontal", size_hint=(1, None), height=dp(44), spacing=dp(10))
        self._btn_back = Button(text="Volver")
        self._btn_save = Button(text="Guardar")
        row_btn.add_widget(self._btn_back)
        row_btn.add_widget(self._btn_save)
        panel.add_widget(row_btn)

        self._btn_back.bind(on_release=lambda *a: self._go_back())
        self._btn_save.bind(on_release=lambda *a: self._save())
        self._btn_auto.bind(on_release=lambda *a: self._set_mode("auto"))
        self._btn_pc.bind(on_release=lambda *a: self._set_mode("pc"))
        self._btn_android.bind(on_release=lambda *a: self._set_mode("android"))

        self.add_widget(root)
        self._sync_from_config()
        self._reflow()

    def _reflow(self):
        if self._body:
            W = Window.width
            H = Window.height
            TOP_H = dp(52)
            body_h = max(H - TOP_H - dp(6), dp(10))
            self._body.size = (W, body_h)
            self._body.pos = (0, 0)

            if self._tb:
                self._tb.pos = (0, H - TOP_H)
            if self._title:
                self._title.pos = (dp(20), H - TOP_H + dp(6))
            if self._btn_back:
                self._btn_back.pos = (W - dp(130), H - TOP_H + dp(8))
            if self._toast:
                self._toast.pos = (W/2 - self._toast.width/2, dp(14))
            return

        if not hasattr(self, "_panel"):
            return
        W = Window.width
        H = Window.height
        pw = min(dp(640), W - dp(40))
        ph = min(dp(320), H - dp(40))
        self._panel.size = (pw, ph)
        self._panel.pos = (W/2 - pw/2, H/2 - ph/2)

    def apply_theme(self):
        try:
            self._bg_col.rgba = BG
        except Exception:
            pass
        try:
            if hasattr(self, "_tb_col"):
                self._tb_col.rgba = BG
        except Exception:
            pass
        if self._body:
            try:
                self._left_col.a = 0.20 if _get_app_config().get("dark_mode") else 0.55
                self._right_col.a = 0.20 if _get_app_config().get("dark_mode") else 0.55
                self._title.color = DARK
            except Exception:
                pass
            self._select_cat(self._cat)
            return
        self._sync_from_config()

    def _toast_msg(self, msg):
        if not self._toast:
            return
        self._toast.text = msg
        self._toast.opacity = 1
        Animation(opacity=0, duration=1.0).start(self._toast)

    def _select_cat(self, cat):
        if not self._body:
            return
        self._cat = cat
        for k, b in (self._cat_buttons or {}).items():
            active = (k == cat)
            b.background_color = (0.05, 0.72, 0.90, 1) if active else (0.25, 0.25, 0.25, 1)
            b.color = (1, 1, 1, 1)
        self._build_detail(cat)

    def _build_detail(self, cat):
        if not self._right:
            return
        self._right.clear_widgets()

        def header(text):
            self._right.add_widget(Label(text=text, font_size=dp(16), bold=True, color=DARK,
                                         size_hint=(1, None), height=dp(28)))

        def row_button(text, on_press):
            b = Button(text=text, size_hint=(1, None), height=dp(42))
            b.bind(on_release=lambda *a: on_press())
            self._right.add_widget(b)
            return b

        def row_toggle(text, value, on_change):
            row = BoxLayout(orientation="horizontal", size_hint=(1, None), height=dp(38), spacing=dp(10))
            row.add_widget(Label(text=text, font_size=dp(13), color=DARK, size_hint=(1, 1)))
            cb = CheckBox(active=bool(value), size_hint=(None, None), size=(dp(28), dp(28)))
            cb.bind(active=lambda inst, v: on_change(bool(v)))
            row.add_widget(cb)
            self._right.add_widget(row)
            return cb

        def row_slider(text, value_0_1, on_change):
            box = BoxLayout(orientation="vertical", size_hint=(1, None), height=dp(70), spacing=dp(4))
            box.add_widget(Label(text=text, font_size=dp(13), color=DARK, size_hint=(1, None), height=dp(20)))
            sld = Slider(min=0.0, max=1.0, value=float(value_0_1), step=0.01, size_hint=(1, None), height=dp(36))
            sld.bind(value=lambda inst, v: on_change(float(v)))
            box.add_widget(sld)
            self._right.add_widget(box)
            return sld

        cfg = _get_app_config()

        if cat == "internet":
            header("Internet")

            def _wifi_toggle(v):
                app = App.get_running_app()
                if not app:
                    return
                if app.set_system_toggle("wifi", v):
                    app.config_data["wifi_enabled"] = bool(v)
                else:
                    self._toast_msg("No se puede cambiar Wi‑Fi acá. Abriendo ajustes…")
                    self._open_system("wifi")

            row_toggle("Wi‑Fi", bool(cfg.get("wifi_enabled", True)), _wifi_toggle)
            row_button("Abrir ajustes Wi‑Fi del sistema", lambda: self._open_system("wifi"))
            row_button("Abrir ajustes de red", lambda: self._open_system("network"))

        elif cat == "bluetooth":
            header("Bluetooth")

            def _bt_toggle(v):
                app = App.get_running_app()
                if not app:
                    return
                if app.set_system_toggle("bluetooth", v):
                    app.config_data["bluetooth_enabled"] = bool(v)
                else:
                    self._toast_msg("No se puede cambiar Bluetooth acá. Abriendo ajustes…")
                    self._open_system("bluetooth")

            row_toggle("Bluetooth", bool(cfg.get("bluetooth_enabled", False)), _bt_toggle)
            row_button("Abrir ajustes Bluetooth del sistema", lambda: self._open_system("bluetooth"))

        elif cat == "sonido":
            header("Sonido")
            row_button("Abrir ajustes de sonido del sistema", lambda: self._open_system("sound"))

        elif cat == "pantalla":
            header("Pantalla")

            def _br(v):
                app = App.get_running_app()
                if not app:
                    return
                app.config_data["brightness"] = float(v)
                app.set_system_brightness(v)

            row_slider("Brillo", float(cfg.get("brightness", 0.75)), _br)
            row_button("Abrir ajustes de pantalla del sistema", lambda: self._open_system("display"))
            self._right.add_widget(Label(text="Si no cambia, ajustalo desde el sistema.", font_size=dp(12), color=LIGHT,
                                         size_hint=(1, None), height=dp(22)))

        elif cat == "sistema":
            header("Sistema")
            row_button("Abrir ajustes del sistema", lambda: self._open_system("system"))
            row_button("Abrir tema / modo oscuro del sistema", lambda: self._open_system("theme"))

        elif cat == "launcher":
            header("Launcher")
            row_toggle("Modo oscuro del launcher", cfg.get("dark_mode", False), self._set_launcher_dark)
            self._right.add_widget(Label(text="Modo del launcher (Auto/PC/Celular):", font_size=dp(12), color=LIGHT,
                                         size_hint=(1, None), height=dp(22)))
            row = BoxLayout(orientation="horizontal", size_hint=(1, None), height=dp(44), spacing=dp(10))
            self._mode_auto = Button(text="Auto")
            self._mode_pc = Button(text="PC")
            self._mode_android = Button(text="Celular")
            row.add_widget(self._mode_auto)
            row.add_widget(self._mode_pc)
            row.add_widget(self._mode_android)
            self._right.add_widget(row)
            self._mode_auto.bind(on_release=lambda *a: self._set_mode("auto"))
            self._mode_pc.bind(on_release=lambda *a: self._set_mode("pc"))
            self._mode_android.bind(on_release=lambda *a: self._set_mode("android"))
            row_button("Guardar cambios", lambda: self._save())
            self._sync_launcher_mode_buttons()

    def _open_system(self, kind):
        app = App.get_running_app()
        if not app or not hasattr(app, "open_system_settings"):
            self._toast_msg("No se pudo abrir ajustes del sistema.")
            return
        ok = app.open_system_settings(kind)
        if not ok:
            self._toast_msg("Este acceso rápido no está disponible.")

    def _sync_launcher_mode_buttons(self):
        cfg = _get_app_config()
        mode = (cfg.get("force_mode") or "auto").lower()

        def style(btn, active):
            btn.background_color = (0.05, 0.72, 0.90, 1) if active else (0.25, 0.25, 0.25, 1)
            btn.color = (1, 1, 1, 1)

        if hasattr(self, "_mode_auto"):
            style(self._mode_auto, mode == "auto")
        if hasattr(self, "_mode_pc"):
            style(self._mode_pc, mode == "pc")
        if hasattr(self, "_mode_android"):
            style(self._mode_android, mode in ("android", "celular", "mobile"))

    def _set_launcher_dark(self, v):
        app = App.get_running_app()
        if not app:
            return
        app.config_data["dark_mode"] = bool(v)
        self._sync_launcher_mode_buttons()
        # Aplicar en vivo (sin esperar a Guardar)
        apply_theme_from_config()
        try:
            app.refresh_screens()
        except Exception:
            pass

    def _sync_from_config(self):
        cfg = _get_app_config()
        mode = (cfg.get("force_mode") or "auto").lower()
        dark = bool(cfg.get("dark_mode", False))
        self._chk_dark.active = dark

        def _style(btn, active):
            btn.background_color = (0.2, 0.6, 0.95, 1) if active else (0.25, 0.25, 0.25, 1)
            btn.color = (1, 1, 1, 1)

        _style(self._btn_auto, mode == "auto")
        _style(self._btn_pc, mode == "pc")
        _style(self._btn_android, mode in ("android", "celular", "mobile"))

    def _set_mode(self, mode):
        app = App.get_running_app()
        if not app:
            return
        app.config_data["force_mode"] = mode
        if self._body:
            self._sync_launcher_mode_buttons()
        else:
            self._sync_from_config()

    def _save(self):
        app = App.get_running_app()
        if not app:
            return
        if self._body:
            app.save_config()
            apply_theme_from_config()
            app.refresh_screens()
            self._toast_msg("Guardado.")
        else:
            app.config_data["dark_mode"] = bool(self._chk_dark.active)
            app.save_config()
            apply_theme_from_config()
            app.refresh_screens()

    def _go_back(self):
        if self.manager:
            self.manager.current = "home"

# ─────────────────────────────────────────────────────────────────────────────
# BOOT SCREEN
# ─────────────────────────────────────────────────────────────────────────────

class BootScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = FloatLayout()
        with root.canvas.before:
            Color(0, 0, 0, 1)
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda *a: setattr(self._bg, "pos", root.pos),
                  size=lambda *a: setattr(self._bg, "size", root.size))

        # Logo Nintendo Switch central
        W = Window.width
        H = Window.height

        self._logo = Widget(size_hint=(None,None), size=(dp(80), dp(56)),
                            pos_hint={"center_x": 0.5, "center_y": 0.52},
                            opacity=0)
        with self._logo.canvas:
            # Joy-Con izq
            Color(*NRED)
            RoundedRectangle(pos=(self._logo.x, self._logo.y),
                             size=(dp(32), dp(56)), radius=[dp(10), 0, 0, dp(10)])
            # Cuerpo
            Color(0.12, 0.12, 0.12, 1)
            RoundedRectangle(pos=(self._logo.x+dp(32), self._logo.y+dp(8)),
                             size=(dp(16), dp(40)), radius=[dp(4)])
            # Joy-Con der
            Color(*NBLU)
            RoundedRectangle(pos=(self._logo.x+dp(48), self._logo.y),
                             size=(dp(32), dp(56)), radius=[0, dp(10), dp(10), 0])

        self._txt = Label(text="Nintendo Switch", font_size=dp(22), bold=True,
                          color=WHITE, pos_hint={"center_x": 0.5, "center_y": 0.36},
                          opacity=0)

        for w in [self._logo, self._txt]:
            root.add_widget(w)
        self.add_widget(root)

    def on_enter(self):
        Clock.schedule_once(self._anim, 0.3)

    def _anim(self, dt):
        Animation(opacity=1, duration=0.5, t="out_back").start(self._logo)
        Clock.schedule_once(lambda dt: Animation(opacity=1, duration=0.4).start(self._txt), 0.5)
        Clock.schedule_once(self._go, 2.5)

    def _go(self, dt):
        anim = Animation(opacity=0, duration=0.5)
        anim.bind(on_complete=lambda *a: setattr(self.manager, "current", "home"))
        anim.start(self)


# ─────────────────────────────────────────────────────────────────────────────
# APP
# ─────────────────────────────────────────────────────────────────────────────

class SwitchLauncherApp(App):
    title = "Switch Launcher"

    def _config_path(self):
        return os.path.join(self.user_data_dir, "config.json")

    def load_config(self):
        default = {
            "force_mode": "auto",
            "dark_mode": False,
            "wifi_enabled": True,
            "bluetooth_enabled": False,
            "brightness": 0.75,
        }
        try:
            with open(self._config_path(), "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                default.update(data)
        except Exception:
            pass
        self.config_data = default

    def save_config(self):
        try:
            os.makedirs(self.user_data_dir, exist_ok=True)
            with open(self._config_path(), "w", encoding="utf-8") as f:
                json.dump(self.config_data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def refresh_screens(self):
        try:
            for name in ("home", "settings"):
                s = self.root.get_screen(name)
                if hasattr(s, "apply_theme"):
                    s.apply_theme()
        except Exception:
            pass

    def handle_action(self, action, data=None):
        if action == "settings":
            try:
                self.root.current = "settings"
                return True
            except Exception:
                return False
        if action == "quit":
            try:
                self.stop()
                return True
            except Exception:
                return False
        return False

    def open_system_settings(self, kind):
        kind = (kind or "").lower()
        if not kind:
            return False

        if platform.system() == "Windows":
            uri_map = {
                "wifi": "ms-settings:network-wifi",
                "network": "ms-settings:network",
                "bluetooth": "ms-settings:bluetooth",
                "sound": "ms-settings:sound",
                "display": "ms-settings:display",
                "system": "ms-settings:about",
                "theme": "ms-settings:colors",
            }
            uri = uri_map.get(kind)
            if not uri:
                return False
            try:
                os.startfile(uri)
                return True
            except Exception:
                return False

        # Android: atajos a pantallas de ajustes
        if not IS_PC:
            action_map = {
                "wifi": "android.settings.WIFI_SETTINGS",
                "network": "android.settings.WIRELESS_SETTINGS",
                "bluetooth": "android.settings.BLUETOOTH_SETTINGS",
                "sound": "android.settings.SOUND_SETTINGS",
                "display": "android.settings.DISPLAY_SETTINGS",
                "system": "android.settings.SETTINGS",
                "theme": "android.settings.DISPLAY_SETTINGS",
            }
            act = action_map.get(kind)
            if not act:
                return False
            try:
                subprocess.Popen(["am", "start", "-a", act],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
            except Exception:
                return False

        return False

    def set_system_toggle(self, kind, enabled):
        kind = (kind or "").lower()
        enabled = bool(enabled)
        if not kind:
            return False

        # Android: best-effort (puede fallar según versión/permisos)
        if not IS_PC:
            if kind == "wifi":
                cmd = ["svc", "wifi", "enable" if enabled else "disable"]
            elif kind == "bluetooth":
                cmd = ["svc", "bluetooth", "enable" if enabled else "disable"]
            else:
                return False
            try:
                subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
            except Exception:
                return False

        # PC: no intentamos togglear (requiere permisos/varía por hardware). Usar ajustes.
        return False

    def set_system_brightness(self, value_0_1):
        try:
            v = float(value_0_1)
        except Exception:
            return False
        v = max(0.0, min(1.0, v))

        # Android: best-effort (WRITE_SETTINGS suele ser requerido)
        if not IS_PC:
            level = int(round(255 * v))
            try:
                subprocess.Popen(
                    ["settings", "put", "system", "screen_brightness", str(level)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                return True
            except Exception:
                return False

        # PC: no universal
        return False

    def build(self):
        self.load_config()
        apply_theme_from_config()
        sm = ScreenManager(transition=FadeTransition(duration=0.35))
        sm.add_widget(BootScreen(name="boot"))
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(SettingsScreen(name="settings"))
        sm.current = "boot"
        return sm

    def on_start(self):
        try:
            from android.runnable import run_on_ui_thread
            from jnius import autoclass
            View = autoclass("android.view.View")
            @run_on_ui_thread
            def _fs():
                act = autoclass("org.kivy.android.PythonActivity").mActivity
                d = act.getWindow().getDecorView()
                f = (View.SYSTEM_UI_FLAG_FULLSCREEN
                     | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                     | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY)
                d.setSystemUiVisibility(f)
            _fs()
        except Exception:
            pass


if __name__ == "__main__":
    SwitchLauncherApp().run()
