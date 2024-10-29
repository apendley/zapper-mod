from state import State

class StateIdle(State):
    def enter(self):
        self.zapper.set_muzzle_rgb(0, 0, 0)

    def update(self, dt):
        if self.zapper.button.rose:
            self.zapper.set_state(self.zapper.STATE_FIRE)
            return

        if self.zapper.button.value == True:
            self.zapper.set_muzzle_rgb(0, 0, 0)
        else:
            self.zapper.set_muzzle_rgb(64, 64, 64)
