# RFID Solenoid Controller - Quick Start

This package contains a simplified RFID reader script that uses the FM-503 reader functions from the GitHub repo and controls solenoids via GPIO pins. No GUI, LEDs, or speakers - just tag reading and solenoid control.

## Files Included

1. **rfid_solenoid_controller.py** - Main script that reads tags and controls solenoids
2. **test_solenoids.py** - Test script to verify GPIO/solenoid connections
3. **SETUP_GUIDE.md** - Detailed setup and configuration guide

## Files You Need from the Original Repo

These files must be in the same directory as the main script:
- `reader.py` - Reader class with all tag reading functions
- `tools.py` - Helper functions for tag interpretation
- `knownTags.py` - Tag identification
- `MonzaR6.py` - Monza R6 tag specific functions

## Quick Setup

### 1. Install Dependencies
```bash
pip3 install pyserial RPi.GPIO
```

### 2. Test GPIO First
```bash
python3 test_solenoids.py
```

This will help you verify your solenoid connections before adding RFID reader complexity.

### 3. Configure the Main Script

Edit `rfid_solenoid_controller.py` and set:
- `SERIAL_PORT` - Your RFID reader's serial port (e.g., /dev/ttyUSB0)
- `SOLENOID_PINS` - GPIO pins for your solenoids
- `TX_POWER_LEVEL` - Reader power (0-25 dB)

### 4. Run the Main Script
```bash
python3 rfid_solenoid_controller.py
```

## Default GPIO Pin Assignments

| Solenoid | GPIO Pin | Physical Pin |
|----------|----------|--------------|
| Solenoid 1 | GPIO 17 | Pin 11 |
| Solenoid 2 | GPIO 18 | Pin 12 |

## How It Works

1. Script initializes GPIO pins and serial connection to RFID reader
2. Sets the transmit power level
3. Continuously reads for RFID tags (TID bank)
4. When tag detected, processes tag data and activates solenoid(s)
5. Uses cache to prevent duplicate triggers from same tag
6. Clean shutdown on Ctrl+C

## Customizing Solenoid Behavior

The `process_tag_data()` function in the main script controls which solenoid activates. Three examples are provided:

**Default:** Activates solenoid based on tag's first byte value
```python
first_byte = tag_data[0] >> 8
solenoid_index = (first_byte % len(SOLENOID_PINS)) + 1
activate_solenoid(f'solenoid_{solenoid_index}')
```

**Alternative:** Activate all solenoids
```python
activate_all_solenoids()
```

**Alternative:** Activate specific solenoid
```python
activate_solenoid('solenoid_1')
```

## Key Features

✓ Uses proven reader functions from FM-503 library  
✓ Simple GPIO control (no complex libraries needed)  
✓ Tag caching prevents duplicate triggers  
✓ Configurable activation duration  
✓ Clean error handling and shutdown  
✓ Test script for troubleshooting  
✓ No GUI/LED/speaker overhead  

## Troubleshooting

**Can't find serial port?**
```bash
ls /dev/ttyUSB* /dev/ttyACM*
python3 -m serial.tools.list_ports
```

**GPIO permission errors?**
```bash
sudo usermod -a -G gpio $USER
# or run with sudo
sudo python3 rfid_solenoid_controller.py
```

**Solenoids not activating?**
- Run test_solenoids.py first
- Check GPIO wiring
- Verify relay module has power
- Ensure relay module is connected between GPIO and solenoids

**Tags not reading?**
- Check serial connection
- Adjust TX_POWER_LEVEL
- Verify antenna connection
- Ensure tags are EPC GEN2 compatible

## Important Safety Notes

⚠️ **Never connect solenoids directly to GPIO pins!**  
Use a relay module or driver board with separate power supply.

⚠️ **Back-EMF Protection Required**  
Solenoids generate voltage spikes. Use driver boards with built-in protection or add flyback diodes.

⚠️ **Test First**  
Always test with test_solenoids.py before connecting RFID reader.

## Next Steps

For detailed configuration options, customization examples, and advanced features, see **SETUP_GUIDE.md**.

## Support

This is based on the FM-503 RFID reader library available at:
https://github.com/tmanabc123/FM-503-UHF-RFID-Reader

For hardware setup and RFID reader questions, refer to the original repository.
