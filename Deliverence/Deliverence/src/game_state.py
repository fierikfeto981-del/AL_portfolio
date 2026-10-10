# ============================================================
#  src/game_state.py — Manajemen state / layar game (Updated)
# ============================================================

import settings

class GameState:
    def __init__(self):
        self.current = settings.STATE_INTRO
        self._prev   = None

    @property
    def is_intro(self):        return self.current == settings.STATE_INTRO
    @property
    def is_menu(self):         return self.current == settings.STATE_MENU
    @property
    def is_playing(self):      return self.current == settings.STATE_PLAYING
    @property
    def is_boss(self):         return self.current == settings.STATE_BOSS
    @property
    def is_stage_clear(self):  return self.current == settings.STATE_STAGE_CLEAR
    @property
    def is_shop(self):         return self.current == settings.STATE_SHOP
    @property
    def is_game_over(self):    return self.current == settings.STATE_GAME_OVER
    @property
    def is_win(self):          return self.current == settings.STATE_WIN
    @property
    def is_map(self):          return self.current == settings.STATE_MAP
    @property
    def is_dialogue(self):     return self.current == settings.STATE_DIALOGUE

    def go_to(self, state):
        self._prev   = self.current
        self.current = state

    def go_menu(self):         self.go_to(settings.STATE_MENU)
    def go_playing(self):      self.go_to(settings.STATE_PLAYING)
    def go_boss(self):         self.go_to(settings.STATE_BOSS)
    def go_stage_clear(self):  self.go_to(settings.STATE_STAGE_CLEAR)
    def go_shop(self):         self.go_to(settings.STATE_SHOP)
    def go_game_over(self):    self.go_to(settings.STATE_GAME_OVER)
    def go_win(self):          self.go_to(settings.STATE_WIN)
    def go_intro(self):        self.go_to(settings.STATE_INTRO)
    def go_map(self):          self.go_to(settings.STATE_MAP)
    def go_dialogue(self):     self.go_to(settings.STATE_DIALOGUE)
