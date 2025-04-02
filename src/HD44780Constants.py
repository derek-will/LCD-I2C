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

"""This file defines the HD44780 Instructions and Parameters."""

CLEAR_DISPLAY = const(0x01) # DB0
RETURN_HOME = const(0x02) # DB1

ENTRY_MODE = const(0x04) # DB2
ENTRY_MODE_INC = const(0x02) # DB1 - Increment option
ENTRY_MODE_SHIFT = const(0x01) # DB0 - Shift option

DISPLAY_CONTROL = const(0x08) # DB3
DISPLAY_ON = const(0x04) # DB2 - Turn display on
DISPLAY_SHOW_CURSOR = const(0x02) # DB1 - Show cursor
DISPLAY_BLINK_CURSOR = const(0x01) # DB0 - Blink cursor

SHIFT = const(0x10) # DB4
SHIFT_DISPLAY = const(0x08) # DB3 - Shift display
SHIFT_RIGHT = const(0x04) # DB2 - Shift right

FUNCTION_SET = const(0x20) # DB5
FUNCTION_8BIT_DL = const(0x10) # DB4 - 8-bit interface data length
FUNCTION_2_LINES = const(0x08) # DB3 - 2 lines display
FUNCTION_5x10_FONT = const(0x04) # DB2 - 5x10 character font

# Character Generator RAM
CGRAM_SET = const(0x40) # DB6
# Display Data RAM
DDRAM_SET = const(0x80) # DB7

# Initializing by instruction
RESET_CMD = const(0x30) 