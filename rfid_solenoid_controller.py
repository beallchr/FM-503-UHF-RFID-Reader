#!/usr/bin/env python3
"""
RFID Tag Reader with Solenoid Control
Uses the FM-503 RFID reader and controls solenoids via GPIO
"""

import serial
from serial.tools.list_ports import comports
import time
import RPi.GPIO as GPIO
from reader import Reader

# ==================== CONFIGURATION ====================

# Serial Configuration
BAUDRATE = 38400
SERIAL_PORT = '/dev/ttyUSB0'  # Update this to match your device

# GPIO Pin Configuration for Solenoids
SOLENOID_PINS = {
    'solenoid_1': 17,  # GPIO 17
    'solenoid_2': 18,  # GPIO 18
}

# Solenoid activation time (seconds)
SOLENOID_ON_TIME = 0.5

# Read interval (seconds)
READ_INTERVAL = 0.1

# TX Power Level (-2 to 25 dB)
TX_POWER_LEVEL = 25

# ==================== GPIO SETUP ====================

def setup_gpio():
    """Initialize GPIO pins for solenoid control"""
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    for name, pin in SOLENOID_PINS.items():
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)
        print(f"Initialized {name} on GPIO pin {pin}")

def cleanup_gpio():
    """Clean up GPIO pins"""
    for pin in SOLENOID_PINS.values():
        GPIO.output(pin, GPIO.LOW)
    GPIO.cleanup()
    print("GPIO cleaned up")

def activate_solenoid(solenoid_name, duration=SOLENOID_ON_TIME):
    """
    Activate a solenoid for a specified duration
    
    Args:
        solenoid_name: Name of solenoid from SOLENOID_PINS dict
        duration: Time in seconds to keep solenoid active
    """
    if solenoid_name in SOLENOID_PINS:
        pin = SOLENOID_PINS[solenoid_name]
        print(f"Activating {solenoid_name} (GPIO {pin}) for {duration}s")
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(duration)
        GPIO.output(pin, GPIO.LOW)
    else:
        print(f"Error: Unknown solenoid '{solenoid_name}'")

def activate_all_solenoids(duration=SOLENOID_ON_TIME):
    """Activate all solenoids simultaneously"""
    print(f"Activating all solenoids for {duration}s")
    for pin in SOLENOID_PINS.values():
        GPIO.output(pin, GPIO.HIGH)
    time.sleep(duration)
    for pin in SOLENOID_PINS.values():
        GPIO.output(pin, GPIO.LOW)

# ==================== SERIAL SETUP ====================

def find_rfid_reader():
    """Attempt to find the RFID reader serial port"""
    ports = list(comports())
    print("\nAvailable serial ports:")
    for i, port in enumerate(ports):
        print(f"  {i}: {port.device} - {port.description}")
    
    if not ports:
        print("No serial ports found!")
        return None
    
    # Try to use configured port first
    for port in ports:
        if SERIAL_PORT in port.device:
            return port.device
    
    # Otherwise return first available
    return ports[0].device

def setup_serial(port):
    """
    Initialize serial connection to RFID reader
    
    Args:
        port: Serial port path
        
    Returns:
        Serial connection object or None if failed
    """
    try:
        ser = serial.Serial(port, BAUDRATE, timeout=1)
        print(f"\nSerial connection opened on {port}")
        print(f"Baudrate: {BAUDRATE}")
        
        # Clear buffers
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        
        return ser
    except Exception as e:
        print(f"Failed to open serial port {port}: {e}")
        return None

# ==================== TAG PROCESSING ====================

def process_tag_data(reader, tag_data):
    """
    Process tag data and trigger appropriate solenoid
    
    Args:
        reader: Reader object
        tag_data: Raw tag data from reader
    """
    # Convert to binary string
    bin_data = reader.convert_to_raw(tag_data)
    
    # Get hex representation for display
    hex_data = ''.join([hex(x)[2:].zfill(4).upper() for x in tag_data])
    
    print(f"\n{'='*60}")
    print(f"Tag Detected!")
    print(f"Hex: {hex_data}")
    print(f"Binary: {bin_data[:32]}... (truncated)")
    print(f"{'='*60}")
    
    # Simple logic: activate solenoid based on tag data
    # You can customize this logic based on your needs
    
    # Example 1: Activate based on first byte value
    first_byte = tag_data[0] >> 8
    solenoid_index = (first_byte % len(SOLENOID_PINS)) + 1
    solenoid_name = f'solenoid_{solenoid_index}'
    activate_solenoid(solenoid_name)
    
    # Example 2: Uncomment to activate all solenoids
    # activate_all_solenoids()
    
    # Example 3: Uncomment to activate specific solenoid
    # activate_solenoid('solenoid_1')

# ==================== MAIN PROGRAM ====================

def main():
    """Main program loop"""
    print("\n" + "="*60)
    print("RFID Reader with Solenoid Control")
    print("="*60)
    
    # Setup GPIO
    setup_gpio()
    
    # Find and setup serial port
    port = find_rfid_reader()
    if not port:
        print("Could not find RFID reader. Exiting.")
        cleanup_gpio()
        return
    
    ser = setup_serial(port)
    if not ser:
        print("Could not open serial connection. Exiting.")
        cleanup_gpio()
        return
    
    # Create reader object
    reader = Reader(ser)
    
    # Set TX power level
    print(f"\nSetting TX power to {TX_POWER_LEVEL}dB...")
    success = reader.set_tx_power_level(TX_POWER_LEVEL)
    if success:
        print(f"TX power set successfully")
    else:
        print(f"Warning: Failed to set TX power level")
    
    time.sleep(0.5)  # Give reader time to adjust
    
    print("\n" + "="*60)
    print("Starting tag reading loop...")
    print("Press Ctrl+C to exit")
    print("="*60 + "\n")
    
    tag_cache = {}  # Cache to avoid re-reading same tag immediately
    cache_timeout = 2.0  # Seconds before allowing same tag to trigger again
    
    try:
        while True:
            # Read TID bank
            tid_data = reader.read_TID_bank()
            
            if tid_data:
                # Convert to string for caching
                tag_id = str(tid_data)
                current_time = time.time()
                
                # Check if this tag was recently read
                if tag_id in tag_cache:
                    last_read = tag_cache[tag_id]
                    if (current_time - last_read) < cache_timeout:
                        # Skip this read - too soon
                        time.sleep(READ_INTERVAL)
                        continue
                
                # Update cache
                tag_cache[tag_id] = current_time
                
                # Process the tag
                process_tag_data(reader, tid_data)
                
                # Clean up old cache entries
                expired_tags = [k for k, v in tag_cache.items() 
                               if (current_time - v) > cache_timeout]
                for k in expired_tags:
                    del tag_cache[k]
            
            # Wait before next read
            time.sleep(READ_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    except Exception as e:
        print(f"\nError occurred: {e}")
    finally:
        # Cleanup
        print("Closing serial connection...")
        ser.close()
        print("Cleaning up GPIO...")
        cleanup_gpio()
        print("Done!")

# ==================== ENTRY POINT ====================

if __name__ == "__main__":
    main()
