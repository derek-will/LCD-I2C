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

import utime
import HD44780Constants

class PCF8574TonHD44780:
    """
    PCF8574T GPIO extender interface for commanding/controlling a HD44780 LCD over I2C.
    
    Example Layout: Pi Pico <I2C> PCF8574T <IO> HD44780
    PCF8574T GPIO extender module uses 4-bit mode, HD44780 pins DB0-DB3 are not used.
    GPIO extender module wiring:                                               
                                                                          
     PCF8574T     HD44780                                                 
     ========     ======                                                 
        P0        RS (register selection)                                                   
        P1        RW (read/write)                                                    
        P2        E (clock enable)                                                 
        P3        BL (backlight)                                      
        P4        DB4 (data bus line 4)                                                
        P5        DB5 (data bus line 5)                                                    
        P6        DB6 (data bus line 6)                                                    
        P7        DB7 (data bus line 7)                                                     
                                                                       
    I2C-byte: DB7 DB6 DB5 DB4 BL E RW RS     
    """
    
    RS = const(0x01) # register select: set for data register
    RW = const(0x02) # read/write mode: set for read mode
    E = const(0x04) # clock enable: set for on
    BL = const(0x08) # backlight: set for on
    
    DB_HIGH = const(0xf0) # DB4-DB7 in high state
    
    # Set for 2-line display
    NUM_COLUMNS = const(40)
    NUM_ROWS = const(2)
    
    LONG_DELAY_US = 2160 # 1520 us when frequency is 270 kHz, 2160 us when frequency is 190 kHz (worst-case)
    SHORT_DELAY_US = 52 # 37 us when frequency is 270 kHz, 52 us when frequency is 190 kHz (worst-case)
        
    def __init__(self, i2c, i2c_addr, check_busy_flag):
        self.i2c = i2c
        self.addr = i2c_addr
        self.backlight_enable = True
        self.cursor_pos_x = 0
        self.cursor_pos_y = 0
        self.initialized = False
        self.check_busy_flag = check_busy_flag

    def write_init(self, value):
        """Write Initialization Data.
        Only DB7, DB6, DB5, DB4 are used.
        """
        upper_nibble = value & 0xf0
        
        # RS, RW Setup (Address Setup Time): RW, RS pins must be settled before setting clock enable high.
        self.i2c.writeto(self.addr, bytes([upper_nibble]))
        utime.sleep_us(1) # minimum address setup time is 60 ns
        
        # The clock of the HD44780 is a falling edge-triggered clock.
        # This means it will execute new instructions on the falling edge of the clock signal.
        # Therefore we send the nibble twice to properly pulse the clock enable pin.
        # First with clock enable set high, then with clock enable set low.   
        self.i2c.writeto(self.addr, bytes([upper_nibble | self.E]))
        utime.sleep_us(1) # minimum enable pulse width time is 450 ns
        self.i2c.writeto(self.addr, bytes([upper_nibble]))
        # enable fall time is worst-case 25 ns, plus address hold time of at least 20 ns
        # Address hold time: RW, RS pins must be settled after setting clock enable low
        utime.sleep_us(1)

    def write_4bit(self, value, write_dr):
        """Write value to Instruction Register (IR) when False or Data Register (DR) when True in 4-bit interface mode."""
        if not self.initialized:
            raise RuntimeError("Initialization function has not been called yet!")
        
        req = (self.RS if write_dr else 0) | (self.BL if self.backlight_enable else 0)
        
        # RS, RW Setup (Address Setup Time): RW, RS pins must be settled before setting clock enable high.
        self.i2c.writeto(self.addr, bytes([req]))
        utime.sleep_us(1) # minimum address setup time is 60 ns
        
        # We send each nibble twice to properly pulse the clock enable pin. See write_init function for more details.    
        upper_nibble = (value & 0xf0) | req
        self.i2c.writeto(self.addr, bytes([upper_nibble | self.E]))
        utime.sleep_us(1) # minimum enable pulse width time is 450 ns
        self.i2c.writeto(self.addr, bytes([upper_nibble]))
        # enable fall time is worst-case 25 ns, plus address hold time of at least 20 ns
        # Address hold time: RW, RS pins must be settled after setting clock enable low
        utime.sleep_us(1)
        
        lower_nibble = ((value & 0x0f) << 4) | req
        self.i2c.writeto(self.addr, bytes([lower_nibble | self.E]))
        utime.sleep_us(1) # minimum enable pulse width time is 450 ns
        self.i2c.writeto(self.addr, bytes([lower_nibble]))
        # enable fall time is worst-case 25 ns, plus address hold time of at least 20 ns
        # Address hold time: RW, RS pins must be settled after setting clock enable low
        utime.sleep_us(1)
        
        # instruction execution time delay
        if write_dr:
            self.execution_delay(self.SHORT_DELAY_US)
        else:
            if value == HD44780Constants.CLEAR_DISPLAY or value == HD44780Constants.RETURN_HOME:
                self.execution_delay(self.LONG_DELAY_US)
            else:
                self.execution_delay(self.SHORT_DELAY_US)

    def read_4bit(self, read_dr):
        """Read value from Instruction Register (IR) when False or Data Register (DR) when True in 4-bit interface mode."""
        if not self.initialized:
            raise RuntimeError("Initialization function has not been called yet!")
        
        req = self.RW | (self.RS if read_dr else 0) | (self.BL if self.backlight_enable else 0)
        
        # RS, RW Setup (Address Setup Time): RW, RS pins must be settled before setting clock enable high.
        self.i2c.writeto(self.addr, bytes([req]))
        utime.sleep_us(1) # minimum address setup time is 60 ns
        
        # Set clock enable high and set Data Bits 4-7 high.
        # Setting DB4-DB7 high is necessary in order to set P4-P7 high on the PCF8574.
        # In order to read a value from P4-P7, they must be set to high.
        # We set clock enable high to begin enable pulse. See write_init function for more details.
        self.i2c.writeto(self.addr, bytes([req | self.E | self.DB_HIGH ]))
        utime.sleep_us(1) # minimum enable pulse width time is 450 ns
        
        # Read upper nibble while clock enable is set high and Data Bits are set high.
        i2c_data = self.i2c.readfrom(self.addr, 1)      
        data = i2c_data[0] & 0xf0
        
        # Set clock enable low to complete enable pulse and also set Data Bits 4-7 low.
        self.i2c.writeto(self.addr, bytes([req]))
        # enable fall time is worst-case 25 ns, plus address hold time of at least 20 ns
        # Address hold time: RW, RS pins must be settled after setting clock enable low
        utime.sleep_us(1)
        
        # Set clock enable high to begin enable pulse and set Data Bits 4-7 high. See above for rationale.
        self.i2c.writeto(self.addr, bytes([req | self.E | self.DB_HIGH ]))
        utime.sleep_us(1) # minimum enable pulse width time is 450 ns
        
        # Read lower nibble while clock enable is set high and Data Bits are set high.
        i2c_data = self.i2c.readfrom(self.addr, 1)        
        data |= (i2c_data[0] >> 4)
        
        # Set clock enable low to complete enable pulse and also set Data Bits 4-7 low.
        self.i2c.writeto(self.addr, bytes([req]))
        # enable fall time is worst-case 25 ns, plus address hold time of at least 20 ns
        # Address hold time: RW, RS pins must be settled after setting clock enable low
        utime.sleep_us(1)
        
        # instruction execution time delay
        if read_dr:
            self.execution_delay(self.SHORT_DELAY_US)

        return data

    def initialize_lcd(self):
        """Initialize the LCD using the 4-bit mode initialization sequence.
        Additionally, configures the display for 2-lines and 5x8 font.
        """
        utime.sleep_ms(100) # wait for more than 40 ms after Vcc rises to 2.7V
        self.write_init(HD44780Constants.RESET_CMD) 
        utime.sleep_ms(5) # wait for more than 4.1 ms
        self.write_init(HD44780Constants.RESET_CMD) 
        utime.sleep_ms(1) # wait for more than 100 us
        self.write_init(HD44780Constants.RESET_CMD)
        utime.sleep_ms(1) # wait for more than 100 us 
        
        # Now set to 4-bit mode
        self.write_init(HD44780Constants.FUNCTION_SET)
        utime.sleep_ms(1) # wait for more than 100 us
        self.initialized = True
        
        # Set 4-bit, 2-line, 5x8 font
        self.write_4bit(HD44780Constants.FUNCTION_SET | HD44780Constants.FUNCTION_2_LINES, False)
        
    def reset_cursor_pos(self):
        """Returns cursor position to the left edge of the first line"""
        self.cursor_pos_x = 0
        self.cursor_pos_y = 0
        self.write_4bit(HD44780Constants.RETURN_HOME, False)
    
    def display_off(self):
        """Turns display off, cursor off - black screen"""
        self.write_4bit(HD44780Constants.DISPLAY_CONTROL, False)
        
    def display_on(self):
        """Turns display on, cursor defaults to off"""
        self.write_4bit(HD44780Constants.DISPLAY_CONTROL | HD44780Constants.DISPLAY_ON, False)
        
    def clear_display(self):
        """Clears display"""
        self.cursor_pos_x = 0
        self.cursor_pos_y = 0
        self.write_4bit(HD44780Constants.CLEAR_DISPLAY, False)

    def cursor_on(self, blink):
        """Makes cursor visible."""
        value = HD44780Constants.DISPLAY_CONTROL | HD44780Constants.DISPLAY_ON | HD44780Constants.DISPLAY_SHOW_CURSOR
        if blink:
            value |= HD44780Constants.DISPLAY_BLINK_CURSOR
            
        self.write_4bit(value, False)
    
    def cursor_off(self):
        """Makes cursor invisible"""
        self.display_on()
        
    def set_entry_mode(self, increment, shift_left):
        """Sets entry mode"""
        value = HD44780Constants.ENTRY_MODE
        if increment:
            value |= HD44780Constants.ENTRY_MODE_INC
        
        if shift_left:
            value |= HD44780Constants.ENTRY_MODE_SHIFT
            
        self.write_4bit(value, False)
        
    def backlight_on(self):
        """Turns on backlight"""
        self.backlight_enable = True
        self.i2c.writeto(self.addr, bytes([self.BL]))
        
    def backlight_off(self):
        """Turns off backlight"""
        self.backlight_enable = False
        self.i2c.writeto(self.addr, bytes([0]))
    
    def set_cursor_pos(self, x, y):
        """Set cursor position (0-based index)"""
        if x > NUM_COLUMNS - 1:
            raise ValueError("X coordinate is outside the bounds of the number of columns")
        
        if y > NUM_ROWS - 1:
            raise ValueError("Y coordinate is outside the bound of the number of rows")
        
        self.cursor_pos_x = x
        self.cursor_pos_y = y    
        ddram_addr = x
        if y == 1:
            ddram_addr += 0x40
        
        self.write_4bit(HD44780Constants.DDRAM_SET | ddram_addr, False)
        
    def write_char(self, char):
        """Writes a single character to the display"""
        if char == '\n':
            self.cursor_pos_x = NUM_COLUMNS
        else:
            self.write_4bit(ord(char), True)
            self.cursor_pos_x += 1
        
        if self.cursor_pos_x >= NUM_COLUMNS:
            self.cursor_pos_x = 0
            self.cursor_pos_y += 1
            
        if self.cursor_pos_y >= NUM_ROWS:
            self.cursor_pos_y = 0
            
        self.set_cursor_pos(self.cursor_pos_x, self.cursor_pos_y)
        
    def write_str(self, string):
        """Write a string of characters to the display"""
        for char in string:
            self.write_char(char)
            
    def shift_display(self, shift_right):
        """Shifts the display by one unit to either the left or the right"""
        value = HD44780Constants.SHIFT | HD44780Constants.SHIFT_DISPLAY
        if shift_right:
            value |= HD44780Constants.SHIFT_RIGHT
        self.write_4bit(value, False)
        
    def add_custom_char(self, index, char_pattern):
        """Adds a custom character to one of the 8 CGRAM locations.
        Access via chr(0) - chr(7)."""
        if index > 7 or index < 0:
            raise ValueError("Only index 0-7 are considered valid")
        if not isinstance(char_pattern, list):
            raise TypeError("Character pattern is expected to be a list")
        if len(char_pattern) != 8:
            raise ValueError("Character pattern must be array of length 8")
        
        cgram_addr = index << 3
        self.write_4bit(HD44780Constants.CGRAM_SET | cgram_addr, False)
        for i in range(8):
            self.write_4bit(char_pattern[i], True)
            
        self.set_cursor_pos(self.cursor_pos_x, self.cursor_pos_y)
    
    def read_instruction_register(self):
        """Reads the Busy Flag (BF) and Address Counter (AC) from the Instruction Register (IR).
        Bit 7 = BF
        Bit 6-0 = AC
        """
        return self.read_4bit(False)
    
    def read_data_register(self):
        """Reads data from the Data Register (DR)."""
        data = self.read_4bit(True)
        self.set_cursor_pos(self.cursor_pos_x, self.cursor_pos_y)
        return data

    def execution_delay(self, delay_usecs):
        """Instruction execution delay
        If check_busy_flag is set, then poll busy flag by reading from instruction register.
        Otherwise, just delay (sleep) for the specified microseconds.
        """
        if self.check_busy_flag:
            start_ticks = utime.ticks_us()
            while self.read_instruction_register() >> 7:
                if utime.ticks_diff(utime.ticks_us(), start_ticks) >= delay_usecs:
                    print("Warning: Busy flag did not clear in time...")
                    break   
        else:
            utime.sleep_us(delay_usecs)
        