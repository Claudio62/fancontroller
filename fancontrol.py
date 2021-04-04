#!/usr/bin/env python3
#
# use : python3 fancontrol.py [-v]
# otion -v print out every time slice the duty cycle of the fan, temperature and frequency clock of the CPU
# you can modify the output pin used for controlling FAN (default 18)
# time interval of the monitoring feature (default 5 sec)
#
# references
# https://howchoo.com/g/ote2mjkzzta/control-raspberry-pi-fan-temperature-python#write-the-fan-controller-code-optional
# https://it.howtodogood.com/90734-PWM-Regulated-Fan-Based-on-CPU-Temperature-for-Ras-80#menu-4
# https://www.instructables.com/PWM-Regulated-Fan-Based-on-CPU-Temperature-for-Ras/
# http://raspi.tv/2013/rpi-gpio-0-5-2a-now-has-software-pwm-how-to-use-it

import RPi.GPIO as GPIO # always needed with RPi.GPIO  
import subprocess
import time
import sys
import signal

SLEEP_INTERVAL = 5      # (seconds) How often we check the core temperature.
FAN_GPIO_PIN   = 18     #  17  # Which GPIO pin you're using to control the fan.
FAN_PWM_FREQ   = 50     # 50 Hz
FAN_PWM_DUTY   = 50     # duty cycle default 50%
VERBOUSE       = 0



#===============================================================================
# manage SIGTERM to correct exit from script
#===============================================================================
class GracefulKiller:
  kill_now = False
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self,signum, frame):
    self.kill_now = True

#===============================================================================
# return CPU temperature
#===============================================================================
def get_temp():
    output = subprocess.run(['vcgencmd', 'measure_temp'], capture_output=True)
    temp_str = output.stdout.decode()
    try:
        return float(temp_str.split('=')[1].split('\'')[0])
    except (IndexError, ValueError):
        raise RuntimeError('Could not parse temperature output.')


#===============================================================================
# return CPU temperature
#===============================================================================
def get_cpu_clock():
    output = subprocess.run(['vcgencmd', 'measure_clock', 'arm'], capture_output=True)
    freq_arm = output.stdout.decode()
    try:
        return float(freq_arm.split('=')[1].split('\'')[0])
    except (IndexError, ValueError):
        raise RuntimeError('Could not parse cpu frequency.')

#===============================================================================
# return duty cycle in temperature function
# new duty cycle = (Tcpu - 25°C) * 3
#===============================================================================
def get_duty(temp):
    deltaT = temp - 25
    if (deltaT) <= 0:
        return 0
    duty = deltaT * 3
    if (duty > 100):
        duty = 100
    return duty
    
# ==============================================================================
# ==============================================================================
#                                S T A R T
# ==============================================================================
# ==============================================================================
if __name__ == '__main__':

    arguments=len(sys.argv)-1
      
    for i, arg in enumerate(sys.argv):
        #print(f"Argument {i:>6}: {arg}")
        if arg[0:2] == "-v":
            VERBOUSE = 1
            print("Verbouse : On")
        if arg[0:2] == "-t":
            SLEEP_INTERVAL = float(arg[2:])
            print ("Interval time :",SLEEP_INTERVAL)
                    
    killer = GracefulKiller()        

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)                  # choose BCM or BOARD numbering schemes. I use BCM  

    GPIO.setup(FAN_GPIO_PIN, GPIO.OUT)      # set GPIO 18 as an output. You can use any GPIO port  

    p = GPIO.PWM(FAN_GPIO_PIN, FAN_PWM_FREQ)# create an object p for PWM on port 25 at 50 Hertz
                                            # you can have more than one of these, but they need  
                                            # different names for each port   
                                            # e.g. p1, p2, motor, servo1 etc.  
    p.start(FAN_PWM_DUTY)                   # start the PWM on 50 percent duty cycle  
                                            # duty cycle value can be 0.0 to 100.0%, floats are OK
                                            
        
    while not killer.kill_now:
        temp = get_temp()
        duty = get_duty(temp)
        p.ChangeDutyCycle(duty)
        freq = get_cpu_clock()/1e6
        if VERBOUSE:
            print('cpu temp = ',temp,' duty cycle = ', round(duty,2), ' clock arm = ',round(freq,0))
        time.sleep(SLEEP_INTERVAL)
    p.stop()                                # stop the PWM output  
    GPIO.cleanup()                          # when your program exits, tidy up after yourself  



