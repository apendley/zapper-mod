from state import State
import random

class StatePowerOn(State):
    COLOR_CHANGE_INTERVAL = 25

    def __init__(self, zapper):
        State.__init__(self, zapper)
        self._wave_files = self.zapper.create_sound_list("sounds/power_on")
        self._hue = 0

    def enter(self):
        (_, self._power_on_duration) = self.zapper.play_random_sound(self._wave_files)

        self._ticks = 0
        self._color_change_time = 0
        self._change_color()

    def update(self, dt):
        self._ticks += dt

        if self._ticks >= self._power_on_duration:
            self.zapper.set_state(self.zapper.STATE_COOLDOWN)
            return

        self._color_change_time -= dt
        if self._color_change_time <= 0:
            self._change_color()

        brightness = self._ticks / self._power_on_duration
        self.zapper.set_muzzle_hsv(self._hue, 1.0, brightness)        

    def _change_color(self):
        self._hue = random.random()
        self._color_change_time = self.COLOR_CHANGE_INTERVAL        
