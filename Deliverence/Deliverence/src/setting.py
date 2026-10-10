import pygame
import os
from os import walk
from os.path import join
from pytmx.util_pygame import load_pygame

# ================= KOORDINAT DAN RESOLUSI WINDOW =================
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
DISPLAY_WIDTH, DISPLAY_HEIGHT = 800, 600  # Skala 1x otomatis ke 800x600, menjaga kompatibilitas portrait 420px
TILE_SIZE = 64  # Sinkron dengan Peta dan Fisika Lama
FRAMERATE = 60

# ================= WARNA (COLOR PALETTES) =================
BG_COLOR = '#fcdfcd'
COL_GOLD = (255, 210, 50)
COL_ACCENT = (0, 210, 200)
COL_WHITE = (255, 255, 255)
COL_BLACK = (0, 0, 0)
COL_DARK_GRAY = (30, 30, 30)
COL_RED = (220, 50, 50)

# Mapping kemudahan akses / kompatibilitas dari Kode Lama
SCREEN_WIDTH, SCREEN_HEIGHT = WINDOW_WIDTH, WINDOW_HEIGHT

# ================= PATH DIREKTORI =================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')

# ================= KONSTANTA GAMEPLAY =================
XP_BASE = 100
PLAYER_MAX_HP = 100
PLAYER_ATTACK = 30
MOVE_SPEED = 400  # Menggunakan kecepatan lama agar game platformer berjalan normal
BULLET_COOLDOWN = 1500

# ================= GAME STATE KONSTANTA =================
STATE_INTRO       = "intro"
STATE_MENU        = "menu"
STATE_PLAYING     = "playing"
STATE_PAUSE       = "pause"
STATE_BOSS        = "boss"
STATE_STAGE_CLEAR = "stage_clear"
STATE_SHOP        = "shop"
STATE_GAME_OVER   = "game_over"
STATE_WIN         = "win"
STATE_MAP         = "map"
STATE_DIALOGUE    = "dialogue"
