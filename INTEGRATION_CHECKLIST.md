# Complete ECM Integration Checklist

## Files to Modify

### 1. `src/vehicle/fsairplaneproperty.h`
- [ ] Add ECM member variables
- [ ] Add ECM function declarations

### 2. `src/vehicle/fsairplaneproperty.cpp`
- [ ] Initialize ECM in `Initialize()`
- [ ] Add `ToggleEcm()` implementation
- [ ] Add `IsEcmActive()` implementation
- [ ] Add `GetEcmPower()` implementation
- [ ] Add `UpdateEcm(double dt)` implementation
- [ ] Call `UpdateEcm(dt)` in main update loop

### 3. `src/externalconsole/fsinstreading.h`
- [ ] Add `ECMSTATE` enum to `FsInstrumentIndication`
- [ ] Add `ecmState` member variable
- [ ] Add `ecmPower` member variable

### 4. Instrument/HUD Update Code
- [ ] Fill `ecmState` based on aircraft ECM status
- [ ] Fill `ecmPower` value
- [ ] Display ECM state on HUD

### 5. `src/core/fsweapon.cpp`
- [ ] Modify `IsOwnerStillHaveTarget()` to check ECM
- [ ] Add lock breaking logic
- [ ] Test with guided missiles

### 6. Radar/Lock Detection Code (if applicable)
- [ ] Apply `radarFactor` to reduce detection range
- [ ] Apply `lockFactor` to reduce lock quality
- [ ] Break lock if factor too low

## Verification Steps

1. **Compilation**
   - [ ] Code compiles without errors
   - [ ] No undefined reference errors

2. **Basic Functionality**
   - [ ] Player aircraft can toggle ECM with button/key
   - [ ] ECM energy drains when active
   - [ ] ECM energy recharges when inactive
   - [ ] Energy stops at 0 or max

3. **HUD Display**
   - [ ] ECM state shows on HUD
   - [ ] ECM OFF when inactive
   - [ ] ECM ACTIVE when running above 55% power
   - [ ] ECM LOW when running 15-55% power
   - [ ] ECM CRITICAL when running below 15% power

4. **Radar Effects**
   - [ ] Enemy radar range reduced when ECM active
   - [ ] Radar range returns to normal when ECM off

5. **Lock Breaking**
   - [ ] Missile loses lock if ECM power too high
   - [ ] Missile loses lock randomly with medium ECM
   - [ ] Missile tracks normally without ECM
   - [ ] Lock can be re-established when ECM off

6. **Edge Cases**
   - [ ] ECM correctly disables at 0 energy
   - [ ] ECM recharges from empty
   - [ ] Multiple aircraft with ECM don't interfere
   - [ ] ECM doesn't affect bombs/unguided weapons

## Parameter Tuning

If gameplay feels wrong, adjust these in order:

1. **ECM too strong?**
   - Increase `chEcmDrainRate` (drain faster)
   - Decrease `chEcmMaxEnergy` (less total time)
   - Decrease `chEcmPower` (less effectiveness)
   - Increase lock quality threshold in `IsOwnerStillHaveTarget()`

2. **ECM too weak?**
   - Decrease `chEcmDrainRate` (drain slower)
   - Increase `chEcmMaxEnergy` (more total time)
   - Increase `chEcmPower` (more effectiveness)
   - Decrease lock quality threshold in `IsOwnerStillHaveTarget()`

3. **Recharge too slow?**
   - Increase `chEcmRechargeRate`

4. **Lock breaking too random?**
   - Increase thresholds (0.15 → 0.25) to make it harder to break
   - Decrease thresholds (0.15 → 0.05) to make it easier to break

## Final Validation

- [ ] Create test flight scenario
- [ ] Verify player aircraft has ECM
- [ ] Verify enemy aircraft has missiles
- [ ] Test all ECM state transitions
- [ ] Test lock breaking at different ECM levels
- [ ] Test HUD display accuracy
- [ ] Test network sync (if applicable)
- [ ] Performance test (no lag from ECM)

## Deployment

- [ ] All changes committed to version control
- [ ] Tested on target platform (Windows/Linux/Mac)
- [ ] Documented in changelog
- [ ] Ready for integration into main branch
