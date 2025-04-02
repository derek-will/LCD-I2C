# BSD 3-Clause License
# 
# Copyright (c) 2025, Derek Will
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import machine
import utime
from PCF8574TonHD44780 import PCF8574TonHD44780

sda = machine.Pin(0)
scl = machine.Pin(1)
i2c = machine.I2C(0, sda=sda, scl=scl, freq=400000)

lcd = PCF8574TonHD44780(i2c, 0x27, True)
lcd.initialize_lcd()

lcd.display_off()
lcd.clear_display()
lcd.cursor_on(False)
lcd.reset_cursor_pos()
lcd.set_entry_mode(True, False)

lcd.set_cursor_pos(4, 1)
lcd.write_str('Hi World!')

for _ in range(6):
    lcd.shift_display(True)
    utime.sleep(2)

for _ in range(6):
    lcd.shift_display(False)
    utime.sleep(2)

pattern = [0x00, 0x00, 0x0A, 0x0A, 0x00, 0x11, 0x0E, 0x00]
lcd.add_custom_char(0, pattern)
lcd.write_char(chr(0))


lcd.set_cursor_pos(4, 1)

cmd_info = lcd.read_instruction_register()
print ("BF:" + str(cmd_info >> 7))
print ("AC:" + hex(cmd_info & 0x7f))
data_info = lcd.read_data_register()
print (chr(data_info))

lcd.set_cursor_pos(1, 0)
lcd.write_str('Guten Tag')

lcd.set_cursor_pos(1, 0)
cmd_info = lcd.read_instruction_register()
print ("BF:" + str(cmd_info >> 7))
print ("AC:" + hex(cmd_info & 0x7f))
data_info = lcd.read_data_register()
print (chr(data_info))

lcd.cursor_off()

utime.sleep(2)
lcd.backlight_off()
utime.sleep(2)
lcd.backlight_on()
utime.sleep(2)
lcd.backlight_off()
utime.sleep(2)
lcd.backlight_on()

