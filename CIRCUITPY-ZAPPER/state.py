
class State(object):
    def __init__(self, zapper):
        self._zapper = zapper

    @property
    def zapper(self):
        return self._zapper

    def enter(self):
        pass

    def update(self, dt):
        pass
