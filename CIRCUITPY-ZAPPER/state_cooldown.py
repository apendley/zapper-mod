from state import State
import random

class StateCooldown(State):
    COOLDOWN_DURATION = 500

    def enter(self):
        self._ticks = self.COOLDOWN_DURATION
        self._hue = random.random()

    def update(self, dt):
        if self.zapper.button.rose:
            self.zapper.set_state(self.zapper.STATE_FIRE)
            return

        self._ticks -= dt

        if self._ticks <= 0:
            self._ticks = 0
            self.zapper.set_state(self.zapper.STATE_IDLE)
            return

        brightness = self._ticks / self.COOLDOWN_DURATION  
        self.zapper.set_muzzle_hsv(self._hue, 1.0, brightness)