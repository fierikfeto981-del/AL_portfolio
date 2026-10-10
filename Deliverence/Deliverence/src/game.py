# game.py
import pygame
import sys
import os
from pytmx.util_pygame import load_pygame
from settings import *
from player import Player
from sprites import Tile
from groups import CameraGroup

class Game:
    def __init__(self):
        pygame.init()
        # Window utama (screen fisik)
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("2D Platformer - Step 6: Double Jump & Fixed Camera")
        
        # Canvas internal untuk rendering pixel art
        self.display_surface = pygame.Surface((RENDER_WIDTH, RENDER_HEIGHT))
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Sprite Groups
        self.all_sprites = CameraGroup()
        self.collision_sprites = pygame.sprite.Group()
        self.background_sprites = pygame.sprite.Group()
        
        # State Machine Dasar
        self.state = STATE_PLAYING
        
        # Load Map dan Spawn Entitas
        self.setup_map()

    def setup_map(self):
        tmx_path = os.path.join(ASSETS_DIR, 'image', 'maps', 'forest.tmx')
        try:
            tmx_data = load_pygame(tmx_path)
        except Exception as e:
            print(f"[Game] Gagal memuat peta TMX dari {tmx_path}: {e}")
            tmx_data = None
            
        if tmx_data:
            tile_scale = 2
            scaled_tile_w = tmx_data.tilewidth * tile_scale
            scaled_tile_h = tmx_data.tileheight * tile_scale
            
            self.all_sprites.map_width = tmx_data.width * scaled_tile_w
            self.all_sprites.map_height = tmx_data.height * scaled_tile_h

            for layer in tmx_data.visible_layers:
                if hasattr(layer, 'data'):
                    for x, y, surf in layer.tiles():
                        pos = (x * scaled_tile_w, y * scaled_tile_h)
                        scaled_surf = pygame.transform.scale(surf, (scaled_tile_w, scaled_tile_h))
                        
                        if layer.name in ('ground', 'wood'):
                            groups = (self.all_sprites, self.collision_sprites)
                            Tile(pos, scaled_surf, groups)
                        else:
                            groups = (self.all_sprites, self.background_sprites)
                            Tile(pos, scaled_surf, groups)

            player_pos = (50, 100)
            for obj in tmx_data.objects:
                if obj.name == 'player':
                    player_pos = (obj.x * tile_scale, obj.y * tile_scale)
                    break
                    
            self.player = Player(player_pos, self.all_sprites, self.collision_sprites)
        else:
            self.player = Player((100, 200), self.all_sprites, self.collision_sprites)

    def run(self):
        while self.running:
            # 1. Kalkulasi Delta Time (dt)
            dt = self.clock.tick(FPS) / 1000.0
            if dt > 0.1:
                dt = 0.1

            # 2. Event Loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    # Tangkap penekanan tombol lompat di event loop untuk mencegah double jump instan
                    elif event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                        self.player.jump()

            # 3. Game Logic & Rendering berdasarkan State
            if self.state == STATE_PLAYING:
                # Update Sprites
                self.all_sprites.update(dt)
                
                # Rendering
                self.display_surface.fill((20, 20, 30))
                self.all_sprites.custom_draw(self.player, self.display_surface)

            # 4. Scaling dan Rendering ke Layar Utama
            scaled_surface = pygame.transform.scale(self.display_surface, (WINDOW_WIDTH, WINDOW_HEIGHT))
            self.screen.blit(scaled_surface, (0, 0))
            
            pygame.display.flip()

        pygame.quit()
        sys.exit()
