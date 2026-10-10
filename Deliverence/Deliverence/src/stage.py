# ============================================================
#  src/stage.py — Stage/Level configuration & manager (Refactored)
# ============================================================

import settings

# ── Konfigurasi tiap stage (disesuaikan dengan folder assets/) ───────────────────
STAGES = {
    1: {
        "map"         : "assets/image/maps/forest.tmx",
        "camera"      : "default",
        "tile_scale"  : 3.0,
        "name"        : "Pantai Reruntuhan",
        "subtitle"    : "Di sinilah segalanya berakhir...",
        "kill_target" : 10,
        "enemy_pool"  : ["Enemy1"],
        "spawn_rate"  : 100,
        "enemy_scale" : 1.0,
        "has_boss"    : False,
        "bg_top"      : (8,  35,  80),
        "bg_bot"      : (5,  15,  40),
        "ground_col"  : (30, 20, 10),
        "story"       : (
            "Hasumi terjatuh ke pantai reruntuhan...",
            "Makhluk-makhluk laut menyerangnya.",
            "Ia harus berjuang untuk bertahan.",
        ),
    },
    2: {
        "map"         : "assets/image/maps/prepare.tmx",
        "camera"      : "default",
        "tile_scale"  : 3.0,
        "name"        : "Jurang Tengah Laut",
        "subtitle"    : "Semakin dalam, semakin terang.",
        "kill_target" : 15,
        "enemy_pool"  : ["Enemy1"],
        "spawn_rate"  : 85,
        "enemy_scale" : 1.2,
        "has_boss"    : False,
        "bg_top"      : (4,  15,  50),
        "bg_bot"      : (2,   8,  25),
        "ground_col"  : (15, 10, 20),
        "story"       : (
            "Hasumi menyelam lebih dalam...",
            "Arus HyperEnd terasa semakin kuat.",
            "Predator laut mengincarnya.",
        ),
    },
    3: {
        "map"         : "assets/image/maps/bossfight.tmx",
        "camera"      : "default",
        "tile_scale"  : 3.0,
        "name"        : "Sarang HyperEnd",
        "subtitle"     : "Ini adalah akhir — atau awal?",
        "kill_target"  : 1,
        "enemy_pool"   : ["Enemy1"],
        "spawn_rate"   : 0,
        "enemy_scale"  : 1.9,
        "has_boss"     : True,
        "bg_top"       : (15,  0,  40),
        "bg_bot"       : (5,   0,  20),
        "ground_col"   : (10,  0,  25),
        "story"        : (
            "Energi Lord HyperEnd memenuhi lautan.",
            "Makhluk-makhluk berubah menjadi monster.",
            "Hasumi merasakan kehancuran dunianya di sini.",
        ),
    }
}

class Stage:
    """Merepresentasikan satu stage dengan konfigurasinya."""

    def __init__(self, index, config):
        self.index        = index # 0-indexed (0, 1, 2)
        self.map_path     = config["map"]
        self.camera_mode  = config["camera"]
        self.tile_scale   = config.get("tile_scale", 1.0)
        self.name         = config["name"]
        self.subtitle     = config["subtitle"]
        self.kill_target  = config["kill_target"]
        self.enemy_pool   = config["enemy_pool"]
        self.spawn_rate   = config["spawn_rate"]
        self.has_boss     = config["has_boss"]
        self.bg_top       = config["bg_top"]
        self.bg_bot       = config["bg_bot"]
        self.ground_col   = config["ground_col"]
        self.enemy_scale  = config["enemy_scale"]
        self.story        = config["story"]

        # Progress
        self.kill_count   = 0
        self.boss_spawned = False
        self.boss_dead    = False
        self.completed    = False
        self.grade        = ""

    @property
    def ready_for_boss(self):
        return self.kill_count >= self.kill_target and not self.boss_spawned

    @property
    def cleared(self):
        return self.boss_dead if self.has_boss else (self.kill_count >= self.kill_target)

    def register_kill(self):
        self.kill_count += 1

    def calculate_grade(self, hp_ratio, time_taken_seconds, damage_taken):
        score = 0
        if hp_ratio > 0.8:   score += 40
        elif hp_ratio > 0.5: score += 25
        elif hp_ratio > 0.2: score += 10

        if time_taken_seconds < 60:  score += 35
        elif time_taken_seconds < 90: score += 20
        elif time_taken_seconds < 120: score += 10

        if damage_taken == 0:         score += 25
        elif damage_taken < 30:       score += 15
        elif damage_taken < 60:       score += 5

        if score >= 85:   self.grade = "S"
        elif score >= 65: self.grade = "A"
        elif score >= 40: self.grade = "B"
        else:             self.grade = "C"
        return self.grade

    def get_scaled_enemy(self, base_data):
        import copy
        d          = copy.deepcopy(base_data)
        d["hp"]    = int(d["hp"]    * self.enemy_scale)
        d["damage"]= int(d["damage"]* self.enemy_scale)
        return d

class StageManager:
    """Mengatur urutan stage dan transisi antar stage."""

    def __init__(self):
        self.stages       = [Stage(idx, STAGES[idx + 1]) for idx in range(len(STAGES))]
        self.current_idx  = 0
        self.final_boss   = False   # True setelah semua stage selesai

    @property
    def current(self) -> Stage:
        if self.current_idx < len(self.stages):
            return self.stages[self.current_idx]
        return None

    @property
    def is_last_stage(self):
        return self.current_idx >= len(self.stages) - 1

    def advance(self):
        """Pindah ke stage berikutnya. Return False kalau sudah final."""
        self.current_idx += 1
        if self.current_idx >= len(self.stages):
            self.final_boss = True
            return False
        return True

    def reset(self):
        self.stages      = [Stage(idx, STAGES[idx + 1]) for idx in range(len(STAGES))]
        self.current_idx = 0
        self.final_boss  = False
