# player.py
import pygame
import os
from settings import *

def import_folder(path):
    surface_list = []
    if os.path.exists(path):
        for _, __, img_files in os.walk(path):
            sorted_files = sorted(img_files, key=lambda x: int(''.join(filter(str.isdigit, x)) or 0))
            for image_name in sorted_files:
                if image_name.endswith('.png'):
                    full_path = os.path.join(path, image_name)
                    try:
                        image_surf = pygame.image.load(full_path).convert_alpha()
                        surface_list.append(image_surf)
                    except Exception as e:
                        print(f"Gagal memuat {image_name}: {e}")
    return surface_list

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites):
        super().__init__(groups)
        
        # Load Animasi
        self.load_animations()
        self.state = 'idle'
        self.frame_index = 0
        
        # Penyelarasan Kecepatan Animasi (diambil dari konversi Tick-Based 60 FPS Project_Base_OLD)
        # idle: 60 / 20 = 3.0 FPS
        # run:  60 / 8  = 7.5 FPS
        # jump: 60 / 15 = 4.0 FPS
        self.animation_speeds = {
            'idle': 3.0,
            'run': 7.5,
            'jump': 4.0
        }
        self.facing_right = True

        # Set gambar awal
        self.image = self.animations['idle'][0] if self.animations['idle'] else pygame.Surface((32, 48))
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox_rect = self.rect.inflate(-12, -4)
        
        # Pergerakan & Fisika
        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.hitbox_rect.center)
        self.speed = 200
        self.gravity = 1000
        self.jump_speed = -360
        self.on_floor = False
        
        # Mekanik Double Jump
        self.max_jumps = 2
        self.jump_count = 0
        
        # Referensi ke grup sprite tabrakan
        self.collision_sprites = collision_sprites

    def load_animations(self):
        self.animations = {'idle': [], 'run': [], 'jump': []}
        for state in self.animations.keys():
            folder_path = os.path.join(ASSETS_DIR, 'image', 'character', state)
            self.animations[state] = import_folder(folder_path)
            
        for state, frames in self.animations.items():
            if not frames:
                print(f"[Player] Warning: Folder '{state}' kosong. Menggunakan fallback.")
                fallback_surf = pygame.Surface((32, 48))
                fallback_surf.fill((0, 150, 255) if state == 'idle' else (255, 100, 0))
                self.animations[state] = [fallback_surf]

    def input(self):
        keys = pygame.key.get_pressed()
        
        # Input horizontal
        self.direction.x = 0
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction.x = 1
            self.facing_right = True
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction.x = -1
            self.facing_right = False

    def jump(self):
        if self.on_floor:
            self.direction.y = self.jump_speed
            self.on_floor = False
            self.jump_count = 1
        elif self.jump_count < self.max_jumps:
            self.direction.y = self.jump_speed
            self.jump_count += 1

    def get_state(self):
        old_state = self.state
        
        if not self.on_floor:
            self.state = 'jump'
        else:
            if self.direction.x != 0:
                self.state = 'run'
            else:
                self.state = 'idle'
                
        if old_state != self.state:
            self.frame_index = 0

    def animate(self, dt):
        self.get_state()
        frames = self.animations[self.state]
        
        # Ambil kecepatan animasi spesifik berdasarkan state saat ini
        speed = self.animation_speeds.get(self.state, 8.0)
        
        # Increment index frame berdasarkan Delta Time
        self.frame_index += speed * dt
        if self.frame_index >= len(frames):
            if self.state == 'jump':
                self.frame_index = len(frames) - 1
            else:
                self.frame_index = 0
            
        image = frames[int(self.frame_index)]
        
        if not self.facing_right:
            self.image = pygame.transform.flip(image, True, False)
        else:
            self.image = image
            
        self.rect = self.image.get_rect(midbottom=self.hitbox_rect.midbottom)

    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if direction == 'horizontal':
                    if self.direction.x > 0:
                        self.hitbox_rect.right = sprite.rect.left
                        self.pos.x = self.hitbox_rect.centerx
                    elif self.direction.x < 0:
                        self.hitbox_rect.left = sprite.rect.right
                        self.pos.x = self.hitbox_rect.centerx
                
                elif direction == 'vertical':
                    if self.direction.y > 0:
                        self.hitbox_rect.bottom = sprite.rect.top
                        self.pos.y = self.hitbox_rect.centery
                        self.direction.y = 0
                        self.on_floor = True
                        self.jump_count = 0
                    elif self.direction.y < 0:
                        self.hitbox_rect.top = sprite.rect.bottom
                        self.pos.y = self.hitbox_rect.centery
                        self.direction.y = 0

    def move(self, dt):
        # 1. Pergerakan Horizontal
        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox_rect.centerx = round(self.pos.x)
        self.collision('horizontal')
        
        # 2. Pergerakan Vertikal
        if not self.on_floor and self.jump_count == 0:
            self.jump_count = 1
            
        self.on_floor = False
        self.direction.y += self.gravity * dt
        self.pos.y += self.direction.y * dt
        self.hitbox_rect.centery = round(self.pos.y)
        self.collision('vertical')

    def update(self, dt):
        self.input()
        self.move(dt)
        self.animate(dt)
