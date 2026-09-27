# fsairplaneproperty.h - ECM Integration Snippet

This file contains the exact code changes needed for `src/vehicle/fsairplaneproperty.h`.

## Changes Required

### Section 1: Add member variables (after line ~483, in the Radar section)

Locate this section:
```cpp
    // Radar
    YSBOOL chHasBombingRadar;
    YSBOOL chHasGroundRadar;
    YSBOOL chHasAirRadar;
```

Add after it:
```cpp
    // ECM / Jamming System
    YSBOOL chHasEcm;
    double chEcmMaxEnergy;
    double chEcmDrainRate;
    double chEcmRechargeRate;
    double chEcmPower;

    YSBOOL staEcmActive;
    double staEcmEnergy;
```

### Section 2: Add public function declarations (after line ~586, near ToggleLandingLight)

Locate this section:
```cpp
    YSRESULT ToggleLight(void);
    YSRESULT ToggleNavLight(void);
    YSRESULT ToggleBeacon(void);
    YSRESULT ToggleStrobe(void);
    YSRESULT ToggleLandingLight(void);
```

Add after it:
```cpp
    // ECM / Jamming System
    YSRESULT ToggleEcm(void);
    YSBOOL IsEcmActive(void) const;
    double GetEcmPower(void) const;
    void UpdateEcm(const double &dt);
```

## Complete Modified Section (Copy-Paste Ready)

If you want to copy the complete modified radar + ECM section, use this:

```cpp
    // Radar
    YSBOOL chHasBombingRadar;
    YSBOOL chHasGroundRadar;
    YSBOOL chHasAirRadar;

    // ECM / Jamming System
    YSBOOL chHasEcm;
    double chEcmMaxEnergy;
    double chEcmDrainRate;
    double chEcmRechargeRate;
    double chEcmPower;

    YSBOOL staEcmActive;
    double staEcmEnergy;
```

And for the function declarations:

```cpp
    YSRESULT ToggleLight(void);
    YSRESULT ToggleNavLight(void);
    YSRESULT ToggleBeacon(void);
    YSRESULT ToggleStrobe(void);
    YSRESULT ToggleLandingLight(void);

    // ECM / Jamming System
    YSRESULT ToggleEcm(void);
    YSBOOL IsEcmActive(void) const;
    double GetEcmPower(void) const;
    void UpdateEcm(const double &dt);
```

That's all that's needed in the header file!
