# Wiring Diagram for 2 Solenoid Setup

## GPIO Pin Connections

```
Raspberry Pi GPIO Pins:
┌──────────────────────────────────┐
│                                  │
│  Pin 11 (GPIO 17) → Solenoid 1   │
│  Pin 12 (GPIO 18) → Solenoid 2   │
│  Pin 14 (GND)     → Common GND   │
│                                  │
└──────────────────────────────────┘
```

## Recommended Setup with Relay Module

```
┌─────────────┐     ┌──────────────┐     ┌────────────┐
│ Raspberry   │     │ Relay Module │     │ Solenoid 1 │
│ Pi          │     │              │     │            │
│             │     │              │     │            │
│ GPIO 17 ────┼────→│ IN1          │     │            │
│             │     │              │     │            │
│ GPIO 18 ────┼────→│ IN2      NO1 ├────→│ +          │
│             │     │              │     │            │
│ GND     ────┼────→│ GND      NO2 ├────→│ Solenoid 2 │
│             │     │              │     │ +          │
│             │     │              │     │            │
└─────────────┘     │ VCC          │     └────────────┘
                    │ (from Pi)    │
                    │              │     ┌────────────┐
                    │ COM1 ────────┼────→│ 12V/24V    │
                    │ COM2 ────────┼────→│ Power      │
                    │              │  ┌──│ Supply +   │
                    │ GND ─────────┼──┤  │            │
                    └──────────────┘  │  │ -      ────┼───→ Solenoid GND
                                      └──│            │
                                         └────────────┘
```

## Physical Pin Layout (Raspberry Pi Header)

```
      3.3V [ 1] [ 2] 5V
           [ 3] [ 4] 5V
           [ 5] [ 6] GND
           [ 7] [ 8] 
       GND [ 9] [10] 
 GPIO 17  [11] [12] ← GPIO 18 (Solenoid 2)
           ↑
    Solenoid 1
    
           [13] [14] ← GND
           [15] [16] 
      3.3V [17] [18] 
           [19] [20] GND
           ... (continues)
```

## Wiring Steps

### 1. Raspberry Pi to Relay Module
- GPIO 17 (Pin 11) → Relay Module IN1
- GPIO 18 (Pin 12) → Relay Module IN2  
- GND (Pin 14) → Relay Module GND
- 5V (Pin 4) → Relay Module VCC (if relay needs 5V trigger)

### 2. Relay Module to Solenoids
- Relay NO1 (Normally Open 1) → Solenoid 1 Positive
- Relay NO2 (Normally Open 2) → Solenoid 2 Positive
- Both solenoid negatives → Power supply ground

### 3. Power Supply to Relay Module
- Power Supply + (12V or 24V) → Relay Module COM1 and COM2
- Power Supply - → Solenoid grounds

## Important Notes

⚠️ **DO NOT connect solenoids directly to GPIO pins!**
- GPIO pins output 3.3V at max 16mA
- Most solenoids need 12-24V and draw 100-500mA
- Use a relay module or MOSFET driver board

⚠️ **Check your solenoid voltage requirements!**
- Common voltages: 12V DC, 24V DC, 120V AC, 240V AC
- Match your power supply to your solenoids
- For AC solenoids, use SSR (Solid State Relay)

⚠️ **Relay module trigger voltage**
- Most modules work with 3.3V or 5V trigger
- If using 5V trigger, may need 5V → 3.3V logic level shifter
- Or use relay module specifically designed for 3.3V

## Testing Connection

1. **Before connecting solenoids:**
   ```bash
   python3 test_solenoids.py
   ```
   Listen for relay clicking when solenoids "activate"

2. **Check with multimeter:**
   - Measure voltage across relay NO when GPIO goes HIGH
   - Should see 0V when OFF, solenoid voltage when ON

3. **Connect one solenoid first:**
   - Test with single solenoid before connecting both
   - Verify it activates/deactivates properly
   - Check for overheating in long activations

## Common Relay Modules

### 2-Channel 5V Relay Module (Common)
- Trigger: 5V (works with 3.3V usually)
- Load: 250VAC 10A or 30VDC 10A
- Cost: ~$5
- Perfect for this application

### 2-Channel 3.3V Relay Module (Better for Pi)
- Trigger: 3.3V
- Load: Same as above
- Cost: ~$7
- No voltage concerns

### Solid State Relay (SSR) - For AC Solenoids
- Silent operation (no clicking)
- Longer lifespan
- More expensive (~$10-15 each)
- Better for high-frequency switching

## Alternative: MOSFET Driver

For DC solenoids, you can use MOSFETs instead of relays:

```
GPIO 17 → 1kΩ resistor → MOSFET Gate
                         MOSFET Drain → Solenoid +
                         MOSFET Source → GND
                         
Power Supply + → Solenoid other terminal
Power Supply - → MOSFET Source (common GND with Pi)
```

Benefits:
- Faster switching
- No mechanical parts
- Silent
- Can do PWM (if needed)

Parts needed:
- Logic-level MOSFETs (e.g., IRL540N, IRLZ44N)
- Flyback diodes (e.g., 1N4007) across solenoid terminals
- 1kΩ gate resistors

## Safety Checklist

- [ ] Relay module power requirements checked
- [ ] Solenoid voltage matches power supply
- [ ] All grounds connected (Pi, relay, power supply)
- [ ] Flyback diodes in place (for inductive loads)
- [ ] Connections secure and insulated
- [ ] Test script runs without errors
- [ ] Manual shutoff switch accessible
- [ ] Fire extinguisher nearby (seriously!)

## Troubleshooting

**Relay clicks but solenoid doesn't activate:**
- Check power supply voltage
- Verify solenoid is getting voltage (use multimeter)
- Test solenoid with direct power connection

**GPIO script runs but relay doesn't click:**
- Check GPIO pin numbers (BCM vs Board numbering)
- Verify relay module is powered
- Test GPIO with LED first

**Solenoid activates but stays on:**
- Software issue - check script logic
- Relay stuck - may need replacement
- Add manual shutoff switch

**One solenoid works, other doesn't:**
- Swap relay channels to isolate problem
- Check wiring on non-working channel
- Verify GPIO pin is working (test with LED)
