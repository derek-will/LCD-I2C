## LCD-I2C

This repository contains a MicroPython library for commanding a HD44780 Liquid Crystal Display (LCD) controller via a PCF8574T GPIO expander. A PCF8574 GPIO expander can be accessed via a I2C bus. This repository includes the library and some example code. The library was developed and tested using a Raspberry Pi Pico.

Using this library you can utilize any of the HD44780 LCD controller instructions indicated below. 

### Feature Chart

| HD44780 Instruction         | Supported?         | 
|:----------------------------|:-------------------|
| Clear Display               | :heavy_check_mark: |
| Return Home                 | :heavy_check_mark: |
| Entry Mode Set              | :heavy_check_mark: |
| Display On/Off Control      | :heavy_check_mark: |
| Cursor or Display Shift     | :heavy_check_mark: |
| Function Set                | :heavy_check_mark: |
| Set CGRAM Address           | :heavy_check_mark: |
| Set DDRAM Address           | :heavy_check_mark: |
| Read Busy Flag & Address    | :heavy_check_mark: |
| Write Data to CG/DDRAM      | :heavy_check_mark: |
| Read Data from CG/DDRAM     | :heavy_check_mark: |
| Initializing By Instruction | :heavy_check_mark: |

In addition, turning the LCD backlight on and off is supported.

### Example Code Snippet

```python
import machine
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
```

### Additional Information:

* [License](LICENSE.md)
