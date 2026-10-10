# settings.py
import pygame
import os

# Window & Rendering Configuration
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
RENDER_WIDTH = 960
RENDER_HEIGHT = 540
FPS = 60

# Directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')

# Game States
STATE_PLAYING = "playing"
STATE_MENU = "menu"
