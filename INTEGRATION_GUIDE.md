# Integration Guide: ECM System for YSFLIGHT

## Overview

This document describes how to integrate the ECM (Electronic Countermeasures) system into the YSFLIGHT flight simulator.

ECM is implemented as an **aircraft subsystem**, not as a weapon type. It operates independently of the munition systems and serves to reduce enemy radar detection and missile lock quality.

## File Modifications

### 1. `src/vehicle/fsairplaneproperty.h`

Add the following members to `FsAirplaneProperty` class (around line 483, after radar properties):

```cpp
    // ECM / Jamming System
    YSBOOL chHasEcm;              // Aircraft has ECM installed
    double chEcmMaxEnergy;        // Maximum ECM energy (seconds)
    double chEcmDrainRate;        // Energy consumption rate (units/sec)
    double chEcmRechargeRate;     // Energy recharge rate when inactive (units/sec)
    double chEcmPower;            // ECM power factor (0..1)

    YSBOOL staEcmActive;          // Current ECM state
    double staEcmEnergy;          // Current ECM energy
```

Add the following public function declarations (around line 586, after ToggleLandingLight):

```cpp
    YSRESULT ToggleEcm(void);
    YSBOOL IsEcmActive(void) const;
    double GetEcmPower(void) const;
    void UpdateEcm(const double &dt);
```

### 2. `src/vehicle/fsairplaneproperty.cpp`

**In `FsAirplaneProperty::Initialize()` function:**

Add initialization (around line 385, after radar initialization):

```cpp
    // ECM / Jamming System
    chHasEcm = YSTRUE;
    chEcmMaxEnergy = 120.0;
    chEcmDrainRate = 8.0;
    chEcmRechargeRate = 12.0;
    chEcmPower = 0.9;

    staEcmActive = YSFALSE;
    staEcmEnergy = chEcmMaxEnergy;
```

**Add these function implementations (at the end of the file, before closing):**

```cpp
YSRESULT FsAirplaneProperty::ToggleEcm(void)
{
    if(chHasEcm==YSFALSE)
    {
        return YSERR;
    }

    staEcmActive = !staEcmActive;
    if(staEcmActive && staEcmEnergy <= 0.0)
    {
        staEcmActive = YSFALSE;
        return YSERR;
    }
    return YSOK;
}

YSBOOL FsAirplaneProperty::IsEcmActive(void) const
{
    return chHasEcm==YSTRUE && staEcmActive==YSTRUE && staEcmEnergy>0.0;
}

double FsAirplaneProperty::GetEcmPower(void) const
{
    if(IsEcmActive()==YSFALSE)
    {
        return 0.0;
    }
    return chEcmPower * (staEcmEnergy / chEcmMaxEnergy);
}

void FsAirplaneProperty::UpdateEcm(const double &dt)
{
    if(chHasEcm==YSFALSE)
    {
        staEcmActive=YSFALSE;
        staEcmEnergy=0.0;
        return;
    }

    if(staEcmActive)
    {
        staEcmEnergy -= chEcmDrainRate * dt;
        if(staEcmEnergy <= 0.0)
        {
            staEcmEnergy = 0.0;
            staEcmActive = YSFALSE;
        }
    }
    else
    {
        staEcmEnergy += chEcmRechargeRate * dt;
        if(staEcmEnergy > chEcmMaxEnergy)
        {
            staEcmEnergy = chEcmMaxEnergy;
        }
    }
}
```

### 3. Call UpdateEcm() in the main move loop

In `FsAirplaneProperty::Move()` (usually around line 1800+), add after other state updates:

```cpp
    UpdateEcm(dt);
```

This ensures the ECM energy is updated every simulation step.

### 4. Integration with Radar/Lock Logic

In any code that calculates radar detection range or missile lock quality, add:

```cpp
    double ecmPower = targetAircraft->Prop().GetEcmPower();
    double radarFactor = 1.0 - 0.75 * ecmPower;
    double lockFactor = 1.0 - 0.85 * ecmPower;
```

Then apply these factors:

```cpp
    effectiveRadarRange *= radarFactor;  // Reduce detection range
    lockQuality *= lockFactor;           // Reduce lock quality
    
    if(lockFactor < 0.25)
    {
        // Break lock if ECM power is too strong
        targetAircraft = NULL;
    }
```

### 5. HUD Display (Optional)

In HUD rendering code (typically `src/externalconsole/fsinstreading.h` or relevant display function):

```cpp
    if(player->Prop().IsEcmActive())
    {
        double ecmPower = player->Prop().GetEcmPower();
        if(ecmPower > 0.55)
        {
            // Display "ECM ACTIVE"
        }
        else if(ecmPower > 0.15)
        {
            // Display "ECM LOW"
        }
        else
        {
            // Display "ECM CRITICAL"
        }
    }
    else
    {
        // Display "ECM OFF" or nothing
    }
```

## Control Mapping

To add a key binding for ECM toggle:

In flight control input handler (typically in `src/core/` or `src/` main loop):

```cpp
    if(ecmToggleKeyPressed)
    {
        playerAirplane->Prop().ToggleEcm();
    }
```

## Parameters

You can adjust these values in `Initialize()` to tune the system:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `chEcmMaxEnergy` | 120.0 | Max ECM operating time (seconds) |
| `chEcmDrainRate` | 8.0 | Energy consumed per second while active |
| `chEcmRechargeRate` | 12.0 | Energy recharged per second while inactive |
| `chEcmPower` | 0.9 | Effectiveness multiplier (0..1) |

### Radar/Lock Factors

In step 4 above:
- `0.75` in radar factor: How much ECM can reduce radar range (75% max reduction)
- `0.85` in lock factor: How much ECM can degrade lock (85% max degradation)
- `0.25` threshold: Minimum lock quality to maintain lock

You can adjust these values for different balance:

- Increase multipliers → ECM more powerful
- Decrease multipliers → ECM less powerful
- Raise threshold → Harder to break lock
- Lower threshold → Easier to break lock

## Testing

1. **Compile with modifications**
2. **Create a test scenario:**
   - One player aircraft with ECM
   - One enemy aircraft with missiles
3. **Test cases:**
   - ECM OFF: enemy locks normally
   - ECM ON: enemy lock becomes harder
   - ECM energy low: less effective jamming
   - ECM energy depleted: ECM turns off automatically
   - ECM OFF: energy slowly recharges

## Network / Replay Considerations

For multiplayer and flight replay support, you may need to:

1. Add ECM state to network encoding (`NetworkEncode()` / `NetworkDecode()`)
2. Save/restore ECM state in flight recordings
3. Increment network version if needed

For an initial local-play implementation, these can be deferred.

## Summary

This integration provides:
- ✅ ECM activation/deactivation toggle
- ✅ Energy drain and recharge
- ✅ Radar detection reduction
- ✅ Missile lock degradation and break capability
- ✅ Automatic state management
- ✅ Realistic jamming behavior

The system is designed to be non-invasive and coexist with existing YSFLIGHT systems without breaking compatibility.
