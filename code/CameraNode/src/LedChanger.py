from RPi import GPIO

LEDS = {"green": 16, "blue": 19, "errorLed": 12}


def initLedChanger():
    GPIO.setup(LEDS["green"], GPIO.OUT)
    GPIO.setup(LEDS["blue"], GPIO.OUT)
    GPIO.setup(LEDS["errorLed"], GPIO.OUT)


def lightErrorLedOn():
    GPIO.output(LEDS["errorLed"], GPIO.HIGH)


def lightErrorLedOff():
    GPIO.output(LEDS["errorLed"], GPIO.LOW)


def lightPhotoLedOn():
    GPIO.output(LEDS["blue"], GPIO.HIGH)


def lightPhotoLedOff():
    GPIO.output(LEDS["blue"], GPIO.LOW)
