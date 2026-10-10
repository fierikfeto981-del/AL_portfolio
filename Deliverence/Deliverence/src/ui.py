# ============================================================
#  src/ui.py — HUD, Menu, Game Over, Intro, Stage Clear (Full RPG)
# ============================================================

import pygame
import math
import settings

def _load_font(size, bold=False):
    try:    return pygame.font.SysFont("Segoe UI", size, bold=bold)
    except: return pygame.font.SysFont("Arial",    size, bold=bold)

class UI:
    INTRO_LINES = [
        "Sebuah dunia yang damai...",
        "Hancur oleh Lord HyperEnd.",
        "Hasumi — gadis remaja yang terdistorsi",
        "ruang dan waktu bersama reruntuhan dunianya,",
        "terdampar di kedalaman laut yang asing.",
        "",
        "Ia harus bertahan.",
        "Ia harus melawan.",
        "Ia harus menemukan jalan pulang.",
    ]

    def __init__(self):
        self._font_sm    = _load_font(18)
        self._font_md    = _load_font(24, bold=True)
        self._font_lg    = _load_font(42, bold=True)
        self._font_xl    = _load_font(68, bold=True)
        self._font_story = _load_font(21)
        self._font_hud   = _load_font(17, bold=True)

        # Intro typewriter
        self._intro_line  = 0
        self._intro_char  = 0
        self._intro_timer = 0
        self._intro_done  = False
        self._intro_hold  = 0

        # Menu & misc
        self._menu_tick   = 0
        self._lv_notif    = ""
        self._lv_timer    = 0

    # ── HUD ───────────────────────────────────────────────────
    def draw_hud(self, screen, player, score, stage, skill_manager):
        W = settings.SCREEN_WIDTH

        # Panel kiri
        panel = pygame.Surface((230, 155), pygame.SRCALPHA)
        panel.fill((0, 10, 30, 160))
        pygame.draw.rect(panel, (0, 160, 200, 80), panel.get_rect(), 1)
        screen.blit(panel, (8, 8))

        # HP bar
        self._draw_bar(screen, 18, 16, 200, 13,
                       player.hp, player.max_hp,
                       (220, 40, 60), (30, 10, 10), label="HP")
        # WP bar
        wp_col = (80, 160, 255) if not player._wp_exhausted else (255, 100, 60)
        self._draw_bar(screen, 18, 38, 200, 10,
                       player.wp, player.max_wp,
                       wp_col, (10, 15, 40), label="WP")

        # XP bar
        self._draw_bar(screen, 18, 56, 200, 7,
                       player.xp, player.xp_to_lv,
                       (80, 220, 255), (10, 20, 50))

        # Stats
        lv  = self._font_hud.render(f"Lv.{player.level}  ⚔{player.attack}  🪙{player.gold}", True, settings.COL_GOLD)
        screen.blit(lv, (18, 70))
        sc  = self._font_hud.render(f"Score: {score}", True, (180, 210, 240))
        screen.blit(sc, (18, 92))

        # Stage info
        if stage:
            st = self._font_hud.render(
                f"Stage {stage.index+1}: {stage.name}  |  Kill: {stage.kill_count}/{stage.kill_target}",
                True, (120, 200, 240))
            screen.blit(st, (18, 114))

            # Kill progress bar
            self._draw_bar(screen, 18, 134, 200, 6,
                           stage.kill_count, stage.kill_target,
                           (0, 220, 180), (20, 40, 30))

        # WP Exhausted warning
        if player._wp_exhausted:
            w = int(math.sin(pygame.time.get_ticks() * 0.01) * 3)
            ws = self._font_md.render("⚠ KELELAHAN ⚠", True, (255, 100, 0))
            screen.blit(ws, (W//2 - ws.get_width()//2, 8 + w))

        # Skill HUD (pojok kanan atas)
        if skill_manager:
            self._draw_skill_hud(screen, skill_manager, player)

        # Level Up notif
        self.draw_level_up(screen)

        # Kontrol hint
        hints = ["←→/AD Gerak", "W/Spasi Lompat", "Z Tembak  X/C/V Skill"]
        for i, h in enumerate(hints):
            hs = self._font_sm.render(h, True, (70, 100, 130))
            screen.blit(hs, (W - 210, settings.SCREEN_HEIGHT - 56 + i*18))

    def _draw_bar(self, screen, x, y, w, h, val, max_val, col_fill, col_bg, label=""):
        ratio = max(0, val / max_val) if max_val > 0 else 0
        pygame.draw.rect(screen, col_bg,   (x, y, w, h))
        pygame.draw.rect(screen, col_fill, (x, y, int(w*ratio), h))
        pygame.draw.rect(screen, (100,100,100), (x, y, w, h), 1)
        if label:
            ls = self._font_sm.render(label, True, (200,200,200))
            screen.blit(ls, (x + 1, y - 1))

    def _draw_skill_hud(self, screen, skill_manager, player):
        import pygame
        W    = settings.SCREEN_WIDTH
        keys = ["X", "C", "V", "B"]
        sx   = W - 210
        sy   = 8
        for i, skill in enumerate(skill_manager.skills):
            if not skill.unlocked:
                continue
            bx = sx + i * 52
            # Kotak skill
            box = pygame.Surface((46, 46), pygame.SRCALPHA)
            if skill.ready:
                box.fill((0, 40, 60, 200))
                pygame.draw.rect(box, skill.COLOR + (200,), box.get_rect(), 2)
            else:
                box.fill((10, 10, 20, 200))
                pygame.draw.rect(box, (60, 60, 80, 150), box.get_rect(), 2)
                # Cooldown overlay
                cd_ratio = getattr(skill, 'cd_ratio', 1.0)
                cd_h = int(46 * (1 - cd_ratio))
                overlay = pygame.Surface((46, cd_h), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 140))
                box.blit(overlay, (0, 0))
            screen.blit(box, (bx, sy))
            # Nama pendek
            short = skill.NAME.split()[0][:4]
            ns = self._font_sm.render(short, True, (200,220,240) if skill.ready else (80,80,100))
            screen.blit(ns, (bx + 2, sy + 3))
            # Tombol
            ks = self._font_sm.render(f"[{keys[i]}]", True, (140,160,180))
            screen.blit(ks, (bx + 2, sy + 26))
            # WP cost
            if skill.WP_COST > 0:
                wc = self._font_sm.render(f"{skill.WP_COST}wp", True, (80,140,255))
                screen.blit(wc, (bx + 2, sy + 42))

    # ── Boss HP Bar ───────────────────────────────────────────
    def draw_boss_bar(self, screen, boss):
        W   = settings.SCREEN_WIDTH
        bw  = W - 80
        bx  = 40
        by  = settings.SCREEN_HEIGHT - 48

        label_col = (200, 0, 255)
        prefix = "☠ "

        panel = pygame.Surface((bw + 20, 38), pygame.SRCALPHA)
        panel.fill((20, 0, 40, 200) if "Warden" in boss.name else (10, 15, 30, 200))
        pygame.draw.rect(panel, label_col + (120,), panel.get_rect(), 2)
        screen.blit(panel, (bx - 10, by - 6))

        label = self._font_md.render(f"{prefix}{boss.name.upper()}", True, label_col)
        screen.blit(label, (bx, by - 4))

        ratio = boss.hp / boss.max_hp
        pygame.draw.rect(screen, (30, 10, 20) if "Warden" in boss.name else (15, 20, 30), (bx, by + 14, bw, 16))
        
        col = label_col if ratio > 0.3 else (255, 0, 80)
        pygame.draw.rect(screen, col, (bx, by + 14, int(bw*ratio), 16))
        pygame.draw.rect(screen, label_col, (bx, by + 14, bw, 16), 2)

        if getattr(boss, 'stage_idx', 2) >= 2:
            ph_col = [(0, 200, 200), (255, 160, 0), (255, 0, 80)][boss.phase - 1]
            ph = self._font_sm.render(f"Phase {boss.phase}", True, ph_col)
        else:
            ph = self._font_sm.render("MINI-BOSS", True, label_col)
        screen.blit(ph, (bx + bw - ph.get_width() - 4, by + 16))

    # ── Level Up ─────────────────────────────────────────────
    def show_level_up(self, level):
        self._lv_notif = f"✦ LEVEL UP!  Lv.{level} ✦"
        self._lv_timer = 120

    def draw_level_up(self, screen):
        if self._lv_timer > 0:
            self._lv_timer -= 1
            w = settings.SCREEN_WIDTH
            h = settings.SCREEN_HEIGHT
            # Efek bouncing sinusoidal
            float_y = 120 + int(math.sin(self._lv_timer * 0.15) * 8)
            alpha = min(255, self._lv_timer * 4)
            
            surf = pygame.Surface((w, 50), pygame.SRCALPHA)
            txt = self._font_lg.render(self._lv_notif, True, (255, 220, 0))
            txt.set_alpha(alpha)
            
            # Glow shadow
            sh = self._font_lg.render(self._lv_notif, True, (0,0,0))
            sh.set_alpha(alpha)
            
            surf.blit(sh, (w//2 - txt.get_width()//2 + 2, float_y - 120 + 2))
            surf.blit(txt, (w//2 - txt.get_width()//2, float_y - 120))
            screen.blit(surf, (0, float_y))

    # ── Intro Typewriter Screen ──────────────────────────────
    def update_intro(self):
        if self._intro_done:
            return
        self._intro_timer += 1
        if self._intro_timer >= 3:  # kecepatan ketik
            self._intro_timer = 0
            lines = self.INTRO_LINES
            if self._intro_line < len(lines):
                target_line = lines[self._intro_line]
                if self._intro_char < len(target_line):
                    self._intro_char += 1
                else:
                    self._intro_hold += 1
                    if self._intro_hold >= 30:  # waktu jeda antar baris
                        self._intro_line += 1
                        self._intro_char = 0
                        self._intro_hold = 0
            else:
                self._intro_done = True

    def draw_intro(self, screen):
        W, H = settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT
        screen.fill((2, 6, 18))
        
        # Grid neon redup
        for x in range(0, W, 80):
            pygame.draw.line(screen, (5, 15, 30), (x, 0), (x, H))
        for y in range(0, H, 80):
            pygame.draw.line(screen, (5, 15, 30), (0, y), (W, y))

        lines = self.INTRO_LINES
        start_y = H // 2 - 140
        
        # Render baris teks yang sudah diketik
        for i in range(self._intro_line):
            ts = self._font_story.render(lines[i], True, (150, 180, 200))
            screen.blit(ts, (W//2 - ts.get_width()//2, start_y + i * 28))
            
        # Render baris teks aktif yang sedang diketik
        if self._intro_line < len(lines):
            active_text = lines[self._intro_line][:self._intro_char]
            # Cursor berkedip di akhir kata
            cursor = "|" if (pygame.time.get_ticks() // 200) % 2 == 0 else ""
            ts = self._font_story.render(active_text + cursor, True, (255, 255, 255))
            screen.blit(ts, (W//2 - ts.get_width()//2, start_y + self._intro_line * 28))

        if self._intro_done:
            hint_y = H - 80 + int(math.sin(pygame.time.get_ticks() * 0.008) * 3)
            hint = self._font_sm.render("TEKAN [ ENTER ] UNTUK MELANJUTKAN", True, (0, 255, 200))
            screen.blit(hint, (W//2 - hint.get_width()//2, hint_y))
        else:
            hint = self._font_sm.render("[ ENTER ] SKIP", True, (60, 80, 100))
            screen.blit(hint, (W - hint.get_width() - 40, H - 40))

    # ── Menu Utama ───────────────────────────────────────────
    def draw_menu(self, screen, has_save=False):
        self._menu_tick += 1
        W, H = settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT
        screen.fill((4, 10, 24))

        # Efek grid bergerak
        offset = int(self._menu_tick * 0.5) % 40
        for x in range(offset, W, 40):
            pygame.draw.line(screen, (8, 20, 45), (x, 0), (x, H))
        for y in range(0, H, 40):
            pygame.draw.line(screen, (8, 20, 45), (0, y), (W, y))

        # Floating title
        title_y = H // 2 - 130 + int(math.sin(self._menu_tick * 0.04) * 10)
        
        # Glow title
        for size in (6, 4, 2):
            ts_glow = self._font_xl.render("VOID MERMAID", True, (0, 100, 255, 50))
            screen.blit(ts_glow, (W//2 - ts_glow.get_width()//2, title_y - size))
            
        title = self._font_xl.render("VOID MERMAID", True, (255, 255, 255))
        screen.blit(title, (W//2 - title.get_width()//2, title_y))

        sub = self._font_sm.render("HASUMI AND THE SHATTERED CORES", True, (0, 220, 220))
        screen.blit(sub, (W//2 - sub.get_width()//2, title_y + 80))

        # Options
        options = [
            "[ ENTER ]  MULAI PETUALANGAN BARU",
            "[ L ]  LANJUTKAN SAVE DATA" if has_save else "[ L ]  LANJUTKAN SAVE DATA (KOSONG)",
            "[ ESC ]  KELUAR DARI GAME"
        ]

        for i, opt in enumerate(options):
            col = (200, 220, 255)
            if i == 1 and not has_save:
                col = (60, 75, 90)
            ts = self._font_md.render(opt, True, col)
            screen.blit(ts, (W//2 - ts.get_width()//2, H//2 + 40 + i * 36))

        hint = self._font_sm.render("Tugas Akhir Pemrograman Berorientasi Objek (PBO)", True, (80, 100, 120))
        screen.blit(hint, (W//2 - hint.get_width()//2, H - 40))

    # ── Game Over Screen ──────────────────────────────────────
    def draw_game_over(self, screen, score, kill_count, level):
        W, H = settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT
        
        # Red overlay
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((40, 5, 5, 220))
        screen.blit(overlay, (0, 0))

        title = self._font_xl.render("GAME OVER", True, (255, 40, 60))
        screen.blit(title, (W//2 - title.get_width()//2, H//2 - 140))

        stats = [
            f"Level Karakter: {level}",
            f"Monster Dikalahkan: {kill_count}",
            f"Skor Akhir: {score}"
        ]

        for i, s in enumerate(stats):
            ts = self._font_md.render(s, True, (240, 200, 200))
            screen.blit(ts, (W//2 - ts.get_width()//2, H//2 - 20 + i * 30))

        hint_y = H - 120 + int(math.sin(pygame.time.get_ticks() * 0.008) * 4)
        hint = self._font_md.render("TEKAN  [ R ]  UNTUK RETRY  |  [ M ]  MENU UTAMA", True, (255, 200, 0))
        screen.blit(hint, (W//2 - hint.get_width()//2, hint_y))

    # ── Win Ending Screen ─────────────────────────────────────
    def draw_win(self, screen, score, kill_count, level):
        W, H = settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT
        
        # Green-blue victory overlay
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((5, 30, 25, 230))
        screen.blit(overlay, (0, 0))

        title = self._font_xl.render("VICTORY!", True, (0, 255, 180))
        screen.blit(title, (W//2 - title.get_width()//2, H//2 - 140))

        congrats = self._font_md.render("DUNIA TELAH DISELAMATKAN DARI KEHAMPAAN VOID", True, (200, 255, 240))
        screen.blit(congrats, (W//2 - congrats.get_width()//2, H//2 - 60))

        stats = [
            f"Level Karakter Akhir: {level}",
            f"Total Monster Dikalahkan: {kill_count}",
            f"Skor Legendaris: {score}"
        ]

        for i, s in enumerate(stats):
            ts = self._font_md.render(s, True, (180, 240, 220))
            screen.blit(ts, (W//2 - ts.get_width()//2, H//2 + i * 30))

        hint_y = H - 100 + int(math.sin(pygame.time.get_ticks() * 0.008) * 4)
        hint = self._font_md.render("TEKAN  [ ENTER ]  UNTUK KEMBALI KE MENU", True, (0, 255, 200))
        screen.blit(hint, (W//2 - hint.get_width()//2, hint_y))


# ============================================================
#  WIDGETS BARU (Kompatibilitas dengan main.py & game.py lama)
# ============================================================

class RetroPanel:
    """Panel bergaya retro dengan border ganda dan bayangan pixel."""
    def __init__(self, x, y, width, height, bg_color=(30,30,30), border_color=(255,255,255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.border_color = border_color
        
    def draw(self, surface):
        shadow_rect = self.rect.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        pygame.draw.rect(surface, (0,0,0), shadow_rect)
        pygame.draw.rect(surface, self.bg_color, self.rect)
        pygame.draw.rect(surface, self.border_color, self.rect, 1)
        
        inner_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 2, self.rect.width - 4, self.rect.height - 4)
        pygame.draw.rect(surface, self.border_color, inner_rect, 1)

class RetroButton:
    """Tombol interaktif dengan deteksi hover mouse atau pilihan keyboard."""
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.is_hovered = False
        
    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered
        
    def draw(self, surface, is_selected=False):
        active = self.is_hovered or is_selected
        bg_col = (30,30,30) if not active else (0, 210, 200)
        border_col = (255,255,255) if not active else (255, 210, 50)
        text_col = (255,255,255) if not active else (0,0,0)
        
        panel = RetroPanel(self.rect.x, self.rect.y, self.rect.width, self.rect.height, bg_color=bg_col, border_color=border_col)
        panel.draw(surface)
        
        font = pygame.font.Font(None, 16)
        text_surface = font.render(self.text, False, text_col)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

class ProgressBar:
    """Bar status untuk HP, Mana, XP, dll. dengan border luar."""
    def __init__(self, x, y, width, height, current_val, max_val, bar_color, bg_color=(30,30,30)):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.current_val = current_val
        self.max_val = max_val
        self.bar_color = bar_color
        self.bg_color = bg_color
        
    def draw(self, surface, current_val):
        self.current_val = max(0, min(current_val, self.max_val))
        bg_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, self.bg_color, bg_rect)
        
        fill_width = int((self.current_val / self.max_val) * (self.width - 4))
        if fill_width > 0:
            fill_rect = pygame.Rect(self.x + 2, self.y + 2, fill_width, self.height - 4)
            pygame.draw.rect(surface, self.bar_color, fill_rect)
            
        pygame.draw.rect(surface, (255,255,255), bg_rect, 1)

class DialogueBox:
    """Dialog Box dengan efek typewriter berjalan per karakter."""
    def __init__(self, x, y, width, height):
        self.panel = RetroPanel(x, y, width, height)
        self.text_list = []
        self.current_line_idx = 0
        self.displayed_text = ""
        self.char_idx = 0
        self.timer = 0
        self.speaker_name = "NPC"
        
    def start_dialogue(self, speaker, lines):
        self.speaker_name = speaker
        self.text_list = lines
        self.current_line_idx = 0
        self.displayed_text = ""
        self.char_idx = 0
        self.timer = 0
        
    def update(self):
        if self.current_line_idx < len(self.text_list):
            target_text = self.text_list[self.current_line_idx]
            if self.char_idx < len(target_text):
                self.timer += 1
                if self.timer >= 2:
                    self.char_idx += 1
                    self.displayed_text = target_text[:self.char_idx]
                    self.timer = 0
            
    def next_line(self):
        if self.current_line_idx < len(self.text_list):
            target_text = self.text_list[self.current_line_idx]
            if self.char_idx < len(target_text):
                self.char_idx = len(target_text)
                self.displayed_text = target_text
                return True
            else:
                self.current_line_idx += 1
                self.char_idx = 0
                self.displayed_text = ""
                if self.current_line_idx < len(self.text_list):
                    return True
        return False

    def draw(self, surface):
        self.panel.draw(surface)
        
        font = pygame.font.Font(None, 14)
        name_surface = font.render(f"[{self.speaker_name}]", False, (255, 210, 50))
        surface.blit(name_surface, (self.panel.rect.x + 10, self.panel.rect.y + 8))
        
        words = self.displayed_text.split(' ')
        lines_to_draw = []
        current_line = ""
        max_width = self.panel.rect.width - 24
        
        t_font = pygame.font.Font(None, 12)
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if t_font.size(test_line)[0] < max_width:
                current_line = test_line
            else:
                lines_to_draw.append(current_line)
                current_line = word
        if current_line:
            lines_to_draw.append(current_line)
            
        start_y = self.panel.rect.y + 24
        for i, line in enumerate(lines_to_draw[:3]):
            txt_surf = t_font.render(line, False, (255,255,255))
            surface.blit(txt_surf, (self.panel.rect.x + 12, start_y + (i * 12)))
            
        if self.current_line_idx < len(self.text_list):
            target_text = self.text_list[self.current_line_idx]
            if self.char_idx >= len(target_text):
                if (pygame.time.get_ticks() // 400) % 2 == 0:
                    arr_surf = t_font.render("V", False, (0, 210, 200))
                    surface.blit(arr_surf, (self.panel.rect.right - 15, self.panel.rect.bottom - 15))
