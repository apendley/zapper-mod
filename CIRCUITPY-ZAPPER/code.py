from adafruit_ticks import ticks_ms, ticks_diff
from zapper import Zapper

zapper = Zapper()
zapper.set_state(zapper.STATE_POWER_ON)

last_ticks = ticks_ms()

while True:
    t = ticks_ms()
    dt = ticks_diff(t, last_ticks)
    last_ticks = t
    zapper.update(dt)