# ============================================================
#  src/save_manager.py — Save & Load data JSON
# ============================================================

import json
import os
import settings

SAVE_PATH = os.path.join(settings.BASE_DIR, "save_data.json")

class SaveManager:
    @staticmethod
    def save(player, stage_index, score, kill_count, skills_unlocked):
        data = {
            "stage"          : stage_index,
            "score"          : score,
            "kill_count"     : kill_count,
            "level"          : player.level,
            "xp"             : player.xp,
            "xp_to_lv"       : player.xp_to_lv,
            "hp"             : player.hp,
            "max_hp"         : player.max_hp,
            "wp"             : player.wp,
            "max_wp"         : player.max_wp,
            "attack"         : player.attack,
            "move_speed"     : getattr(player, "move_speed", getattr(player, "speed", 400)),
            "bullet_cooldown": getattr(player, "bullet_cd_max", 1500),
            "gold"           : getattr(player, "gold", 0),
            "skills_unlocked": skills_unlocked,
        }
        try:
            with open(SAVE_PATH, "w") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"[SaveManager] Gagal save: {e}")
            return False

    @staticmethod
    def load():
        if not os.path.isfile(SAVE_PATH):
            return None
        try:
            with open(SAVE_PATH, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"[SaveManager] Gagal load: {e}")
            return None

    @staticmethod
    def apply(data, player, skill_manager):
        """Terapkan data save ke player dan skill manager."""
        player.level          = data.get("level", 1)
        player.xp             = data.get("xp", 0)
        player.xp_to_lv       = data.get("xp_to_lv", settings.XP_BASE)
        player.hp             = data.get("hp", settings.PLAYER_MAX_HP)
        player.max_hp         = data.get("max_hp", settings.PLAYER_MAX_HP)
        player.wp             = data.get("wp", 60)
        player.max_wp         = data.get("max_wp", 60)
        player.attack         = data.get("attack", settings.PLAYER_ATTACK)
        if hasattr(player, "move_speed"):
            player.move_speed = data.get("move_speed", settings.MOVE_SPEED)
        elif hasattr(player, "speed"):
            player.speed = data.get("move_speed", 400)
            
        if hasattr(player, "bullet_cd_max"):
            player.bullet_cd_max  = data.get("bullet_cooldown", settings.BULLET_COOLDOWN)
        player.gold           = data.get("gold", 0)
        if skill_manager is not None:
            for i in data.get("skills_unlocked", []):
                skill_manager.unlock(i)

    @staticmethod
    def delete():
        if os.path.isfile(SAVE_PATH):
            os.remove(SAVE_PATH)
