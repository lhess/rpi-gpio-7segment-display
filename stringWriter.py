import RPi.GPIO as GPIO
import time

NUM_OF_DIGITS = 4

GPIO.setmode(GPIO.BCM)

# GPIO ports for the 7seg pins
segments =  (11,4,23,8,7,10,18,25)
for segment in segments:
    GPIO.setup(segment, GPIO.OUT)
    GPIO.output(segment, 0)
 
# GPIO ports for the digit 0-3 pins 
digits = (22,27,17,24)
for digit in digits:
    GPIO.setup(digit, GPIO.OUT)
    GPIO.output(digit, 1)
 
letters = {
    'K': (0,1,1,0,1,1,1),
    'L': (0,0,0,1,1,1,0),
    'E': (1,0,0,1,1,1,1),
    'A': (1,1,1,0,1,1,1),
    'R': (1,1,1,0,1,1,1),
    'S': (1,0,1,1,0,1,1),
    'O': (1,1,1,1,1,1,0),
    ' ': (0,0,0,0,0,0,0),
    '0': (1,1,1,1,1,1,0),
    '1': (0,1,1,0,0,0,0),
    '2': (1,1,0,1,1,0,1),
    '3': (1,1,1,1,0,0,1),
    '4': (0,1,1,0,0,1,1),
    '5': (1,0,1,1,0,1,1),
    '6': (1,0,1,1,1,1,1),
    '7': (1,1,1,0,0,0,0),
    '8': (1,1,1,1,1,1,1),
    '9': (1,1,1,1,0,1,1),
    '_': (0,0,0,0,0,0,1)
}

def writeDisplay(str, seconds = 0.5):
    print str, "for", seconds, "seconds"
    t_end = time.time() + seconds
    while time.time() < t_end:
        for digitNum in range(NUM_OF_DIGITS):
            if len(str) > digitNum:
                letter = str.upper()[digitNum]
                letterBits = letters[letter] if letter in letters.keys() else letters["_"]
                for segmentNum in range(0, 7):
                    GPIO.output(segments[segmentNum], letterBits[segmentNum])
                GPIO.output(digits[digitNum], 0)
                time.sleep(0.001)
                GPIO.output(digits[digitNum], 1)

def writeMarquee(str):
    str = str.rjust(len(str) + NUM_OF_DIGITS, " ")
    str = str.ljust(len(str) + NUM_OF_DIGITS, " ")
    strLen = len(str)

    for i in range(strLen - NUM_OF_DIGITS):
        strWindow = str[i:i + NUM_OF_DIGITS]
        writeDisplay(strWindow)

try:
    while True:
        writeMarquee("LOL LOL LOL");
finally:
    GPIO.cleanup()
