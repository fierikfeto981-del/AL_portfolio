import pygame
import math
import random
import os
from timer import Timer
from settings import WINDOW_WIDTH, WINDOW_HEIGHT

# Konfigurasi Tipe Musuh
ENEMY_TYPES = [
    {
        "name"  : "Enemy1",      # Musuh aktif dari assets/image/enemy/enemy1
        "hp"    : 70,
        "speed" : 110,
        "color" : (50, 255, 100),
        "size"  : (60, 110),     # Mengingat ukuran sprite 21x40 yang akan di scale-up
        "damage": 15,
        "xp"    : 45,
        "aggro_range": 240,
        "attack_range": 60,
        "style" : "ground_melee"
    }
]

# ── SISTEM SPRITE ──
_sprite_cache = {}

def _slice_sheet(path, frame_w, frame_h):
    try:
        sheet = pygame.image.load(path).convert_alpha()
    except Exception as e:
        print(f"[Enemy] Gagal memuat spritesheet {path}: {e}")
        return []
    frames = []
    cols = sheet.get_width() // frame_w
    for c in range(cols):
        frame = sheet.subsurface(pygame.Rect(c * frame_w, 0, frame_w, frame_h))
        bbox = frame.get_bounding_rect()
        if bbox.width > 2 and bbox.height > 2:
            frames.append(frame)
    return frames

def _load_sequence(folder, scale_w, scale_h):
    frames = []
    if not os.path.isdir(folder):
        return frames
    # Load and sort files alphabetically
    files = sorted([f for f in os.listdir(folder) if f.endswith('.png')])
    for f in files:
        path = os.path.join(folder, f)
        try:
            img = pygame.image.load(path).convert_alpha()
            frames.append(img)
        except Exception as e:
            print(f"[Enemy] Gagal load sprite {path}: {e}")
    return frames

def _get_enemy_sprites(name):
    if name in _sprite_cache:
        return _sprite_cache[name]

    base_dir = os.path.dirname(os.path.abspath(__file__))
    enemy_dir = os.path.join(base_dir, "..", "assets", "image", "enemy", name.lower())

    sprites = {}
    if os.path.isdir(enemy_dir):
        # Load from separate folders per animation state (idle, walk, attack, die/dead)
        for state in ["idle", "walk", "attack", "die", "dead"]:
            folder = os.path.join(enemy_dir, state)
            frames = _load_sequence(folder, 60, 110)
            if frames:
                key = "dead" if state == "die" else state
                sprites[key] = frames
        if sprites:
            print(f"[Enemy] Sprite dimuat untuk '{name}': " + ", ".join(f"{k}({len(v)}f)" for k, v in sprites.items()))
        else:
            print(f"[Enemy] Warning: Sprite '{name}' tidak ada frame valid.")
    else:
        print(f"[Enemy] Warning: Folder sprite untuk '{name}' tidak ditemukan di assets/image/enemy/{name.lower()}.")
    
    _sprite_cache[name] = sprites
    return sprites

ANIM_TICK_RATES = {
    "idle": 9,
    "walk": 6,
    "attack": 5,
    "hurt": 8,
    "dead": 7
}

class BaseEnemy(pygame.sprite.Sprite):
    def __init__(self, pos, name, groups, collision_sprites, player, main_rectangle=None):
        super().__init__(groups)
        self.name = name
        self.player = player
        self.collision_sprites = collision_sprites
        self.main_rectangle = main_rectangle

        # Data Setup
        self.data = next(item for item in ENEMY_TYPES if item["name"] == name)
        self.hp = self.data["hp"]
        self.max_hp = self.data["hp"]
        self.speed = self.data["speed"]
        self.damage = self.data["damage"]
        self.color = self.data["color"]
        self.xp = self.data["xp"]
        self.aggro_range = self.data["aggro_range"]
        self.attack_range = self.data.get("attack_range", 60)
        self.shoot_range = self.data.get("shoot_range", 0)
        self.style = self.data["style"]
        
        self.width, self.height = self.data["size"]
        
        # Sprite Animation Setup
        self._sprites = _get_enemy_sprites(self.name)
        self._anim_state = "idle"
        self._anim_idx = 0
        self._anim_tick = 0
        self.flip = False
        
        # State
        self.ai_state = "idle"
        self.direction = pygame.Vector2(0, 0)
        self.vy = 0.0
        self.gravity = 30.0
        
        # Timers & Combat
        self.shoot_cooldown = Timer(1500)
        self.hurt_timer = 0
        self.dying = False
        self.death_timer = None
        self.alive = True
        
        # Hover properties
        self.amplitude = random.randint(30, 60)
        self.frequency = random.randint(300, 500)
        self.start_y = pos[1]
        
        # Setup Initial Surface
        self.image = self._make_surface()
        self.rect = self.image.get_rect(topleft = pos)
        self.mask = pygame.mask.from_surface(self.image)

    # ── FALLBACK GEOMETRIS ──
    def _make_surface(self):
        w, h = self.width, self.height
        surf = pygame.Surface((w, h), pygame.SRCALPHA)

        if self.name == "Crab":
            pygame.draw.ellipse(surf, self.color, (4, h//3, w-8, h*2//3))
            pygame.draw.circle(surf, (0,0,0), (w//3, h//3+2), 3)
            pygame.draw.circle(surf, (0,0,0), (2*w//3, h//3+2), 3)
        elif self.name == "Jellyfish":
            pygame.draw.ellipse(surf, (*self.color, 180), (2, 2, w-4, h//2))
        elif self.name == "Shark":
            pygame.draw.ellipse(surf, self.color, (0, h//4, w, h//2))
            pygame.draw.circle(surf, (10,10,10), (12, h//2-2), 4)

        return surf

    def _get_current_frame(self):
        frames = self._sprites.get(self._anim_state)
        if not frames:
            frames = self._sprites.get("idle")
        if not frames:
            return None
        return frames[self._anim_idx % len(frames)]

    def _update_animation(self):
        tick_rate = ANIM_TICK_RATES.get(self._anim_state, 8)
        self._anim_tick += 1
        
        if self._anim_tick >= tick_rate:
            self._anim_tick = 0
            self._anim_idx += 1
            
            frames = self._sprites.get(self._anim_state, [])
            if frames:
                if self._anim_state == "dead":
                    if self._anim_idx >= len(frames):
                        self._anim_idx = len(frames) - 1
                elif self._anim_state == "hurt" or self._anim_state == "attack":
                    # Khusus attack, tembak proyektil atau beri damage melee pada frame tertentu
                    if self._anim_state == "attack" and self._anim_idx == len(frames) // 2:
                        if self.style == "ground_ranged":
                            dist_x = self.player.rect.centerx - self.rect.centerx
                            dist_y = self.player.rect.centery - self.rect.centery
                            self.shoot_projectile(dist_x, dist_y)
                        elif self.style == "ground_melee":
                            # Cek jarak untuk damage melee
                            dist_x = self.player.rect.centerx - self.rect.centerx
                            dist_y = self.player.rect.centery - self.rect.centery
                            if math.hypot(dist_x, dist_y) < self.attack_range + 20:
                                self.player.take_damage(self.damage)
                                
                    if self._anim_idx >= len(frames):
                        self._anim_idx = 0
                        if self._anim_state == "attack":
                            self._anim_state = "idle" # Kembali ke idle/walk setelah serang
                else:
                    self._anim_idx %= len(frames)

    def _render_sprite(self):
        frame = self._get_current_frame()
        if frame:
            orig_w, orig_h = frame.get_size()
            scale_h = self.height
            scale_w = int(orig_w * (scale_h / orig_h))
            scaled = pygame.transform.scale(frame, (scale_w, scale_h))
            
            if self.flip:
                scaled = pygame.transform.flip(scaled, True, False)
                
            # Efek hurt kedip
            if self.hurt_timer > 0 and (self.hurt_timer // 3) % 2 == 0:
                white = scaled.copy()
                white.fill((255, 255, 255, 120), special_flags=pygame.BLEND_RGBA_ADD)
                scaled = white
                
            # Efek mati perlahan menghilang
            if self.dying:
                fade = scaled.copy()
                fade.fill((100, 0, 0, 80), special_flags=pygame.BLEND_RGBA_ADD)
                scaled = fade
                
            # Padding untuk menyesuaikan dengan rect fisika enemy
            surf_w = max(self.width, scale_w)
            padded = pygame.Surface((surf_w, self.height), pygame.SRCALPHA)
            draw_x = surf_w // 2 - scale_w // 2
            draw_y = self.height - scale_h
            padded.blit(scaled, (draw_x, draw_y))
            self.image = padded
        else:
            surf = self._make_surface()
            if self.flip:
                surf = pygame.transform.flip(surf, True, False)
            self.image = surf

        self.mask = pygame.mask.from_surface(self.image)

    def take_damage(self, amount):
        if self.dying:
            return
        self.hp -= amount
        
        # Paksa aggro kalau dipukul dari jauh
        if self.ai_state == "idle":
            self.ai_state = "chase"
            
        if self.hp <= 0:
            self.hp = 0
            self.dying = True
            self.speed = 0
            self._anim_state = "dead"
            self._anim_idx = 0
            
            # Jika punya animasi dead, hapus setelah sekian ms, jika tidak langsung hapus
            delay = 500
            if "dead" in self._sprites:
                frames = len(self._sprites["dead"])
                delay = frames * ANIM_TICK_RATES["dead"] * 16 # roughly 16ms per pygame tick
                
            self.death_timer = Timer(delay, autostart=True, func=self.kill)
        else:
            self.hurt_timer = 15
            self._anim_state = "hurt"
            self._anim_idx = 0

    def update(self, dt):
        if self.dying:
            if self.death_timer:
                self.death_timer.update()
            self._update_animation()
            self._render_sprite()
            return

        if self.hurt_timer > 0:
            self.hurt_timer -= 1
            if self.hurt_timer == 0 and self._anim_state == "hurt":
                self._anim_state = "idle"

        self.shoot_cooldown.update()

        dist_x = self.player.rect.centerx - self.rect.centerx
        dist_y = self.player.rect.centery - self.rect.centery
        dist = math.hypot(dist_x, dist_y)

        # ── AGGRO LOGIC ──
        if dist < self.aggro_range:
            self.ai_state = "chase"
        else:
            self.ai_state = "idle"

        if self.ai_state == "idle":
            self.direction.x = 0
            if self._anim_state not in ["hurt", "attack"]:
                self._anim_state = "idle"
        elif self.ai_state == "chase":
            self.direction.x = 1 if dist_x > 0 else -1
            self.flip = self.direction.x > 0
            
            if self._anim_state not in ["hurt", "attack"]:
                self._anim_state = "walk"
                
            # Logika serangan untuk tipe ranged
            if self.style == "ground_ranged" and dist < self.shoot_range:
                self.direction.x = 0 # Berhenti untuk menembak
                if not self.shoot_cooldown:
                    self._anim_state = "attack"
                    self._anim_idx = 0
                    self.shoot_cooldown.activate()
            # Logika serangan untuk tipe melee darat
            elif self.style == "ground_melee" and dist < self.attack_range:
                self.direction.x = 0 # Berhenti untuk memukul
                if not self.shoot_cooldown: # Gunakan shoot_cooldown sebagai attack cooldown
                    self._anim_state = "attack"
                    self._anim_idx = 0
                    self.shoot_cooldown.activate()
            # Logika serangan untuk tipe hover (karena tidak ada animasi serang, kita buat dia dash)
            elif self.style == "hover_melee" and dist < self.attack_range:
                if not self.shoot_cooldown:
                    # Dash attack effect
                    self.direction.x = (1 if dist_x > 0 else -1) * 3
                    self.shoot_cooldown.activate()

        # ── MOVEMENT & COLLISION ──
        if self.style == "hover_melee":
            # Terbang mengejar kalau aggro, melayang diam kalau idle
            if self.ai_state == "chase":
                # Jika sedang dash cooldown awal, speed lebih cepat
                elapsed = pygame.time.get_ticks() - getattr(self.shoot_cooldown, 'start_time', 0)
                current_speed = self.speed * 2.5 if getattr(self.shoot_cooldown, 'active', False) and elapsed < 300 else self.speed
                self.rect.x += self.direction.x * current_speed * dt
                self.collision('horizontal')
                # Kejar secara vertikal perlahan
                self.direction.y = 1 if dist_y > 0 else -1
                self.rect.y += self.direction.y * (current_speed * 0.5) * dt
                self.collision('vertical')
                self.start_y = self.rect.y # update titik tengah hover
            else:
                # Melayang di tempat
                self.rect.y = self.start_y + math.sin(pygame.time.get_ticks() / self.frequency) * self.amplitude
        else:
            # Gerak darat
            self.rect.x += self.direction.x * self.speed * dt
            self.collision('horizontal')
            
            self.vy += self.gravity * dt
            self.rect.y += self.vy
            self.collision('vertical')

        self._update_animation()
        self._render_sprite()

    def shoot_projectile(self, dx, dy):
        from sprites import Bullet
        bullet_surf = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.circle(bullet_surf, (200, 60, 255), (6, 6), 6)
        
        dir_vec = pygame.Vector2(dx, dy)
        if dir_vec.length() > 0:
            dir_vec = dir_vec.normalize()
        else:
            dir_vec = pygame.Vector2(1 if self.flip else -1, 0)
            
        Bullet(bullet_surf, self.rect.center, dir_vec, (self.groups()[0], self.player.collision_sprites), mode="boss")

    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.rect):
                if direction == 'horizontal':
                    if self.direction.x > 0:
                        self.rect.right = sprite.rect.left
                        self.direction.x = 0
                    elif self.direction.x < 0:
                        self.rect.left = sprite.rect.right
                        self.direction.x = 0
                elif direction == 'vertical':
                    if self.vy > 0:
                        self.rect.bottom = sprite.rect.top
                        self.vy = 0
                    elif self.vy < 0:
                        self.rect.top = sprite.rect.bottom
                        self.vy = 0


# BossEnemy dibiarkan menggunakan bentuk geometris sesuai sebelumnya (Deep Sea Warden / Void Core)
class BossEnemy(pygame.sprite.Sprite):
    def __init__(self, pos, name, groups, collision_sprites, player):
        super().__init__(groups)
        self.name = name
        self.player = player
        self.collision_sprites = collision_sprites
        
        self.hp = 1200
        self.max_hp = 1200
        self.speed = 120
        self.damage = 35
        self.color = (200, 0, 255)
        self.xp = 1000
        self.phase = 1
        self.stage_idx = 2
        
        self.width, self.height = 96, 96
        self.image = self._make_surface()
        self.rect = self.image.get_rect(center = pos)
        
        self.direction = pygame.Vector2()
        self.shoot_timer = Timer(1200, autostart=True)
        self.bullet_surf = pygame.Surface((18, 18), pygame.SRCALPHA)
        pygame.draw.circle(self.bullet_surf, (255, 60, 60), (9, 9), 9)

        self.ai_state = "idle"
        self.action_timer = Timer(2000, autostart=True)
        self.bullets_fired = 0
        self.dying = False
        self.death_timer = None
        self.mask = pygame.mask.from_surface(self.image)

    def _make_surface(self):
        w, h = self.width, self.height
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        
        pygame.draw.ellipse(surf, self.color, (12, 12, w-24, h-24))
        pygame.draw.ellipse(surf, (0, 0, 0), (w//4, h//3, w//2, h//3))
        
        eye_color = (0, 255, 200) if self.phase == 1 else ((255, 150, 0) if self.phase == 2 else (255, 0, 80))
        pygame.draw.circle(surf, eye_color, (w//2, h//2), 12)
        pygame.draw.circle(surf, (255, 255, 255), (w//2 - 3, h//2 - 3), 3)
        
        for i in range(8):
            angle = i * (math.pi / 4)
            x1 = w//2 + int(math.cos(angle) * (w//2 - 12))
            y1 = h//2 + int(math.sin(angle) * (h//2 - 12))
            x2 = w//2 + int(math.cos(angle) * (w//2))
            y2 = h//2 + int(math.sin(angle) * (h//2))
            pygame.draw.line(surf, (150, 0, 180), (x1, y1), (x2, y2), 4)

        return surf

    def take_damage(self, amount):
        if self.dying:
            return
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.dying = True
            self.speed = 0
            
            # Efek Siluet Putih (Silhouette Death Effect)
            self.image = self._make_surface()
            mask = pygame.mask.from_surface(self.image)
            self.image = mask.to_surface(setcolor=(255, 255, 255), unsetcolor=(0, 0, 0))
            self.image.set_colorkey((0, 0, 0))
            self.death_timer = Timer(200, autostart=True, func=self.kill)
            return
            
        if self.hp > 800:
            self.phase = 1
        elif 400 < self.hp <= 800:
            if self.phase == 1:
                self.phase = 2
                self.speed = 180
                self.shoot_timer.duration = 800
        else:
            if self.phase == 2:
                self.phase = 3
                self.speed = 240
                self.shoot_timer.duration = 400

    def update(self, dt):
        if self.dying:
            if self.death_timer:
                self.death_timer.update()
            return

        self.shoot_timer.update()
        self.action_timer.update()
        
        dist_x = self.player.rect.centerx - self.rect.centerx
        dist_y = self.player.rect.centery - self.rect.centery
        dist = math.hypot(dist_x, dist_y)
        
        if not self.action_timer:
            states = ["charge", "orbit", "shoot"]
            self.ai_state = random.choice(states)
            self.action_timer = Timer(random.randint(1500, 3000), autostart=True)
            self.bullets_fired = 0
            
        if self.ai_state == "charge":
            if dist > 0:
                self.direction = pygame.Vector2(dist_x, dist_y).normalize()
            else:
                self.direction = pygame.Vector2()
        elif self.ai_state == "orbit":
            if dist > 0:
                dir_to_player = pygame.Vector2(dist_x, dist_y).normalize()
                self.direction = pygame.Vector2(-dir_to_player.y, dir_to_player.x)
            else:
                self.direction = pygame.Vector2()
        else:
            self.direction = pygame.Vector2()
            
        if not self.shoot_timer and dist < 600:
            dir_to_player = pygame.Vector2(dist_x, dist_y)
            if dir_to_player.length() > 0:
                from sprites import Bullet
                Bullet(self.bullet_surf, self.rect.center, dir_to_player, self.groups(), mode="boss")
            self.shoot_timer.activate()
            
        self.rect.x += self.direction.x * self.speed * dt
        self.collision('horizontal')
        self.rect.y += self.direction.y * self.speed * dt
        self.collision('vertical')
        
        self.image = self._make_surface()
        self.mask = pygame.mask.from_surface(self.image)

    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.rect):
                if direction == 'horizontal':
                    if self.direction.x > 0:
                        self.rect.right = sprite.rect.left
                    elif self.direction.x < 0:
                        self.rect.left = sprite.rect.right
                elif direction == 'vertical':
                    if self.direction.y > 0:
                        self.rect.bottom = sprite.rect.top
                    elif self.direction.y < 0:
                        self.rect.top = sprite.rect.bottom
