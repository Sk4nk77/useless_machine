import time
import math
import smbus
from gpiozero import Button

# Raspi PCA9685 16-Channel PWM Servo Driver
class PCA9685:
    __SUBADR1 = 0x02
    __SUBADR2 = 0x03
    __SUBADR3 = 0x04
    __MODE1 = 0x00
    __PRESCALE = 0xFE
    __LED0_ON_L = 0x06
    __LED0_ON_H = 0x07
    __LED0_OFF_L = 0x08
    __LED0_OFF_H = 0x09
    __ALLLED_ON_L = 0xFA
    __ALLLED_ON_H = 0xFB
    __ALLLED_OFF_L = 0xFC
    __ALLLED_OFF_H = 0xFD

    def __init__(self, address=0x40, debug=False):
        self.bus = smbus.SMBus(1)
        self.address = address
        self.debug = debug
        if self.debug:
            print("Resetting PCA9685")
        self.write(self.__MODE1, 0x00)

    def write(self, reg, value):
        "Writes an 8-bit value to the specified register/address"
        self.bus.write_byte_data(self.address, reg, value)
        if self.debug:
            print("I2C: Write 0x%02X to register 0x%02X" % (value, reg))

    def read(self, reg):
        "Read an unsigned byte from the I2C device"
        result = self.bus.read_byte_data(self.address, reg)
        if self.debug:
            print("I2C: Device 0x%02X returned 0x%02X from reg 0x%02X" % (self.address, result & 0xFF, reg))
        return result

    def setPWMFreq(self, freq):
        "Sets the PWM frequency"
        prescaleval = 24500000.0    # 25MHz
        prescaleval /= 4096.0       # 12-bit
        prescaleval /= float(freq)
        prescaleval -= 1.0
        if self.debug:
            print("Setting PWM frequency to %d Hz" % freq)
            print("Estimated pre-scale: %d" % prescaleval)
        prescale = math.floor(prescaleval + 0.5)
        if self.debug:
            print("Final pre-scale: %d" % prescale)

        oldmode = self.read(self.__MODE1)
        newmode = (oldmode & 0x7F) | 0x10  # sleep
        self.write(self.__MODE1, newmode)  # go to sleep
        self.write(self.__PRESCALE, int(math.floor(prescale)))
        self.write(self.__MODE1, oldmode)
        time.sleep(0.005)
        self.write(self.__MODE1, oldmode | 0x80)

    def setPWM(self, channel, on, off):
        "Sets a single PWM channel"
        self.write(self.__LED0_ON_L + 4 * channel, on & 0xFF)
        self.write(self.__LED0_ON_H + 4 * channel, on >> 8)
        self.write(self.__LED0_OFF_L + 4 * channel, off & 0xFF)
        self.write(self.__LED0_OFF_H + 4 * channel, off >> 8)
        if self.debug:
            print("channel: %d  LED_ON: %d LED_OFF: %d" % (channel, on, off))

    def setServoPulse(self, channel, pulse):
        "Sets the Servo Pulse, The PWM frequency must be 50HZ"
        pulse = pulse * 4096 / 20000  # PWM frequency is 50HZ, the period is 20000us
        self.setPWM(channel, 0, int(pulse))

# Set up PCA9685 and GPIO
pwm = PCA9685(0x40, debug=False)
pwm.setPWMFreq(50)

# Define servo channels
lid_servo_channel = 15
arm_servo_channel = 14
flag_servo_channel = 13

# Set up trigger button (GPIO 21)
trigger_button = Button(21)

# Servo default starting positions
def set_default_positions():
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm fully closed (pulse 2450) (pulse 2450) position
    pwm.setServoPulse(flag_servo_channel, 2450)  # Flag fully closed position
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid fully closed position

set_default_positions()

action = 1

# Define actions
# The lid must always open before the arm moves, and the arm must be fully closed before the lid can be closed

def action1():
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
    time.sleep(1)
    pwm.setServoPulse(arm_servo_channel, 1700)  # Arm fully open
    time.sleep(0.5)
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm fully closed
    time.sleep(1)
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid back to fully closed (pulse 2400) (pulse 2400)
    time.sleep(1)

def action2():
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
    time.sleep(0.1)
    pwm.setServoPulse(arm_servo_channel, 1700)  # Arm fully open
    time.sleep(0.25)
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm fully closed
    time.sleep(0.1)
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid back to fully closed

def action3():
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
    time.sleep(0.1)
    pwm.setServoPulse(arm_servo_channel, 1700)  # Arm fully open
    time.sleep(0.1)
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm fully closed
    time.sleep(0.1)
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid back to fully closed

def action4():
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
    time.sleep(0.1)
    pwm.setServoPulse(arm_servo_channel, 1700)  # Arm fully open
    time.sleep(2.5)
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm fully closed
    time.sleep(0.1)
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid back to fully closed

def action5():
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
    time.sleep(0.1)
    for _ in range(3):
        pwm.setServoPulse(lid_servo_channel, 1500)  # Lid to mid position
        time.sleep(0.5)
        pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
        time.sleep(0.5)
    pwm.setServoPulse(arm_servo_channel, 1700)  # Arm fully open
    time.sleep(0.1)
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm fully closed
    time.sleep(0.1)
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid back to fully closed

def action6():
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
    time.sleep(0.1)
    for _ in range(3):
        pwm.setServoPulse(arm_servo_channel, 2300)  # Arm partially closed
        time.sleep(0.25)
        pwm.setServoPulse(arm_servo_channel, 1700)  # Arm fully open
        time.sleep(0.1)
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm fully closed
    time.sleep(0.25)
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid back to fully closed

def action7():
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
    time.sleep(0.1)
    pwm.setServoPulse(arm_servo_channel, 1700)  # Arm fully open
    time.sleep(0.1)
    for pos in range(1700, 2450, 20):
        pwm.setServoPulse(arm_servo_channel, pos)
        time.sleep(0.1)
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm fully closed
    time.sleep(0.1)
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid back to fully closed

def action8():
    if trigger_button.is_pressed:
        time.sleep(1)
        pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
        time.sleep(0.1)
        pwm.setServoPulse(arm_servo_channel, 1700)  # Arm fully open
        time.sleep(0.1)
        pwm.setServoPulse(arm_servo_channel, 2450)  # Arm fully closed
        time.sleep(0.1)
        for pos in range(1500, 2450, 50):
            pwm.setServoPulse(flag_servo_channel, pos)
            time.sleep(0.03)
        time.sleep(0.25)
        for _ in range(5):
            for pos in range(2450, 1500, -50):
                pwm.setServoPulse(flag_servo_channel, pos)
                time.sleep(0.03)
            for pos in range(1500, 2450, 50):
                pwm.setServoPulse(flag_servo_channel, pos)
                time.sleep(0.03)
        time.sleep(0.25)
        for pos in range(2450, 1500, -50):
            pwm.setServoPulse(flag_servo_channel, pos)
            time.sleep(0.05)
        pwm.setServoPulse(flag_servo_channel, 2450)  # Flag fully closed
        time.sleep(0.1)
        pwm.setServoPulse(arm_servo_channel, 2450)  # Arm fully closed
        time.sleep(0.1)
        pwm.setServoPulse(lid_servo_channel, 2400)  # Lid back to fully closed

def action9():
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
    time.sleep(0.5)
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid closes halfway
    time.sleep(0.5)
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open again
    time.sleep(0.5)
    pwm.setServoPulse(arm_servo_channel, 1700)  # Arm fully open
    time.sleep(0.5)
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm fully closed
    time.sleep(0.5)
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid back to fully closed

def action10():
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
    time.sleep(0.2)
    pwm.setServoPulse(arm_servo_channel, 1700)  # Arm fully open
    time.sleep(0.2)
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm fully closed
    time.sleep(0.2)
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid back to fully closed

def action11():
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
    time.sleep(0.1)
    pwm.setServoPulse(arm_servo_channel, 1700)  # Arm fully open
    time.sleep(0.5)
    pwm.setServoPulse(lid_servo_channel, 1500)  # Lid partially closes
    time.sleep(0.5)
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open again
    time.sleep(0.5)
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm fully closed
    time.sleep(0.1)
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid back to fully closed

def action12():
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
    time.sleep(0.1)
    pwm.setServoPulse(arm_servo_channel, 1700)  # Arm fully open
    time.sleep(0.1)
    pwm.setServoPulse(arm_servo_channel, 2300)  # Arm moves halfway
    time.sleep(0.1)
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm fully closed
    time.sleep(0.1)
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid back to fully closed

def action13():
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
    time.sleep(0.5)
    pwm.setServoPulse(arm_servo_channel, 1700)  # Arm fully open
    time.sleep(0.5)
    pwm.setServoPulse(flag_servo_channel, 1500)  # Flag halfway up
    time.sleep(0.5)
    pwm.setServoPulse(flag_servo_channel, 2450)  # Flag fully closed
    time.sleep(0.5)
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm fully closed
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid back to fully closed

def action14():
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
    time.sleep(0.1)
    pwm.setServoPulse(arm_servo_channel, 1700)  # Arm fully open
    time.sleep(0.5)
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm fully closed
    time.sleep(0.1)
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid closes halfway
    time.sleep(0.5)
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid opens again
    time.sleep(0.5)
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid back to fully closed

def action15():
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
    time.sleep(0.1)
    pwm.setServoPulse(arm_servo_channel, 1700)  # Arm fully open
    time.sleep(0.5)
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm fully closed
    time.sleep(0.1)
    for _ in range(3):
        pwm.setServoPulse(flag_servo_channel, 1500)  # Flag halfway up
        time.sleep(0.2)
        pwm.setServoPulse(flag_servo_channel, 2450)  # Flag fully closed
        time.sleep(0.2)
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid back to fully closed

def action16():
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
    time.sleep(0.3)
    pwm.setServoPulse(arm_servo_channel, 1700)  # Arm fully open
    time.sleep(0.3)
    pwm.setServoPulse(lid_servo_channel, 1500)  # Lid closes halfway
    time.sleep(0.3)
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid opens again
    time.sleep(0.3)
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm fully closed
    time.sleep(0.3)
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid back to fully closed

def action17():
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
    time.sleep(0.2)
    pwm.setServoPulse(flag_servo_channel, 1500)  # Flag halfway up
    time.sleep(0.2)
    pwm.setServoPulse(flag_servo_channel, 2450)  # Flag fully closed
    time.sleep(0.2)
    pwm.setServoPulse(arm_servo_channel, 1700)  # Arm fully open
    time.sleep(0.3)
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm fully closed
    time.sleep(0.2)
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid back to fully closed

def action18():
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
    time.sleep(0.4)
    pwm.setServoPulse(arm_servo_channel, 1700)  # Arm fully open
    time.sleep(0.4)
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm fully closed
    time.sleep(0.4)
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid back to fully closed
    time.sleep(0.4)

def action19():
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
    time.sleep(0.3)
    for _ in range(2):
        pwm.setServoPulse(arm_servo_channel, 1700)  # Arm fully open
        time.sleep(0.3)
        pwm.setServoPulse(arm_servo_channel, 2450)  # Arm fully closed
        time.sleep(0.3)
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid back to fully closed

def action20():
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
    time.sleep(0.1)
    pwm.setServoPulse(flag_servo_channel, 2000)  # Flag raises slightly
    time.sleep(0.1)
    pwm.setServoPulse(flag_servo_channel, 2450)  # Flag lowers
    time.sleep(0.1)
    pwm.setServoPulse(arm_servo_channel, 1700)  # Arm fully open
    time.sleep(0.3)
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm fully closed
    time.sleep(0.3)
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid back to fully closed

def action21():
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
    time.sleep(0.2)
    pwm.setServoPulse(arm_servo_channel, 1700)  # Arm fully open
    time.sleep(0.2)
    pwm.setServoPulse(flag_servo_channel, 1500)  # Flag halfway up
    time.sleep(0.2)
    pwm.setServoPulse(flag_servo_channel, 2450)  # Flag fully closed
    time.sleep(0.2)
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm fully closed
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid back to fully closed

def action22():
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
    time.sleep(0.3)
    pwm.setServoPulse(arm_servo_channel, 1700)  # Arm fully open
    time.sleep(0.1)
    pwm.setServoPulse(arm_servo_channel, 1800)  # Arm makes a small adjustment
    time.sleep(0.1)
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm fully closed
    time.sleep(0.3)
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid back to fully closed

def action23():
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
    time.sleep(0.1)
    pwm.setServoPulse(arm_servo_channel, 1700)  # Arm fully open
    time.sleep(0.5)
    pwm.setServoPulse(flag_servo_channel, 1500)  # Flag halfway up
    time.sleep(0.1)
    pwm.setServoPulse(flag_servo_channel, 2450)  # Flag fully closed
    time.sleep(0.1)
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm fully closed
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid back to fully closed

def action24():
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
    time.sleep(0.2)
    pwm.setServoPulse(arm_servo_channel, 1700)  # Arm fully open
    time.sleep(0.2)
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm almost closed
    time.sleep(0.2)
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm fully closed
    time.sleep(0.2)
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid back to fully closed

def action25():
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
    time.sleep(0.1)
    pwm.setServoPulse(arm_servo_channel, 1700)  # Arm fully open
    time.sleep(0.3)
    pwm.setServoPulse(arm_servo_channel, 2000)  # Arm moves slightly closed
    time.sleep(0.3)
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm fully closed
    time.sleep(0.1)
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid back to fully closed

def action26():
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
    time.sleep(0.3)
    pwm.setServoPulse(arm_servo_channel, 1700)  # Arm fully open
    time.sleep(0.1)
    pwm.setServoPulse(lid_servo_channel, 1500)  # Lid partially closes
    time.sleep(0.1)
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid opens again
    time.sleep(0.3)
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm fully closed
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid back to fully closed

def action27():
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
    time.sleep(0.1)
    pwm.setServoPulse(arm_servo_channel, 1700)  # Arm fully open
    time.sleep(0.4)
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm fully closed
    time.sleep(0.2)
    pwm.setServoPulse(flag_servo_channel, 1500)  # Flag halfway up
    time.sleep(0.4)
    pwm.setServoPulse(flag_servo_channel, 2450)  # Flag fully closed
    pwm.setServoPulse(lid_servo_channel, 2300)  # Lid back to fully closed

def action28():
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
    time.sleep(0.2)
    pwm.setServoPulse(arm_servo_channel, 1700)  # Arm fully open
    time.sleep(0.3)
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm fully closed
    time.sleep(0.1)
    pwm.setServoPulse(lid_servo_channel, 1500)  # Lid partially closes
    time.sleep(0.2)
    pwm.setServoPulse(lid_servo_channel, 2300)  # Lid back to fully closed

def action29():
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
    time.sleep(0.1)
    pwm.setServoPulse(arm_servo_channel, 1700)  # Arm fully open
    time.sleep(0.2)
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm fully closed
    time.sleep(0.2)
    pwm.setServoPulse(lid_servo_channel, 2300)  # Lid back to fully closed
    time.sleep(0.2)
    pwm.setServoPulse(flag_servo_channel, 1500)  # Flag halfway up
    time.sleep(0.1)
    pwm.setServoPulse(flag_servo_channel, 2450)  # Flag fully closed

def action30():
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
    time.sleep(0.1)
    pwm.setServoPulse(arm_servo_channel, 1700)  # Arm fully open
    time.sleep(0.1)
    pwm.setServoPulse(lid_servo_channel, 1500)  # Lid partially closes
    time.sleep(0.1)
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open again
    time.sleep(0.1)
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm fully closed
    pwm.setServoPulse(lid_servo_channel, 2300)  # Lid back to fully closed

def action31():
    pwm.setServoPulse(lid_servo_channel, 1200)  # Slowly open lid halfway
    time.sleep(1)
    pwm.setServoPulse(arm_servo_channel, 1800)  # Slowly move arm halfway open
    time.sleep(1)
    pwm.setServoPulse(arm_servo_channel, 2450)  # Quickly retract arm
    time.sleep(0.2)
    pwm.setServoPulse(lid_servo_channel, 1100)  # Fake open the lid fully
    time.sleep(0.5)
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid back to fully closed

def action32():
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
    time.sleep(0.5)
    pwm.setServoPulse(arm_servo_channel, 1700)  # Arm fully open
    time.sleep(0.5)
    for _ in range(3):
        pwm.setServoPulse(flag_servo_channel, 1500)  # Flag halfway up
        time.sleep(0.2)
        pwm.setServoPulse(flag_servo_channel, 2450)  # Flag fully closed
        time.sleep(0.2)
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm fully closed
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid back to fully closed

def action33():
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
    time.sleep(1)
    pwm.setServoPulse(arm_servo_channel, 1700)  # Arm fully open
    time.sleep(0.5)
    pwm.setServoPulse(arm_servo_channel, 2300)  # Arm moves halfway back
    time.sleep(0.5)
    pwm.setServoPulse(arm_servo_channel, 1700)  # Arm fully open again
    time.sleep(0.5)
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm fully closed
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid back to fully closed

def action34():
    pwm.setServoPulse(lid_servo_channel, 1500)  # Lid slowly opens halfway
    time.sleep(1)
    pwm.setServoPulse(arm_servo_channel, 1700)  # Arm fully open
    time.sleep(0.5)
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm quickly closes
    time.sleep(0.2)
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid back to fully closed

def action35():
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
    time.sleep(0.3)
    pwm.setServoPulse(flag_servo_channel, 1500)  # Flag halfway up
    time.sleep(0.3)
    pwm.setServoPulse(flag_servo_channel, 2450)  # Flag fully closed
    time.sleep(0.3)
    pwm.setServoPulse(arm_servo_channel, 1700)  # Arm fully open
    time.sleep(0.3)
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm fully closed
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid back to fully closed

def action36():
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
    time.sleep(0.4)
    pwm.setServoPulse(arm_servo_channel, 1700)  # Arm fully open
    time.sleep(0.4)
    pwm.setServoPulse(flag_servo_channel, 1500)  # Flag halfway up
    time.sleep(0.4)
    pwm.setServoPulse(flag_servo_channel, 2450)  # Flag fully closed
    time.sleep(0.4)
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm fully closed
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid back to fully closed

def action37():
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
    time.sleep(0.1)
    pwm.setServoPulse(arm_servo_channel, 1800)  # Arm halfway open
    time.sleep(0.1)
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm quickly closes
    time.sleep(0.1)
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid back to fully closed

def action38():
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
    time.sleep(0.2)
    pwm.setServoPulse(arm_servo_channel, 1700)  # Arm fully open
    time.sleep(0.2)
    for _ in range(2):
        pwm.setServoPulse(flag_servo_channel, 1500)  # Flag halfway up
        time.sleep(0.1)
        pwm.setServoPulse(flag_servo_channel, 2450)  # Flag fully closed
        time.sleep(0.1)
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm fully closed
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid back to fully closed

def action39():
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
    time.sleep(0.3)
    pwm.setServoPulse(flag_servo_channel, 2000)  # Flag raises slightly
    time.sleep(0.2)
    pwm.setServoPulse(flag_servo_channel, 2450)  # Flag lowers
    time.sleep(0.2)
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid back to fully closed

def action40():
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
    time.sleep(0.5)
    pwm.setServoPulse(arm_servo_channel, 1700)  # Arm fully open
    time.sleep(0.5)
    pwm.setServoPulse(flag_servo_channel, 1500)  # Flag halfway up
    time.sleep(0.5)
    pwm.setServoPulse(flag_servo_channel, 2450)  # Flag fully closed
    time.sleep(0.5)
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm fully closed
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid back to fully closed

def action41():
    pwm.setServoPulse(lid_servo_channel, 1500)  # Lid opens halfway
    time.sleep(1)
    pwm.setServoPulse(arm_servo_channel, 1700)  # Arm fully open
    time.sleep(0.5)
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm quickly retracts
    time.sleep(0.2)
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid back to fully closed

def action42():
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
    time.sleep(0.3)
    pwm.setServoPulse(arm_servo_channel, 1700)  # Arm fully open
    time.sleep(0.5)
    pwm.setServoPulse(flag_servo_channel, 1500)  # Flag halfway up
    time.sleep(0.3)
    pwm.setServoPulse(flag_servo_channel, 2450)  # Flag fully closed
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm fully closed
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid back to fully closed

def action43():
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
    time.sleep(0.4)
    pwm.setServoPulse(arm_servo_channel, 1700)  # Arm fully open
    time.sleep(0.2)
    pwm.setServoPulse(lid_servo_channel, 1500)  # Lid partially closes
    time.sleep(0.2)
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open again
    time.sleep(0.3)
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm fully closed
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid back to fully closed

def action44():
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
    time.sleep(0.2)
    pwm.setServoPulse(arm_servo_channel, 1700)  # Arm fully open
    time.sleep(0.1)
    pwm.setServoPulse(arm_servo_channel, 2300)  # Arm moves halfway back
    time.sleep(0.1)
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm fully closed
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid back to fully closed

def action45():
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
    time.sleep(0.5)
    pwm.setServoPulse(flag_servo_channel, 1500)  # Flag halfway up
    time.sleep(0.2)
    pwm.setServoPulse(flag_servo_channel, 2450)  # Flag fully closed
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid back to fully closed

def action46():
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
    time.sleep(0.2)
    pwm.setServoPulse(arm_servo_channel, 1800)  # Arm moves halfway open slowly
    time.sleep(0.5)
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm quickly retracts
    time.sleep(0.1)
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid back to fully closed

def action47():
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
    time.sleep(0.5)
    pwm.setServoPulse(arm_servo_channel, 1700)  # Arm fully open
    time.sleep(0.5)
    for _ in range(4):
        pwm.setServoPulse(flag_servo_channel, 1500)  # Flag halfway up
        time.sleep(0.2)
        pwm.setServoPulse(flag_servo_channel, 2450)  # Flag fully closed
        time.sleep(0.2)
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm fully closed
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid back to fully closed

def action48():
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
    time.sleep(0.1)
    pwm.setServoPulse(arm_servo_channel, 1700)  # Arm fully open
    time.sleep(0.5)
    pwm.setServoPulse(flag_servo_channel, 1500)  # Flag halfway up
    time.sleep(0.1)
    pwm.setServoPulse(flag_servo_channel, 2000)  # Flag slightly down
    time.sleep(0.1)
    pwm.setServoPulse(flag_servo_channel, 2450)  # Flag fully closed
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm fully closed
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid back to fully closed

def action49():
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
    time.sleep(0.3)
    pwm.setServoPulse(arm_servo_channel, 2000)  # Arm moves partially open
    time.sleep(0.2)
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm quickly retracts
    pwm.setServoPulse(flag_servo_channel, 1500)  # Flag halfway up
    time.sleep(0.5)
    pwm.setServoPulse(flag_servo_channel, 2450)  # Flag fully closed
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid back to fully closed

def action50():
    pwm.setServoPulse(lid_servo_channel, 1100)  # Lid fully open
    time.sleep(0.2)
    pwm.setServoPulse(arm_servo_channel, 1700)  # Arm fully open
    time.sleep(0.3)
    pwm.setServoPulse(flag_servo_channel, 1500)  # Flag halfway up
    time.sleep(0.3)
    pwm.setServoPulse(flag_servo_channel, 2450)  # Flag fully closed
    pwm.setServoPulse(arm_servo_channel, 2450)  # Arm fully closed
    pwm.setServoPulse(lid_servo_channel, 2400)  # Lid back to fully closed

# Main loop
import random
while True:
    if trigger_button.is_pressed:
        action = random.randint(1, 50)
        globals()[f'action{action}']()
