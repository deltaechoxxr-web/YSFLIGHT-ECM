# YSFLIGHT ECM System Patches

These patches add a complete Electronic Countermeasures (ECM) / Jamming system to YSFLIGHT.

## Installation

### Automatic (Linux/Mac)

1. Copy the `patches/` directory to the root of your YSFLIGHT repository
2. Run:
```bash
bash patches/APPLY_PATCHES.sh
```

### Manual (Windows or step-by-step)

1. Copy `patches/` to your YSFLIGHT root
2. Apply each patch individually using `patch` command or manually:

```bash
# Using patch command
patch -p1 < patches/fsairplaneproperty.h.patch
patch -p1 < patches/fsairplaneproperty.cpp.patch
patch -p1 < patches/fsinstreading.h.patch
patch -p1 < patches/fsweapon.cpp.patch
```

Or apply manually by copying the changes from each `.patch` file.

## After Applying Patches

### 1. Add UpdateEcm() call in FsAirplaneProperty::Move()

Find the function `FsAirplaneProperty::Move()` in `src/vehicle/fsairplaneproperty.cpp`

Look for where other state updates happen, and add:

```cpp
UpdateEcm(dt);
```

This should be called every frame to update ECM energy.

### 2. Fill ECM state in cockpit display

Find where `FsInstrumentIndication` is populated with aircraft data.

Add this code:

```cpp
if(air->Prop().IsEcmActive())
{
    double p = air->Prop().GetEcmPower();
    if(p > 0.55)
    {
        inst.ecmState = FsInstrumentIndication::FSECM_ACTIVE;
    }
    else if(p > 0.15)
    {
        inst.ecmState = FsInstrumentIndication::FSECM_LOW;
    }
    else
    {
        inst.ecmState = FsInstrumentIndication::FSECM_CRITICAL;
    }
    inst.ecmPower = p;
}
else
{
    inst.ecmState = FsInstrumentIndication::FSECM_OFF;
    inst.ecmPower = 0.0;
}
```

### 3. Display ECM state on HUD (optional)

Where you render HUD text, add:

```cpp
switch(inst.ecmState)
{
case FsInstrumentIndication::FSECM_OFF:
    // Draw "ECM OFF"
    break;
case FsInstrumentIndication::FSECM_ACTIVE:
    // Draw "ECM ACTIVE"
    break;
case FsInstrumentIndication::FSECM_LOW:
    // Draw "ECM LOW"
    break;
case FsInstrumentIndication::FSECM_CRITICAL:
    // Draw "ECM CRITICAL"
    break;
}
```

## Features

✅ **ECM Toggle** - Turn ECM on/off
✅ **Energy System** - Limited ECM energy with drain/recharge
✅ **Missile Lock Breaking** - Guided missiles lose lock when ECM is active
✅ **Lock Degradation** - Lock quality degrades based on ECM power
✅ **Realistic Behavior** - Probabilistic lock breaking based on ECM strength
✅ **HUD Display** - ECM status visible on instrument panel

## Configuration

Edit these values in `fsairplaneproperty.cpp` Initialize() to tune:

```cpp
chEcmMaxEnergy   = 120.0;     // Total ECM time (seconds)
chEcmDrainRate   = 8.0;       // Drain speed when active (units/sec)
chEcmRechargeRate= 12.0;      // Recharge speed when off (units/sec)
chEcmPower       = 0.9;       // Effectiveness (0.0-1.0)
```

## Lock Breaking Parameters

Edit in `fsweapon.cpp` IsOwnerStillHaveTarget():

```cpp
double lockFactor = 1.0 - 0.85 * ecmPower;  // 0.85 = degradation strength
if(lockFactor < 0.15)  // 0.15 = immediate break threshold
if(lockFactor < 0.35)  // 0.35 = random break threshold
```

Higher thresholds = easier to break lock
Lower thresholds = harder to break lock

## Testing

1. Compile YSFLIGHT
2. Create a scenario with:
   - Player aircraft with ECM
   - Enemy aircraft with guided missiles
3. Test cases:
   - Launch missile with ECM OFF → should lock and track
   - Launch missile with ECM ON (high power) → should lose lock
   - Launch missile, turn ECM ON → should break lock

## Troubleshooting

### Patch fails to apply
- Make sure you're in the YSFLIGHT root directory
- Check that file paths match your version
- Apply manually by copying code from `.patch` files

### Compilation errors
- Ensure all files are properly saved
- Check for missing includes or typos
- Verify function signatures match

### ECM not working
- Verify `UpdateEcm(dt)` is called in Move()
- Check that `ecmState` is filled correctly
- Ensure guided missiles use `IsOwnerStillHaveTarget()`

## Files Modified

- `src/vehicle/fsairplaneproperty.h` - ECM members and functions
- `src/vehicle/fsairplaneproperty.cpp` - ECM implementation
- `src/externalconsole/fsinstreading.h` - HUD state
- `src/core/fsweapon.cpp` - Lock breaking logic

## License

These patches are provided as-is for integration into YSFLIGHT.
