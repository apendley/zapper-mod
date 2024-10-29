import os
import random
from state import State

class StateFire(State):
    def __init__(self, zapper):
        State.__init__(self, zapper)
        self._wave_files = self.zapper.create_sound_list("sounds/fire")
        self._last_sfx = None

    def enter(self):
        (self._last_sfx, self._muzzle_flash_duration) = self.zapper.play_random_sound(self._wave_files, self._last_sfx)
        self._ticks = self._muzzle_flash_duration

        self._hue = random.random()
        self.zapper.set_muzzle_hsv(self._hue, 1.0, 1.0)

    def update(self, dt):
        if self.zapper.button.rose:
            self.zapper.set_state(self.zapper.STATE_FIRE)
            return

        self._ticks -= dt

        if self._ticks <= 0:
            self.zapper.set_state(self.zapper.STATE_IDLE)
            return
        
        if self._muzzle_flash_duration > 0:
            brightness = self._ticks / self._muzzle_flash_duration
            self.zapper.set_muzzle_hsv(self._hue, 1.0, brightness)