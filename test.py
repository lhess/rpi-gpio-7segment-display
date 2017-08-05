import asyncio

from gpiozero import Button, LED

from seven_seg import SevenSegmentDisplay, Message, TimedMessage

display = SevenSegmentDisplay(
    (22, 27, 17, 24),
    (11, 4, 23, 8, 7, 10, 18, 25)
)

btnCounter = 0

wtfButton = Button(6)
wtfLED = LED(12)
wtfLED.off()

leftButton = Button(16)


def wtfButtonPressed():
    global btnCounter

    wtfLED.blink(on_time=0.3, off_time=0.3)

    btnCounter += 1
    print("btn press '%d'" % btnCounter)
    display.show_sticky(Message(str(btnCounter)))


def wtfButtonReleased():
    wtfLED.off()

def leftButtonPressed():
    display.show(TimedMessage("Helo"))
    wtfLED.blink(0.2, 0.2, 10)


wtfButton.when_pressed = wtfButtonPressed
wtfButton.when_released = wtfButtonReleased
leftButton.when_pressed = leftButtonPressed

display.show_sticky(Message(str(btnCounter)))

ioloop = asyncio.get_event_loop()
tasks = [
    ioloop.create_task(display.run())
]

wait_tasks = asyncio.wait(tasks)
ioloop.run_until_complete(wait_tasks)

ioloop.close()
