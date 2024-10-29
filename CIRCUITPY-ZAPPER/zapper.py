import board
import os
import random

from digitalio import DigitalInOut, Direction, Pull
from adafruit_debouncer import Debouncer

from audiocore import WaveFile
from audiobusio import I2SOut
from audiomixer import Mixer

import neopixel
import adafruit_fancyled.adafruit_fancyled

from state_power_on import StatePowerOn
from state_cooldown import StateCooldown
from state_idle import StateIdle
from state_fire import StateFire

class Zapper:
    STATE_POWER_ON = 0
    STATE_COOLDOWN = 1
    STATE_IDLE = 2
    STATE_FIRE = 3

    MUZZLE_GAMMA = 2.0

    def __init__(self):
        # Enable power to sound, neopixels, etc
        self._ext_power = DigitalInOut(board.EXTERNAL_POWER)
        self._ext_power.switch_to_output(value=True)

        # Set up debounce for trigger
        button_input = DigitalInOut(board.EXTERNAL_BUTTON)
        button_input.direction = Direction.INPUT
        button_input.pull = Pull.UP
        self._button = Debouncer(button_input)

        # Set up audio system and mixer
        self._audio = I2SOut(board.I2S_BIT_CLOCK, board.I2S_WORD_SELECT, board.I2S_DATA)
        self._mixer = Mixer(voice_count=1, 
                            sample_rate=44100, 
                            channel_count=1, 
                            bits_per_sample=16, 
                            samples_signed=True)

        self._audio.play(self._mixer)
        self._mixer.voice[0].level = 1.0

        # Set up neopixel and fancy led
        self._pixel = neopixel.NeoPixel(board.EXTERNAL_NEOPIXELS, 1, brightness=1.0, auto_write=True, pixel_order="RGB")
        self._fancy = adafruit_fancyled.adafruit_fancyled

        # Set up state machine
        self._states = [
            StatePowerOn(self),
            StateCooldown(self),
            StateIdle(self),
            StateFire(self)
        ]

        self._state = None        

    @property
    def button(self):
        return self._button

    @property
    def fancy(self):
        return self._fancy

    def set_muzzle_hsv(self, hue, saturation=1.0, value=1.0):
        fancy_color = self.fancy.CHSV(hue, 1.0, value)
        self._set_muzzle_fancy_color(fancy_color)

    def set_muzzle_rgb(self, r, g, b):
        color = self.fancy.CRGB(r, g, b)
        self._set_muzzle_fancy_color(color)

    def _set_muzzle_fancy_color(self, fancy_color):
        fancy_color = self.fancy.gamma_adjust(fancy_color, gamma_value=self.MUZZLE_GAMMA)
        self._pixel.fill(fancy_color.pack())

    def set_state(self, state_identifier):
        if state_identifier is None:
            self._state = None
            return;

        if state_identifier >= len(self._states):
            print("Invalid state identifier:", state_identifier);
            self._state = None
            return

        self._state = self._states[state_identifier]

        if self._state:
            self._state.enter()

    def update(self, dt):
        if self._state:
            self._button.update()
            self._state.update(dt)

    # Plays a wave file, and returns the duration of the sound in milliseconds
    def play_sound(self, filename):
        try:
            wave_file = open(filename, "rb")
            wave = WaveFile(wave_file)            
        except:
            print("Error opening wav file:", filename)
            return 0

        # Move to the end of the file to get the size of the data
        wave_file.seek(0, 2)
        file_size = wave_file.tell()

        # Reset to the start of the file
        wave_file.seek(0)                    

        # Calculate the duration of the sound, in milliseconds
        bit_depth = wave.bits_per_sample
        byte_rate = wave.sample_rate * wave.channel_count * (bit_depth / 8)
        duration = (file_size - 44) / byte_rate
        duration = int(duration * 1000)
        
        # Play the sound
        self._mixer.voice[0].play(wave)

        # Return the duration
        return duration

    # Returns a list of .wav files from the specified directory
    def create_sound_list(self, directory):
        return [
            directory + "/" + file
            for file in os.listdir(directory)
            if (file.endswith(".wav") and not file.startswith("._"))
        ]

    # Play a random sound from a list of wav files.
    # If last_sound_index is provided, that sound will not be played twice in a row.
    # Returns a tuple: (played_sfx_index, duration_in_ms)
    def play_random_sound(self, sound_list, last_sound_index=None):
        sound_list_count = len(sound_list)
        sfx_index = random.randrange(0, sound_list_count)

        # Don't play the same sound twice in a row
        while sfx_index == last_sound_index:
            sfx_index = random.randrange(0, sound_list_count)
        
        duration = self.play_sound(sound_list[sfx_index])
        return (sfx_index, duration)