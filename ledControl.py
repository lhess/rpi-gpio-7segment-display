import time
import RPi.GPIO as GPIO

GPIO_PIN_RED = 26
GPIO_PIN_BLUE = 19
GPIO_PIN_GREEN = 13

GPIO.setmode(GPIO.BCM)

GPIO.setup(GPIO_PIN_RED, GPIO.OUT)
pRed = GPIO.PWM(GPIO_PIN_RED, 100)

GPIO.setup(GPIO_PIN_BLUE, GPIO.OUT)
pBlue = GPIO.PWM(GPIO_PIN_BLUE, 100)

GPIO.setup(GPIO_PIN_GREEN, GPIO.OUT)
pGreen = GPIO.PWM(GPIO_PIN_GREEN, 100)

pRGB = {pRed, pGreen, pBlue}
        
try:
    while 1:
        for pin in pRGB:
            pin.start(0)

            # fade in...
            for dc in range(0, 101, 1):
                pin.ChangeDutyCycle(dc)
                time.sleep(0.03)

            # ... fade out
            for dc in range(100, -1, -2):
                pin.ChangeDutyCycle(dc)
                time.sleep(0.03)

            pin.stop()
except KeyboardInterrupt:
    pass

for pin in pRGB:
    pin.stop()
    

GPIO.cleanup()
