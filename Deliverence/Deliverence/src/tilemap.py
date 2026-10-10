import pygame
import os

# Konfigurasi ukuran tile dan grid autotiling
TILE_SIZE = 64
ROWS = 15
COLS = 150

NEIGHBOR_MAP = {
    (0, 0, 0, 0): (3, 3), # Isolated
    (0, 0, 1, 0): (3, 2), # Right cap (only left neighbor)
    (0, 0, 0, 1): (3, 0), # Left cap (only right neighbor)
    (1, 0, 0, 0): (2, 3), # Bottom cap (only top neighbor)
    (0, 1, 0, 0): (0, 3), # Top cap (only bottom neighbor)
    (0, 0, 1, 1): (3, 1), # Horizontal center
    (1, 1, 0, 0): (1, 3), # Vertical center
    (0, 1, 1, 0): (0, 2), # Top-Right corner (left & bottom neighbors)
    (0, 1, 0, 1): (0, 0), # Top-Left corner (right & bottom neighbors)
    (1, 0, 1, 0): (2, 2), # Bottom-Right corner (left & top neighbors)
    (1, 0, 0, 1): (2, 0), # Bottom-Left corner (right & top neighbors)
    (0, 1, 1, 1): (0, 1), # Top edge (left, right, bottom neighbors)
    (1, 0, 1, 1): (2, 1), # Bottom edge (left, right, top neighbors)
    (1, 1, 1, 0): (1, 2), # Right edge (left, top, bottom neighbors)
    (1, 1, 0, 1): (1, 0), # Left edge (right, top, bottom neighbors)
    (1, 1, 1, 1): (1, 1), # Solid center
}

def make_stage_map(stage_idx):
    """Membangun layout grid untuk stage terpilih"""
    grid = [['.' for _ in range(COLS)] for _ in range(ROWS)]
    
    if stage_idx == 0:
        # Stage 0: Pantai Reruntuhan - Tanah dasar lebih tebal
        for r in range(12, ROWS):
            for c in range(COLS):
                grid[r][c] = '#'
        
        for r in range(ROWS):
            grid[r][0] = '#'
            grid[r][COLS - 1] = '#'
        
        # Bukit dan rintangan tebal
        structures = [
            (9, 12, 12, 15),   # Bukit 1
            (10, 12, 28, 35),  # Bukit 2
            (8, 12, 45, 52),   # Pilar / Menara
            (10, 12, 60, 75),  # Dataran tinggi
            (9, 12, 85, 95),
            (10, 12, 110, 120),
            (8, 12, 135, 142),
        ]
        for r_top, r_bottom, c_start, c_end in structures:
            for r in range(r_top, r_bottom):
                for c in range(c_start, c_end):
                    if c < COLS:
                        grid[r][c] = '#'
                    
        # Platform melayang
        floating = [
            (6, 8, 24, 32),
            (7, 9, 39, 44),
            (5, 7, 72, 80),
            (6, 8, 125, 132),
        ]
        for r_top, r_bottom, c_start, c_end in floating:
            for r in range(r_top, r_bottom):
                for c in range(c_start, c_end):
                    if c < COLS:
                        grid[r][c] = '#'

    elif stage_idx == 1:
        # Stage 1: Jurang Tengah Laut
        for r in range(12, ROWS):
            for c in range(COLS):
                grid[r][c] = '#'
                
        for r in range(ROWS):
            grid[r][0] = '#'
            grid[r][COLS - 1] = '#'

        # Buat celah-celah besar
        gaps = [(20, 28), (55, 65), (105, 115), (130, 142)]
        for r in range(12, ROWS):
            for start, end in gaps:
                for c in range(start, end):
                    if c < COLS:
                        grid[r][c] = '.'
                    
        blocks = [
            (10, 12, 17, 20),
            (10, 12, 28, 31),
            (9, 12, 50, 55),
            (9, 12, 65, 70),
            (10, 12, 100, 105),
            (10, 12, 115, 120),
        ]
        for r_top, r_bottom, c_start, c_end in blocks:
            for r in range(r_top, r_bottom):
                for c in range(c_start, c_end):
                    if c < COLS:
                        grid[r][c] = '#'
                    
        floating = [
            (8, 10, 22, 26),
            (7, 9, 58, 62),
            (8, 10, 108, 112),
        ]
        for r_top, r_bottom, c_start, c_end in floating:
            for r in range(r_top, r_bottom):
                for c in range(c_start, c_end):
                    if c < COLS:
                        grid[r][c] = '#'

    elif stage_idx == 2:
        # Stage 2: Sarang HyperEnd (Goa)
        for r in range(12, ROWS):
            for c in range(COLS):
                grid[r][c] = '#'
                
        for r in range(ROWS):
            grid[r][0] = '#'
            grid[r][COLS - 1] = '#'
                
        for r in range(0, 3):
            for c in range(COLS):
                grid[r][c] = '#'
                
        pillars = [
            (3, 7, 30, 34),    # Pilar atas
            (10, 12, 30, 34),  # Pilar bawah (celah di r=7,8,9)
            (3, 5, 80, 85),
            (8, 12, 80, 85),
            (3, 8, 140, 145),
        ]
        for r_top, r_bottom, c_start, c_end in pillars:
            for r in range(r_top, r_bottom):
                for c in range(c_start, c_end):
                    if c < COLS:
                        grid[r][c] = '#'
                    
        ledges = [
            (8, 10, 10, 25),
            (6, 8, 45, 60),
            (9, 11, 65, 75),
            (5, 7, 100, 120),
        ]
        for r_top, r_bottom, c_start, c_end in ledges:
            for r in range(r_top, r_bottom):
                for c in range(c_start, c_end):
                    if c < COLS:
                        grid[r][c] = '#'

    else:
        # Stage 3: Void Core (Boss Arena)
        for r in range(11, ROWS):
            for c in range(COLS):
                grid[r][c] = '#'
                
        for r in range(ROWS):
            grid[r][0] = '#'
            grid[r][COLS - 1] = '#'
                
    return grid

class Autotiler:
    """Mengimpor, memotong tileset Mossy, dan merubahnya menjadi sprite."""
    def __init__(self):
        self.tiles = {}
        self._load_tileset()

    def _load_tileset(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, '..', 'assets', 'image', 'tilesets', 'Mossy - TileSet.png')
        if not os.path.isfile(path):
            print(f"[Autotiler] Warning: Tileset Mossy tidak ditemukan di: {path}")
            return
            
        try:
            full_img = pygame.image.load(path).convert_alpha()
            orig_size = 512  # Ukuran potongan grid tileset orisinal adalah 512x512
            for r in range(7):
                for c in range(7):
                    rect = pygame.Rect(c * orig_size, r * orig_size, orig_size, orig_size)
                    sub = full_img.subsurface(rect)
                    scaled = pygame.transform.smoothscale(sub, (TILE_SIZE, TILE_SIZE))
                    self.tiles[(r, c)] = scaled
        except Exception as e:
            print(f"[Autotiler] Gagal memuat tileset image: {e}")

    def get_tile_index(self, grid, r, c):
        if grid[r][c] != '#':
            return None
            
        T = int(grid[r-1][c] == '#') if r > 0 else 0
        B = int(grid[r+1][c] == '#') if r < ROWS - 1 else 1
        L = int(grid[r][c-1] == '#') if c > 0 else 1
        R = int(grid[r][c+1] == '#') if c < COLS - 1 else 1
        
        key = (T, B, L, R)
        
        if key == (1, 1, 1, 1):
            TL = int(grid[r-1][c-1] == '#') if r > 0 and c > 0 else 1
            TR = int(grid[r-1][c+1] == '#') if r > 0 and c < COLS - 1 else 1
            BL = int(grid[r+1][c-1] == '#') if r < ROWS - 1 and c > 0 else 1
            BR = int(grid[r+1][c+1] == '#') if r < ROWS - 1 and c < COLS - 1 else 1
            
            if not TL: return (0, 6) # Top-Left inner corner
            if not TR: return (1, 4) # Top-Right inner corner
            if not BL: return (0, 5) # Bottom-Left inner corner
            if not BR: return (0, 4) # Bottom-Right inner corner
            return (1, 1) # Solid center
            
        return NEIGHBOR_MAP.get(key, (1, 1))
