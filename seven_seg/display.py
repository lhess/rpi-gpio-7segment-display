import asyncio
import time

from gpiozero import DigitalOutputDevice

from .message import TimedMessage
from .symbol_mapping import SYMBOL


class SevenSegmentDisplayMessageData:
    def __init__(self, display, message):
        self._data = []
        self._length = 0

        self._display_window_size = display.window_size()
        self._message = message
        self._formatted_string = self._format_message(message)
        self._init_data()

    def _init_data(self):
        for next_letter_is_dot, letter in self._letter_iterator():
            self._length += 1

            data = SYMBOL.get(letter, SYMBOL["_"])
            if next_letter_is_dot:
                data += SYMBOL.get(".", 0)

            self._data.append(self._to_bitfield(data))

    def _letter_iterator(self):
        string_length = len(self._formatted_string)
        for i in range(string_length):
            if self._formatted_string[i] != ".":
                yield (i < (string_length - 1) and self._formatted_string[i + 1] == "."), self._formatted_string[i]

    def _to_bitfield(self, n):
        bit_string = bin(n)[2:].rjust(8, "0")
        return [1 if digit == "1" else 0 for digit in bit_string]

    def _format_message(self, message):
        if len(message.string) == 0:
            return " " * self._display_window_size
        else:
            return message.string.upper().rjust(self._display_window_size, " ")

    def data_windowed_iterator(self):
        if (self._length <= self._display_window_size):
            yield "none", self._data
            return

        yield "start", self._data[0: self._display_window_size]

        for window_start_position in range(1, self._length - self._display_window_size):
            yield "middle", self._data[window_start_position: window_start_position + self._display_window_size]

        yield "end", self._data[self._length - self._display_window_size: self._length]

    def data_iterator(self):
        for digit_data in self._data:
            yield digit_data

    def time_iterator(self):
        if not self.is_timed():
            yield False

        t_end = time.time() + self._message.timeout
        while time.time() < t_end:
            yield True

        yield False

    def get_message_string(self):
        return self._message.string

    def is_timed(self):
        return isinstance(self._message, TimedMessage)


class SevenSegmentDisplay:
    def __init__(self, digit_pin_numbers, segment_pin_numbers):
        super(SevenSegmentDisplay, self).__init__()

        self._render_message = False
        self._window = range(len(digit_pin_numbers))
        self._window_size = len(digit_pin_numbers)
        self._sticky_message = None
        self._message_stack = []

        self._digit_pins = []
        for digit_pin_number in digit_pin_numbers:
            self._digit_pins.append(DigitalOutputDevice(digit_pin_number))

        self._segment_pins = []
        for segment_pin_number in segment_pin_numbers:
            self._segment_pins.append(DigitalOutputDevice(segment_pin_number))

    async def run(self):
        message = None
        while True:
            while not message or self._message_stack:
                if self._message_stack:
                    message = self._message_stack.pop(0)
                elif self._sticky_message:
                    message = self._sticky_message
                else:
                    await asyncio.sleep(0.5)

            print("DISPLAY > run > next message '%s'" % message.get_message_string())

            self._render_message = True
            if message.is_timed():
                print("!!! TIMED")
                for active in message.time_iterator():
                    if (not active or not self._render_message):
                        break

                    self._show(message)
                    await asyncio.sleep(0)
            else:
                print("!!! NOT TIMED")
                while self._render_message:
                    self._show(message)
                    await asyncio.sleep(0)

            self._render_message = False
            message = None

            await asyncio.sleep(0)

    def _show(self, message, scrolling_delay=0.8, start_delay=2.0, end_delay=3.0):
        delay_switcher = {
            "start": start_delay,
            "middle": scrolling_delay,
            "end": end_delay,
            "none": 0
        }

        for position, data_window in message.data_windowed_iterator():
            delay = delay_switcher.get(position)
            if delay > 0:
                t_end = time.time() + delay
                while time.time() < t_end:
                    self._render_digits(data_window)
            else:
                self._render_digits(data_window)

    def _render_digits(self, data):
        digit_num = 0
        for digit_data in data:
            segment_num = 0
            for bit in digit_data:
                if bit == 1:
                    self._segment_pins[segment_num].on()
                else:
                    self._segment_pins[segment_num].off()
                segment_num += 1

            self._digit_pins[digit_num].off()
            time.sleep(0.001)
            self._digit_pins[digit_num].on()
            digit_num += 1

    def show_sticky(self, message):
        print(">> SHOW_STICKY '%s'" % message.string)
        self._sticky_message = SevenSegmentDisplayMessageData(self, message)
        self.show_next()

    def show(self, message):
        print(">> SHOW '%s'" % message.string)
        self._message_stack.append(
            SevenSegmentDisplayMessageData(self, message)
        )
        self.show_next()

    def show_next(self):
        self._render_message = False

    def window_size(self):
        return self._window_size
