#!/usr/bin/env python3
"""
GPIO Solenoid Test Script
Test solenoid connections without RFID reader
"""

import RPi.GPIO as GPIO
import time
import sys

# GPIO Pin Configuration (should match your main script)
SOLENOID_PINS = {
    'solenoid_1': 17,
    'solenoid_2': 18,
}

def setup_gpio():
    """Initialize GPIO pins"""
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    for name, pin in SOLENOID_PINS.items():
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)
        print(f"✓ Initialized {name} on GPIO pin {pin}")

def cleanup_gpio():
    """Clean up GPIO pins"""
    for pin in SOLENOID_PINS.values():
        GPIO.output(pin, GPIO.LOW)
    GPIO.cleanup()

def test_individual_solenoids():
    """Test each solenoid individually"""
    print("\n" + "="*60)
    print("Testing Individual Solenoids")
    print("="*60)
    
    duration = 0.5
    
    for name, pin in SOLENOID_PINS.items():
        print(f"\nActivating {name} (GPIO {pin}) for {duration}s...")
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(duration)
        GPIO.output(pin, GPIO.LOW)
        print(f"✓ {name} test complete")
        time.sleep(0.5)  # Brief pause between tests

def test_all_solenoids():
    """Test all solenoids simultaneously"""
    print("\n" + "="*60)
    print("Testing All Solenoids Simultaneously")
    print("="*60)
    
    duration = 0.5
    
    print(f"\nActivating ALL solenoids for {duration}s...")
    for pin in SOLENOID_PINS.values():
        GPIO.output(pin, GPIO.HIGH)
    
    time.sleep(duration)
    
    for pin in SOLENOID_PINS.values():
        GPIO.output(pin, GPIO.LOW)
    
    print("✓ All solenoids test complete")

def test_sequence():
    """Test solenoids in sequence"""
    print("\n" + "="*60)
    print("Testing Solenoid Sequence")
    print("="*60)
    
    duration = 0.3
    
    print("\nRunning sequence (1 -> 2 -> 3 -> 4)...")
    for name, pin in sorted(SOLENOID_PINS.items()):
        print(f"  → {name}")
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(duration)
        GPIO.output(pin, GPIO.LOW)
        time.sleep(0.1)
    
    print("✓ Sequence test complete")

def continuous_test():
    """Continuous cycling test"""
    print("\n" + "="*60)
    print("Continuous Cycling Test")
    print("Press Ctrl+C to stop")
    print("="*60)
    
    cycle = 0
    try:
        while True:
            cycle += 1
            print(f"\nCycle {cycle}:")
            
            for name, pin in sorted(SOLENOID_PINS.items()):
                print(f"  {name}...", end='', flush=True)
                GPIO.output(pin, GPIO.HIGH)
                time.sleep(0.2)
                GPIO.output(pin, GPIO.LOW)
                print(" ✓")
                time.sleep(0.1)
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print(f"\n\nStopped after {cycle} cycles")

def interactive_test():
    """Interactive solenoid control"""
    print("\n" + "="*60)
    print("Interactive Solenoid Control")
    print("="*60)
    print("\nCommands:")
    print("  1-2  : Test individual solenoid")
    print("  a    : Test all solenoids")
    print("  s    : Test sequence")
    print("  c    : Continuous cycling")
    print("  q    : Quit")
    print("="*60)
    
    while True:
        try:
            cmd = input("\nEnter command: ").strip().lower()
            
            if cmd == 'q':
                break
            elif cmd == 'a':
                test_all_solenoids()
            elif cmd == 's':
                test_sequence()
            elif cmd == 'c':
                continuous_test()
            elif cmd in ['1', '2']:
                solenoid_name = f'solenoid_{cmd}'
                pin = SOLENOID_PINS[solenoid_name]
                print(f"\nActivating {solenoid_name} (GPIO {pin})...")
                GPIO.output(pin, GPIO.HIGH)
                time.sleep(0.5)
                GPIO.output(pin, GPIO.LOW)
                print("✓ Done")
            else:
                print("Invalid command. Try again.")
                
        except KeyboardInterrupt:
            print("\n")
            break

def main():
    """Main test menu"""
    print("\n" + "="*60)
    print("GPIO Solenoid Test Script")
    print("="*60)
    
    # Setup GPIO
    print("\nInitializing GPIO...")
    setup_gpio()
    
    print("\nSelect test mode:")
    print("  1. Test individual solenoids")
    print("  2. Test all solenoids")
    print("  3. Test sequence")
    print("  4. Continuous cycling")
    print("  5. Interactive mode")
    print("  6. Full test suite (runs all tests)")
    
    try:
        choice = input("\nEnter choice (1-6): ").strip()
        
        if choice == '1':
            test_individual_solenoids()
        elif choice == '2':
            test_all_solenoids()
        elif choice == '3':
            test_sequence()
        elif choice == '4':
            continuous_test()
        elif choice == '5':
            interactive_test()
        elif choice == '6':
            print("\nRunning full test suite...")
            test_individual_solenoids()
            time.sleep(1)
            test_all_solenoids()
            time.sleep(1)
            test_sequence()
            print("\n✓ Full test suite complete!")
        else:
            print("Invalid choice")
            
    except KeyboardInterrupt:
        print("\n\nTest interrupted")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        print("\nCleaning up GPIO...")
        cleanup_gpio()
        print("Done!")

if __name__ == "__main__":
    main()
