# ============================================================
#  src/map.py — Layar Peta Pemilihan Stage (Destination Select) (Refactored)
# ============================================================

import pygame
import math
import settings

def _load_font(size, bold=False):
    try:    return pygame.font.SysFont("Segoe UI", size, bold=bold)
    except: return pygame.font.SysFont("Arial",    size, bold=bold)

class StageMap:
    """
    Mengelola layar peta interaktif untuk memilih stage.
    """

    def __init__(self):
        self._font_title = _load_font(32, bold=True)
        self._font_jp    = _load_font(28, bold=True)
        self._font_stname= _load_font(24, bold=True)
        self._font_info  = _load_font(18)
        self._font_sm    = _load_font(15)

        self.selected_node = 0
        self._tick         = 0

        W, H = settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT
        cx, cy = W // 2, H // 2 + 10

        # Stage nodes: Stage 1, Stage 2, Stage 3 (Boss)
        self.nodes = [
            {
                "idx": 0,
                "name": "Stage 1: Pantai Reruntuhan",
                "x": cx - 200, "y": cy,
                "jp_title": "鋼鉄の海岸線",
                "progress_str": "1/2",
                "connections": {"right": 1}
            },
            {
                "idx": 1,
                "name": "Stage 2: Jurang Tengah Laut",
                "x": cx, "y": cy,
                "jp_title": "深海の割れ目",
                "progress_str": "0/2",
                "connections": {"left": 0, "right": 2}
            },
            {
                "idx": 2,
                "name": "Stage 3: Sarang HyperEnd (BOSS)",
                "x": cx + 200, "y": cy,
                "jp_title": "ハイパーエンドの巣",
                "progress_str": "0/3",
                "connections": {"left": 1}
            }
        ]

        self.connections = [
            (0, 1), # Stage 1 -> Stage 2
            (1, 2)  # Stage 2 -> Stage 3
        ]

    def handle_key(self, key, stage_manager):
        curr_node = self.nodes[self.selected_node]
        conn = curr_node["connections"]

        if key == pygame.K_LEFT or key == pygame.K_a:
            if "left" in conn:
                self._try_select(conn["left"], stage_manager)
        elif key == pygame.K_RIGHT or key == pygame.K_d:
            if "right" in conn:
                self._try_select(conn["right"], stage_manager)
        elif key == pygame.K_RETURN or key == pygame.K_z:
            if self._is_unlocked(self.selected_node, stage_manager):
                return self.selected_node
        return None

    def _try_select(self, target_idx, stage_manager):
        self.selected_node = target_idx

    def _is_unlocked(self, node_idx, stage_manager):
        if node_idx == 0:
            return True
        if node_idx == 1:
            return stage_manager.stages[0].completed or (stage_manager.current_idx > 0)
        if node_idx == 2:
            return stage_manager.stages[1].completed or (stage_manager.current_idx > 1)
        return False

    def draw(self, screen, stage_manager):
        self._tick += 1
        W, H = settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT

        screen.fill((5, 12, 28))

        # Grid neon tipis
        grid_space = 40
        for x in range(0, W, grid_space):
            pygame.draw.line(screen, (10, 30, 60), (x, 0), (x, H))
        for y in range(0, H, grid_space):
            pygame.draw.line(screen, (10, 30, 60), (0, y), (W, y))

        # Siluet
        sub_surf = pygame.Surface((340, 240), pygame.SRCALPHA)
        pygame.draw.ellipse(sub_surf, (15, 30, 55, 80), sub_surf.get_rect())
        pygame.draw.ellipse(sub_surf, (25, 45, 80, 100), sub_surf.get_rect(), 3)
        pygame.draw.line(sub_surf, (25, 45, 80, 100), (0, 120), (340, 120), 2)
        screen.blit(sub_surf, (W//2 - 170, H//2 - 120))

        # Render Garis Neon Penghubung
        for start_idx, end_idx in self.connections:
            sn = self.nodes[start_idx]
            en = self.nodes[end_idx]

            connected = self._is_unlocked(start_idx, stage_manager) and self._is_unlocked(end_idx, stage_manager)
            line_col = (0, 160, 255) if connected else (25, 45, 75)

            if connected:
                pygame.draw.line(screen, (0, 100, 255, 40), (sn["x"], sn["y"]), (en["x"], en["y"]), 8)
                pygame.draw.line(screen, (0, 200, 255, 90), (sn["x"], sn["y"]), (en["x"], en["y"]), 4)
            pygame.draw.line(screen, line_col, (sn["x"], sn["y"]), (en["x"], en["y"]), 2)

        # Render Node Heksagonal
        for i, node in enumerate(self.nodes):
            unlocked = self._is_unlocked(i, stage_manager)
            selected = (i == self.selected_node)

            if unlocked:
                node_col = (0, 230, 220) if i != 2 else (220, 0, 255)
            else:
                node_col = (50, 70, 90)

            pulse = int(math.sin(self._tick * 0.1) * 4) if selected else 0

            self._draw_hexagon(screen, node["x"], node["y"], radius=22 + pulse, color=node_col, active=selected, unlocked=unlocked)
            self._draw_progress_badge(screen, node["x"] + 25, node["y"] + 15, node["progress_str"], unlocked)

        # Render Panel Informasi
        sel_node = self.nodes[self.selected_node]
        unlocked = self._is_unlocked(self.selected_node, stage_manager)

        jp_surf = self._font_jp.render(sel_node["jp_title"], True, (0, 220, 200, 80) if unlocked else (60,80,95))
        screen.blit(jp_surf, (W//2 - jp_surf.get_width()//2, H - 150))

        inf_box = pygame.Surface((W - 160, 68), pygame.SRCALPHA)
        inf_box.fill((2, 10, 25, 230))
        box_col = (0, 200, 255, 120) if unlocked else (40, 55, 70)
        pygame.draw.rect(inf_box, box_col, inf_box.get_rect(), 1)
        screen.blit(inf_box, (80, H - 105))

        name_col = (255, 215, 0) if unlocked else (120, 130, 140)
        name_surf = self._font_stname.render(sel_node["name"], True, name_col)
        screen.blit(name_surf, (100, H - 98))

        status_text = "SIAP DIJELAJAHI" if unlocked else "TERKUNCI — SELESAIKAN STAGE SEBELUMNYA"
        if self.selected_node == 2 and unlocked:
            status_text = "PERTEMPURAN AKHIR: LORD HYPEREND"
        status_col = (0, 255, 200) if unlocked else (220, 80, 80)
        status_surf = self._font_info.render(status_text, True, status_col)
        screen.blit(status_surf, (100, H - 68))

        pygame.draw.line(screen, (0, 100, 120), (40, 60), (W-40, 60), 1)

        title = self._font_title.render("PILIH DESTINASI PETUALANGAN", True, (255, 255, 255))
        screen.blit(title, (40, 18))
        dest = self._font_sm.render("DESTINATION SELECT", True, (0, 220, 200))
        screen.blit(dest, (40, 44))

        back_btn = pygame.Surface((180, 36), pygame.SRCALPHA)
        back_btn.fill((0, 15, 30, 200))
        pygame.draw.rect(back_btn, (0, 200, 255, 80), back_btn.get_rect(), 1)
        screen.blit(back_btn, (40, H - 215))

        back_text = self._font_sm.render("◀  [ B ]  KEMBALI", True, (0, 220, 200))
        screen.blit(back_text, (55, H - 207))

        nav_hint = self._font_sm.render("[ Arah Panah ] Navigasi    [ ENTER / Z ] Konfirmasi", True, (70, 100, 130))
        screen.blit(nav_hint, (W - nav_hint.get_width() - 40, H - 207))

    def _draw_hexagon(self, screen, x, y, radius, color, active, unlocked):
        points = []
        for i in range(6):
            angle = math.radians(i * 60)
            px = x + int(math.cos(angle) * radius)
            py = y + int(math.sin(angle) * radius)
            points.append((px, py))

        if unlocked:
            fill_col = (color[0], color[1], color[2], 50) if active else (color[0], color[1], color[2], 20)
            fill_surf = pygame.Surface((radius*2+10, radius*2+10), pygame.SRCALPHA)
            fill_pts = [(p[0] - x + radius+5, p[1] - y + radius+5) for p in points]
            pygame.draw.polygon(fill_surf, fill_col, fill_pts)
            screen.blit(fill_surf, (x - radius - 5, y - radius - 5))

        border_w = 3 if active else 1
        pygame.draw.polygon(screen, color, points, border_w)

        if unlocked:
            core_r = 6 if active else 4
            pygame.draw.circle(screen, color, (x, y), core_r)
        else:
            pygame.draw.line(screen, color, (x - 4, y - 4), (x + 4, y + 4), 2)
            pygame.draw.line(screen, color, (x + 4, y - 4), (x - 4, y + 4), 2)

    def _draw_progress_badge(self, screen, x, y, text, unlocked):
        w, h = 38, 18
        badge = pygame.Surface((w, h), pygame.SRCALPHA)
        badge.fill((0, 12, 20, 220))
        col = (0, 200, 255, 140) if unlocked else (40, 55, 70)
        pygame.draw.rect(badge, col, badge.get_rect(), 1)
        screen.blit(badge, (x, y))

        dot_col = (0, 255, 180) if unlocked else (100, 110, 120)
        pygame.draw.circle(screen, dot_col, (x + 6, y + h//2), 3)

        ts = self._font_sm.render(text, True, (200, 230, 255) if unlocked else (100,110,120))
        screen.blit(ts, (x + 13, y - 1))
