#!/usr/bin/env python
#
# Bitbang'd SPI interface with an MCP3008 ADC device
# MCP3008 is 8-channel 10-bit analog to digital converter
#  Connections are:
#     CLK => SCLK  
#     DOUT =>  MISO
#     DIN => MOSI
#     CS => CE0

import time
import sys
import spidev

spi_ch = 0 #using raspberry Pi's SPI channel 0 (chip enable 0)

spi = spidev.SpiDev()
spi.open(0, spi_ch)

def read_adc(adc_ch, vref=3.3):
    # ensure that ADC channel is 0 or 1 <-- assuming this has to do with layout
    if adc_ch != 0:
        adc_ch = 1
        
    # todo: make this for tcp
    #construct SPI message:
    # first bit is LOGIC HIGH - start according to TCP datasheeet needs to be rising edge
    # second bit is 1 for SINGLE mode.
    # third bit is channel
    # fourth bit: MSFB: 0 for LSB first
    # next 12 bits do not matter, so 0. just need to send clock pulses so MCP sends data back over Dout (MISO) line
    msg = 0b11
    msg = ((msg << 1) + adc_ch) << 5
    msg = [msg, 0b000000000000]
    reply = spi.xfer2(msg) #reply comes back to us as a list of 2 bytes (stored as 2 ints)
    
    #construct integer reply (2B)
    adc = 0
    for n in reply:
        adc = (adc << 8) + n
        
    #last bit irrelevant, not part of ADC value. shift:
    adc = adc >> 1
    
    # get percentage
    #calculate voltage from ADC value
    voltage = (vref * adc) / 1024 #1024 because MCP3002 is a 10-bit ADC
    
    return voltage

try:
    while True:
        adc_0 = read_adc(0)
        adc_1 = read_adc(1)
        print("Ch 0:", round(adc_0, 2), "V ch 1:", round(adc_1, 2), "V")
        time.sleep(0.2)
        
finally:
    GPIO.cleanup()
    
    
    
    
    

def buildReadCommand(channel):
    startBit = 0x01
    singleEnded = 0x08

    # Return python list of 3 bytes
    #   Build a python list using [1, 2, 3]
    #   First byte is the start bit
    #   Second byte contains single ended along with channel #
    #   3rd byte is 0
    return [startBit, singleEnded|(channel<<4), 0]
    
def processAdcValue(result):
    '''Take in result as array of three bytes. 
       Return the two lowest bits of the 2nd byte and
       all of the third byte'''
    byte2 = (result[1] & 0x03)
    return (byte2 << 8) | result[2]
        
def readAdc(channel):
    if ((channel > 7) or (channel < 0)):
        return -1
    r = spi.xfer2(buildReadCommand(channel))
    return processAdcValue(r)
        
if __name__ == '__main__':
    try:
        while True:
            val = readAdc(0)
            print ("ADC Result: ", str(val))
            time.sleep(5)
    except KeyboardInterrupt:
        spi.close() 
        sys.exit(0)