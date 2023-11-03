# this code is currently for python 2.7
from __future__ import print_function
from time import sleep
import numpy as np
from datetime import datetime

#import RPi.GPIO as GPIO
#import smbus

# i2c address-es
# not required?
I2C_WRITE_ADDR = 0xAE
I2C_READ_ADDR = 0xAF

# register address-es
REG_INTR_STATUS_1 = 0x00
REG_INTR_STATUS_2 = 0x01

REG_INTR_ENABLE_1 = 0x02
REG_INTR_ENABLE_2 = 0x03

REG_FIFO_WR_PTR = 0x04
REG_OVF_COUNTER = 0x05
REG_FIFO_RD_PTR = 0x06
REG_FIFO_DATA = 0x07
REG_FIFO_CONFIG = 0x08

REG_MODE_CONFIG = 0x09
REG_SPO2_CONFIG = 0x0A
REG_LED1_PA = 0x0C

REG_LED2_PA = 0x0D
REG_PILOT_PA = 0x10
REG_MULTI_LED_CTRL1 = 0x11
REG_MULTI_LED_CTRL2 = 0x12

REG_TEMP_INTR = 0x1F
REG_TEMP_FRAC = 0x20
REG_TEMP_CONFIG = 0x21
REG_PROX_INT_THRESH = 0x30
REG_REV_ID = 0xFE
REG_PART_ID = 0xFF

# currently not used
MAX_BRIGHTNESS = 255

SAMPLES_PER_SECOND_DIC = {50  :0 << 2,
                          100 :1 << 2,
                          200 :2 << 2,
                          400 :3 << 2,
                          800 :4 << 2,
                          1000:5 << 2,
                          1600:6 << 2,
                          3200:7 << 2}

SAMPLES_AVG_PER_FIFO_DIC = {1 :0 << 5,
                            2 :1 << 5,
                            4 :2 << 5,
                            8 :3 << 5,
                            16:4 << 5,
                            32:5 << 5}

class MAX30102():
    # by default, this assumes that physical pin 7 (GPIO 4) is used as interrupt
    # by default, this assumes that the device is at 0x57 on channel 1
    def __init__(self,samples_per_second, samples_avg_per_fifo, channel=1, address=0x57, gpio_pin=7):
        print("[SETUP]Channel: {0}, address: 0x{1:x}".format(channel, address))
        self.address = address
        self.channel = channel
        self.bus = smbus.SMBus(self.channel)
        self.interrupt = gpio_pin
        self.samples_per_second = samples_per_second
        self.samples_avg_per_fifo = samples_avg_per_fifo
        print("[SETUP]Data per second = {0}/{1} = {2}".format(samples_per_second,samples_avg_per_fifo,int(samples_per_second/samples_avg_per_fifo)))
        # set gpio mode
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.interrupt, GPIO.IN)

        self.reset()

        sleep(1)  # wait 1 sec

        # read & clear interrupt register (read 1 byte)
        reg_data = self.bus.read_i2c_block_data(self.address, REG_INTR_STATUS_1, 1)
        # print("[SETUP] reset complete with interrupt register0: {0}".format(reg_data))
        self.setup()
        print("[SETUP] setup complete")

    def shutdown(self):
        """
        Shutdown the device.
        """
        self.bus.write_i2c_block_data(self.address, REG_MODE_CONFIG, [0x80])

    def reset(self):
        """
        Reset the device, this will clear all settings,
        so after running this, run setup() again.
        """
        self.bus.write_i2c_block_data(self.address, REG_MODE_CONFIG, [0x40])

    def setup(self):
        """
        This will setup the device with the values written in sample Arduino code.
        """
        # INTR setting
        # 0xc0 : A_FULL_EN and PPG_RDY_EN = Interrupt will be triggered when
        # fifo almost full & new fifo data ready
        self.bus.write_i2c_block_data(self.address, REG_INTR_ENABLE_1, [0xe0])#0xc0
        self.bus.write_i2c_block_data(self.address, REG_INTR_ENABLE_2, [0x02])#0x00

        # FIFO_WR_PTR[4:0]
        self.bus.write_i2c_block_data(self.address, REG_FIFO_WR_PTR, [0x00])
        # OVF_COUNTER[4:0]
        self.bus.write_i2c_block_data(self.address, REG_OVF_COUNTER, [0x00])
        # FIFO_RD_PTR[4:0]
        self.bus.write_i2c_block_data(self.address, REG_FIFO_RD_PTR, [0x00])

        # 0b 0100 1111
        # sample avg = 4, fifo rollover = false, fifo almost full = 17
        self.bus.write_i2c_block_data(self.address, REG_FIFO_CONFIG, [0x0f | SAMPLES_AVG_PER_FIFO_DIC[self.samples_avg_per_fifo]])

        # 0x02 for red-only, 0x03 for SpO2 mode, 0x07 multimode LED
        self.bus.write_i2c_block_data(self.address, REG_MODE_CONFIG, [0x02])#0x03
        # 0b 0010 0111
        # SPO2_ADC range = 4096nA, SPO2 sample rate = 100Hz, LED pulse-width = 411uS
        self.bus.write_i2c_block_data(self.address, REG_SPO2_CONFIG, [0x23 | SAMPLES_PER_SECOND_DIC[self.samples_per_second]])#0x27

        # choose value for ~7mA for LED1
        self.bus.write_i2c_block_data(self.address, REG_LED1_PA, [0x24])
        # choose value for ~7mA for LED2
        self.bus.write_i2c_block_data(self.address, REG_LED2_PA, [0x24])
        # choose value fro ~25mA for Pilot LED
        self.bus.write_i2c_block_data(self.address, REG_PILOT_PA, [0x7f])

    # this won't validate the arguments!
    # use when changing the values from default
    def set_config(self, reg, value):
        self.bus.write_i2c_block_data(self.address, reg, value)

    def read_fifo(self, printflag = False):
        """
        This function will read the data register.
        """
        red_led = None
        ir_led = None

        # read 1 byte from registers (values are discarded)
        reg_INTR1 = self.bus.read_i2c_block_data(self.address, REG_INTR_STATUS_1, 1)
        reg_INTR2 = self.bus.read_i2c_block_data(self.address, REG_INTR_STATUS_2, 1)

        if printflag:
            print("FIFO Almost Full Flag:{0}".format((reg_INTR1 >> 7) & 1))
            print("New FIFO Data Ready:{0}".format((reg_INTR1 >> 6) & 1))
            print("Ambient Light Cancellation Overflow:{0}".format((reg_INTR1 >> 5) & 1))
            print("Power Ready Flag:{0}".format((reg_INTR1 >> 0) & 1))
            print("Internal Temperature Ready Flag:{0}".format((reg_INTR2 >> 1) & 1))

        # read 6-byte data from the device
        d = self.bus.read_i2c_block_data(self.address, REG_FIFO_DATA, 6)

        # mask MSB [23:18]
        red_led = (d[0] << 16 | d[1] << 8 | d[2]) & 0x03FFFF
        ir_led = (d[3] << 16 | d[4] << 8 | d[5]) & 0x03FFFF

        return red_led, ir_led

    def read_sequential(self, amount=100, printflag = False):
        """
        This function will read the red-led and ir-led `amount` times.
        This works as blocking function.
        """
        red_buf = []
        ir_buf = []
        for i in range(amount):
            while(GPIO.input(self.interrupt) == 1):
                # wait for interrupt signal, which means the data is available
                # do nothing here
                pass

            red, ir = self.read_fifo(printflag = printflag)

            red_buf.append(red)
            ir_buf.append(ir)

        return red_buf, ir_buf
    def get_bpm(self, amount=100, save=False, reversal = False):
        try:
            red, ir = self.read_sequential(amount)
        except Exception as e:
            print("get bpm data error:" + e)
            return -999        
        try:
            hr,peaks,peakinv = calc_ir(ir, int(self.samples_per_second/self.samples_avg_per_fifo), reversal = reversal)
        except Exception as e:
            print("calc bpm data error:" + e)
            return -999

        if save:
            with open("./irdata_{0}_{1}.csv".format(datetime.now().strftime("%Y%m%d%H%M%S"),int(hr)), "w") as f:
                f.write(str(hr) + "\n")
                f.write((",").join(map(str,peaks)))
                f.write("\n")       
                f.write((",").join(map(str,peakinv)))
                f.write("\n")       
                f.write((",").join(map(str,ir)))
        return hr

def AMPD(data):
    """
    实现AMPD算法
    :param data: 1-D numpy.ndarray 
    :return: 波峰所在索引值的列表
    """
    p_data = np.zeros_like(data, dtype=np.int32)
    count = data.shape[0]
    arr_rowsum = []
    for k in range(1, count // 2 + 1):
        row_sum = 0
        for i in range(k, count - k):
            if data[i] > data[i - k] and data[i] > data[i + k]:
                row_sum -= 1
        arr_rowsum.append(row_sum)
    min_index = np.argmin(arr_rowsum)
    max_window_length = min_index
    for k in range(1, max_window_length + 1):
        for i in range(k, count - k):
            if data[i] > data[i - k] and data[i] > data[i + k]:
                p_data[i] += 1
    return np.where(p_data == max_window_length)[0]

def calc_ir(ir, interval, reversal = True):
    peaks = AMPD(np.array(ir) * (-1 if reversal else 1))
    peakinv = []
    for i in range(1,len(peaks)):
        peakinv.append(peaks[i] -peaks[i-1])
    me = np.mean(np.array(peakinv))
    return interval * 60 / me, peaks, peakinv