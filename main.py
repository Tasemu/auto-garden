from machine import ADC, Pin
import utime

adc = ADC(27)
statusLEDPin = Pin(25, Pin.OUT)

# These values are taken from dry air and a glass of water to calibrate the range of the moisture sensor.
adcValueDry = 57600
adcValueWet = 26750


def waitOneHour():
    utime.sleep(60 * 60)


class StatusLED:
    def __init__(self, ledPin):
        self.ledPin = ledPin

    def activate(self):
        self.ledPin.high()

    def deactivate(self):
        self.ledPin.low()

    def toggle(self):
        self.ledPin.toggle()


class MoistureSensor:
    def __init__(self, wetValue, dryValue):
        self.wetValue = wetValue
        self.dryValue = dryValue
        self.valueIntervals = (dryValue - wetValue) / 3

    def getDryValue(self):
        return self.dryValue

    def getWetValue(self):
        return self.wetValue

    def getPercentageDry(self, uint16value):
        calculationRange = self.dryValue - self.wetValue
        correctedStartValue = uint16value - self.wetValue
        percentage = (correctedStartValue * 100) / calculationRange
        return percentage

    def getPercentageWet(self, uint16value):
        calculationRange = self.dryValue - self.wetValue
        correctedStartValue = uint16value - self.wetValue
        percentage = (correctedStartValue * 100) / calculationRange
        return 100 - percentage

    def getMoistureEstimate(self, uint16value):
        if (uint16value > self.wetValue and uint16value < (self.wetValue + self.valueIntervals)):
            return "Very Wet"
        elif (uint16value > (self.wetValue + self.valueIntervals) and uint16value < (self.dryValue - self.valueIntervals)):
            return "Wet"
        elif (uint16value < self.dryValue and uint16value > (self.dryValue - self.valueIntervals)):
            return "Dry"
        else:
            return "Unsupported"


moistureSensor = MoistureSensor(adcValueWet, adcValueDry)
statusLed = StatusLED(statusLEDPin)

statusLed.activate()
utime.sleep(1)
statusLed.deactivate()

while True:
    # Wait an hour before testing soil moisture, this hopefully avoids a situation where a low battery event could cause flooding of plant.
    # waitOneHour()
    utime.sleep(5)  # Sleep 5 seconds for testing

    moistureValue = adc.read_u16()
    moisturePercentage = moistureSensor.getPercentageWet(moistureValue)
    moistureEstimate = moistureSensor.getMoistureEstimate(moistureValue)
    displayText = moistureEstimate + ": " + str(moisturePercentage) + "%"

    print(displayText)
