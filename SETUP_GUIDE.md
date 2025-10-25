# RFID Solenoid Controller Setup Guide

## Overview
This script reads RFID tags using the FM-503 reader and controls solenoids via Raspberry Pi GPIO pins.

## Features
- Uses existing `reader.py` functions from the FM-503 library
- Simple GPIO control for up to 4 solenoids
- Tag caching to prevent duplicate triggers
- Configurable activation duration
- No GUI, LEDs, or speakers - just tag reading and solenoid control

## Hardware Requirements
- FM-503 UHF RFID Reader
- Raspberry Pi (any model with GPIO)
- 2 Solenoid valves
- Relay module or solenoid driver board
- Power supply for solenoids

## Wiring
Default GPIO pin assignments:
- Solenoid 1: GPIO 17
- Solenoid 2: GPIO 18

**Important:** Solenoids typically require more current than GPIO pins can provide. Use a relay module or driver board between the GPIO pins and solenoids.

## Installation

1. **Copy required files to your Raspberry Pi:**
   ```bash
   # You need these files from the original repo:
   # - reader.py
   # - tools.py
   # - knownTags.py (if using tag identification)
   # - MonzaR6.py (if reading Monza R6 tags)
   # - rfid_solenoid_controller.py (this script)
   ```

2. **Install dependencies:**
   ```bash
   pip3 install pyserial RPi.GPIO
   ```

3. **Find your RFID reader's serial port:**
   ```bash
   ls /dev/ttyUSB* /dev/ttyACM*
   # or
   python3 -m serial.tools.list_ports
   ```

4. **Edit the configuration in the script:**
   ```python
   SERIAL_PORT = '/dev/ttyUSB0'  # Update to your port
   TX_POWER_LEVEL = 25  # Adjust power level (-2 to 25 dB)
   SOLENOID_ON_TIME = 0.5  # Activation duration in seconds
   READ_INTERVAL = 0.1  # Time between reads
   ```

5. **Update GPIO pins if needed:**
   ```python
   SOLENOID_PINS = {
       'solenoid_1': 17,  # Change these to your wiring
       'solenoid_2': 18,
   }
   ```

## Usage

### Basic Usage
```bash
python3 rfid_solenoid_controller.py
```

### Run at startup (optional)
Add to `/etc/rc.local`:
```bash
python3 /home/pi/rfid_solenoid_controller.py &
```

Or create a systemd service:
```bash
sudo nano /etc/systemd/system/rfid-controller.service
```

Add:
```ini
[Unit]
Description=RFID Solenoid Controller
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/rfid_solenoid_controller.py
WorkingDirectory=/home/pi
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```

Then enable:
```bash
sudo systemctl enable rfid-controller.service
sudo systemctl start rfid-controller.service
```

## Customizing Solenoid Logic

The script includes three example activation patterns in the `process_tag_data()` function:

### Example 1: Activate based on tag data (default)
```python
first_byte = tag_data[0] >> 8
solenoid_index = (first_byte % len(SOLENOID_PINS)) + 1
solenoid_name = f'solenoid_{solenoid_index}'
activate_solenoid(solenoid_name)
```

### Example 2: Activate all solenoids
```python
activate_all_solenoids()
```

### Example 3: Activate specific solenoid
```python
activate_solenoid('solenoid_1')
```

### Custom Logic Examples

**Activate based on serial number:**
```python
from tools import extract_serial_num, segment_TID_data, interpret_lower_48_TID

bin_data = reader.convert_to_raw(tag_data)
segmented = segment_TID_data(True, bin_data)
interpreted = interpret_lower_48_TID(segmented)
sn = extract_serial_num(interpreted, bin_data)

if sn:
    sn_int = int(sn, 2)
    if sn_int < 1000:
        activate_solenoid('solenoid_1')
    elif sn_int < 2000:
        activate_solenoid('solenoid_2')
    # etc...
```

**Activate based on manufacturer:**
```python
from tools import segment_TID_data, interpret_lower_48_TID

bin_data = reader.convert_to_raw(tag_data)
segmented = segment_TID_data(True, bin_data)
interpreted = interpret_lower_48_TID(segmented)
manufacturer = interpreted[4]  # MDID

if manufacturer == "Impinj":
    activate_solenoid('solenoid_1')
elif manufacturer == "NXP Semiconductors":
    activate_solenoid('solenoid_2')
```

**Time-based activation:**
```python
import datetime

hour = datetime.datetime.now().hour
if 9 <= hour < 12:
    activate_solenoid('solenoid_1')
elif 12 <= hour < 17:
    activate_solenoid('solenoid_2')
```

## Configuration Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `BAUDRATE` | 38400 | Serial communication speed |
| `SERIAL_PORT` | /dev/ttyUSB0 | RFID reader serial port |
| `SOLENOID_ON_TIME` | 0.5 | Solenoid activation duration (seconds) |
| `READ_INTERVAL` | 0.1 | Time between tag reads (seconds) |
| `TX_POWER_LEVEL` | 25 | Reader transmit power (-2 to 25 dB) |
| `cache_timeout` | 2.0 | Seconds before re-triggering same tag |

## Troubleshooting

**No serial port found:**
- Check USB connection
- Run `ls /dev/ttyUSB*` to see available ports
- Check user permissions: `sudo usermod -a -G dialout $USER`

**GPIO permission errors:**
- Run with sudo: `sudo python3 rfid_solenoid_controller.py`
- Or add user to gpio group: `sudo usermod -a -G gpio $USER`

**Solenoids not activating:**
- Check GPIO wiring
- Verify relay module is powered
- Test GPIO manually: `gpio -g write 17 1`
- Check if solenoids require more voltage/current

**Tags not reading:**
- Adjust TX_POWER_LEVEL
- Ensure tags are ISO18000-6C / EPC GEN2 compatible
- Check antenna connection
- Verify reader serial connection

**Multiple reads of same tag:**
- Increase `cache_timeout` value
- Increase `READ_INTERVAL` value

## Safety Notes

1. **Solenoid Power:** Most solenoids require 12V-24V DC. Never connect directly to GPIO pins (max 3.3V).

2. **Current Draw:** Use a relay module or driver board with separate power supply for solenoids.

3. **Back-EMF Protection:** Solenoids generate voltage spikes. Use diodes or driver boards with built-in protection.

4. **Testing:** Test with one solenoid first before connecting all four.

5. **Shutoff:** The script turns off all solenoids on exit, but add a manual shutoff switch as backup.

## Additional Features to Add

Here are some ideas for extending the script:

- **Database logging:** Store tag reads with timestamps
- **Web interface:** Monitor activity remotely
- **Multiple activation patterns:** Different behaviors based on time/date
- **Tag whitelist/blacklist:** Only trigger for specific tags
- **Activation sequences:** Complex timing patterns
- **Remote control:** Trigger solenoids via network commands
- **Activity logging:** Track which tags triggered which solenoids

## License
This script is provided as-is. Use at your own risk.
