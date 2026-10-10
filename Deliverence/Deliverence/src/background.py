import pygame
import random
import math
import settings
import os

class Bubble:
    """Gelembung kecil yang naik dari dasar laut."""

    def __init__(self):
        self.reset()

    def reset(self, x=None):
        self.x      = x if x is not None else random.randint(0, settings.SCREEN_WIDTH)
        self.y      = random.randint(settings.SCREEN_HEIGHT, settings.SCREEN_HEIGHT + 100)
        self.radius = random.randint(2, 6)
        self.speed  = random.uniform(0.6, 1.8)
        self.wobble = random.uniform(0, math.pi * 2)
        self.alpha  = random.randint(60, 160)

    def update(self):
        self.y      -= self.speed
        self.wobble += 0.04
        self.x      += math.sin(self.wobble) * 0.5
        if self.y < -10:
            self.reset()

    def draw(self, screen):
        surf = pygame.Surface((self.radius * 2 + 4, self.radius * 2 + 4), pygame.SRCALPHA)
        cx, cy = self.radius + 2, self.radius + 2
        pygame.draw.circle(surf, (150, 220, 255, self.alpha), (cx, cy), self.radius)
        pygame.draw.circle(surf, (200, 240, 255, 80), (cx - 1, cy - 1), max(1, self.radius // 2))
        screen.blit(surf, (int(self.x) - self.radius - 2, int(self.y) - self.radius - 2))

class Background:
    """
    Mengelola background parallax menggunakan gambar dari Underwater_Parallax.
    """

    def __init__(self):
        W, H = settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT
        self._layers = []
        
        # Load parallax images
        base_dir = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.join(base_dir, "..", "assets", "image", "maps", "Underwater_Parallax")
        
        # Define layers and their parallax speeds
        layer_files = [
            ("Sinky_Sub_BG.png", 0.05),
            ("Sinky_Sub_GodRays.png", 0.1),
            ("Sinky_Sub_Ruins_Whale.png", 0.15),
            ("Sinky_Sub_Cliffs.png", 0.25),
            ("Sinky_Sub_CloseRockKelp.png", 0.4)
        ]
        
        for filename, speed in layer_files:
            path = os.path.join(base_path, filename)
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    # Scale from 320x180 to fit H=600 -> W=1067
                    scaled_w = int(img.get_width() * (H / img.get_height()))
                    img = pygame.transform.smoothscale(img, (scaled_w, H))
                    self._layers.append({
                        "surface": img,
                        "width": scaled_w,
                        "speed": speed
                    })
                except Exception as e:
                    print(f"[Background] Gagal load layer {filename}: {e}")

        # Gelembung tetap dipertahankan
        self._bubbles = [Bubble() for _ in range(30)]
        for b in self._bubbles:
            b.y = random.randint(0, settings.SCREEN_HEIGHT)  # distribusi acak awal

    def update(self):
        for b in self._bubbles:
            b.update()

    def set_stage_colors(self, col_top, col_bot):
        """Ubah warna dasar sesuai stage aktif. (Dinonaktifkan karena kita pakai gambar)"""
        pass

    def draw(self, screen, cam_offset, draw_ground=True):
        W, H = settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT

        # Draw parallax layers jika ada
        if self._layers:
            for layer in self._layers:
                img = layer["surface"]
                img_w = layer["width"]
                speed = layer["speed"]
                
                x = -(cam_offset * speed) % img_w
                
                screen.blit(img, (x, 0))
                if x > 0:
                    screen.blit(img, (x - img_w, 0))
                if x + img_w < W:
                    screen.blit(img, (x + img_w, 0))
                if x - img_w > 0:
                    screen.blit(img, (x - 2 * img_w, 0))
        else:
            # Fallback jika gambar parallax tidak ada: isi gradasi warna laut dalam
            for y in range(H):
                # Gradasi biru laut ke hitam
                col_r = max(0, int(10 - 8 * (y / H)))
                col_g = max(0, int(30 - 20 * (y / H)))
                col_b = max(10, int(70 - 45 * (y / H)))
                pygame.draw.line(screen, (col_r, col_g, col_b), (0, y), (W, y))

        # Gelembung (selalu di koordinat layar, tidak ikut kamera)
        for b in self._bubbles:
            b.draw(screen)
