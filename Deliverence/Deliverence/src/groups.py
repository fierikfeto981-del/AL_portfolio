# groups.py
import pygame
from settings import *

class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.offset = pygame.math.Vector2()
        
        # Batas peta default (akan diperbarui dari game.py saat map dimuat)
        self.map_width = 0
        self.map_height = 0

    def custom_draw(self, player, display_surface):
        # 1. Hitung offset kamera agar pemain berada di tengah layar
        self.offset.x = player.rect.centerx - RENDER_WIDTH / 2
        self.offset.y = player.rect.centery - RENDER_HEIGHT / 2

        # 2. Batasi (Clamp) kamera agar tidak keluar dari batas Peta (Map Boundary)
        # Batas Horizontal
        if self.map_width > RENDER_WIDTH:
            self.offset.x = max(0, min(self.offset.x, self.map_width - RENDER_WIDTH))
        else:
            self.offset.x = 0
            
        # Batas Vertikal
        if self.map_height > RENDER_HEIGHT:
            self.offset.y = max(0, min(self.offset.y, self.map_height - RENDER_HEIGHT))
        else:
            # Jika tinggi map lebih kecil dari layar, tengahkan secara vertikal
            self.offset.y = -(RENDER_HEIGHT - self.map_height) / 2

        # 3. Gambar semua sprite dikurangi offset kamera
        for sprite in self:
            offset_pos = sprite.rect.topleft - self.offset
            display_surface.blit(sprite.image, offset_pos)
