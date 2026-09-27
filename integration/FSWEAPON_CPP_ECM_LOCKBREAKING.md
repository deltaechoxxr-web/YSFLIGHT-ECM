# fsweapon.cpp - ECM Lock Breaking Logic

## Overview

This file contains the exact code changes needed for `src/core/fsweapon.cpp` to implement ECM lock breaking.

The logic works by:
1. Checking if the target aircraft has ECM active
2. Calculating a "lock quality" factor based on ECM power
3. If lock quality falls below a threshold, breaking the lock
4. Occasionally losing track if ECM is strong enough

## Key Function: `FsWeapon::IsOwnerStillHaveTarget()`

This function is called every frame to check if the missile should continue tracking its target.

Find this function in `fsweapon.cpp` and modify it to include ECM logic.

## Modified IsOwnerStillHaveTarget()

Replace or augment this function with:

```cpp
YSBOOL FsWeapon::IsOwnerStillHaveTarget(void)
{
    // Check if target still exists
    if(NULL==target)
    {
        return YSFALSE;
    }

    // Check if target is still alive
    if(YSTRUE!=target->IsAlive())
    {
        target=NULL;
        return YSFALSE;
    }

    // ECM Lock Breaking Logic
    // If the target has active ECM, degrade and potentially break the lock
    FsAirplane *targetAir = NULL;
    if(target->GetType()==FSEX_AIRPLANE)
    {
        targetAir = (FsAirplane *)target;
    }

    if(NULL != targetAir && YSTRUE == targetAir->Prop().IsEcmActive())
    {
        double ecmPower = targetAir->Prop().GetEcmPower();

        // Calculate lock quality degradation
        // ecmPower ranges 0.0 to ~0.9
        // lockFactor ranges 0.1 (weak ECM) to nearly 0.0 (strong ECM)
        double lockFactor = 1.0 - 0.85 * ecmPower;

        // If ECM is strong enough, break lock immediately
        if(lockFactor < 0.15)
        {
            target = NULL;
            return YSFALSE;
        }

        // If ECM is moderately strong, randomly break lock
        // The stronger the ECM, the higher the probability of losing lock
        if(lockFactor < 0.35)
        {
            // 50% to 80% chance of losing lock depending on ECM power
            double breakLockProbability = 0.8 * (1.0 - lockFactor);
            if(YsRandom() < breakLockProbability)
            {
                target = NULL;
                return YSFALSE;
            }
        }
    }

    return YSTRUE;
}
```

## Alternative: Less Aggressive Version

If you want ECM to be less punishing, use this variant:

```cpp
YSBOOL FsWeapon::IsOwnerStillHaveTarget(void)
{
    if(NULL==target)
    {
        return YSFALSE;
    }

    if(YSTRUE!=target->IsAlive())
    {
        target=NULL;
        return YSFALSE;
    }

    // Mild ECM lock breaking
    FsAirplane *targetAir = NULL;
    if(target->GetType()==FSEX_AIRPLANE)
    {
        targetAir = (FsAirplane *)target;
    }

    if(NULL != targetAir && YSTRUE == targetAir->Prop().IsEcmActive())
    {
        double ecmPower = targetAir->Prop().GetEcmPower();

        // Only break lock if ECM is extremely strong
        if(ecmPower > 0.75)
        {
            // 30% chance of losing lock if ECM is very strong
            if(YsRandom() < 0.3)
            {
                target = NULL;
                return YSFALSE;
            }
        }
    }

    return YSTRUE;
}
```

## Alternative: Guidance Degradation (Missile Accuracy Loss)

Instead of breaking lock, you can make the missile less accurate by modifying the guidance code:

```cpp
// In the missile guidance update section (typically in FsWeapon::Move())

if(NULL != target && FSEX_AIRPLANE == target->GetType())
{
    FsAirplane *tgtAir = (FsAirplane *)target;
    
    if(YSTRUE == tgtAir->Prop().IsEcmActive())
    {
        double ecmPower = tgtAir->Prop().GetEcmPower();
        
        // Degrade accuracy: add random noise to guidance
        double guidanceNoise = 100.0 * ecmPower;  // meters of random deviation
        YsVec3 targetPos = target->GetPosition();
        
        // Add random offset to target position for guidance
        targetPos.x += (YsRandom() - 0.5) * guidanceNoise;
        targetPos.y += (YsRandom() - 0.5) * guidanceNoise;
        targetPos.z += (YsRandom() - 0.5) * guidanceNoise;
        
        // Use modified target position for guidance calculations
    }
}
```

## Where to Add This

The `IsOwnerStillHaveTarget()` function is typically called in:
- `FsWeapon::Move()` - the main update loop
- Missile guidance calculation sections
- Any code that checks if a guided weapon still has a valid target

Look for existing calls like:
```cpp
if(YSTRUE != IsOwnerStillHaveTarget())
{
    // target lost or invalid
}
```

Your ECM logic will integrate naturally there.

## Integration Points

### Point 1: In FsWeapon::Move()

Find the section where the missile updates its guidance. Add:

```cpp
if(YSTRUE != IsOwnerStillHaveTarget())
{
    // Stop guiding, switch to ballistic
    target = NULL;
}
```

This is usually where lock verification happens.

### Point 2: In Radar Update

If there's a section that updates radar lock detection, add:

```cpp
double ecmPower = targetAircraft->Prop().GetEcmPower();
double lockFactor = 1.0 - 0.85 * ecmPower;

if(lockFactor < 0.25)
{
    // Cannot maintain lock
    break;  // or continue to next target
}
```

## Parameters You Can Tune

In the lock breaking logic:

| Parameter | Default | Effect |
|-----------|---------|--------|
| `0.85` in lockFactor | 0.85 | How much ECM degrades lock (higher = more degradation) |
| `0.15` threshold | 0.15 | Minimum lock quality to maintain (lower = easier to break) |
| `0.35` threshold | 0.35 | Threshold for random break chance |
| `0.8 * (1.0-lockFactor)` | varies | Probability calculation |

Example: To make ECM weaker, increase the threshold:
```cpp
if(lockFactor < 0.05)  // Instead of 0.15 - harder to break
{
    target = NULL;
    return YSFALSE;
}
```

## Testing

1. Create a test scenario with:
   - Player aircraft with ECM
   - Enemy aircraft with missiles

2. Test cases:
   - **ECM OFF**: missile locks and tracks normally
   - **ECM ACTIVE (high power)**: missile loses lock immediately
   - **ECM ACTIVE (medium power)**: missile randomly loses lock
   - **ECM LOW (depleting)**: missile weaker but still has chance to track
   - **ECM OFF (recharging)**: lock should be re-established

3. Verify behavior:
   - Launch missile while ECM is active → should lose lock
   - Launch missile while ECM is off → should track normally
   - Turn ECM on during missile flight → should break lock
   - Turn ECM off → lock can be re-established

## Important Notes

- The `YsRandom()` function returns a value 0.0 to 1.0
- Probability checks use `if(YsRandom() < probability)`
- Make sure to include the header for `FsAirplane` if not already included
- The lock breaking is probabilistic for realism (not always breaks immediately)
- Adjust thresholds based on your balance preferences

## Complete Integration Summary

1. Add ECM system to `FsAirplaneProperty` (header + cpp)
2. Update ECM energy every frame
3. Fill `FsInstrumentIndication` with ECM state
4. Show ECM on HUD
5. **Apply ECM lock breaking in `fsweapon.cpp` (this file)**
6. Optionally: apply radar range reduction elsewhere

With all these pieces together, you have a complete, functional ECM system.
