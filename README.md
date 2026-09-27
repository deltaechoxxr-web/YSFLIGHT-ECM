# YSFLIGHT-ECM

Prototype of an ECM / jamming subsystem for a flight simulator.

This version is intentionally isolated from the original YSFLIGHT codebase and focuses on the logic behind:

- aircraft ECM activation / deactivation
- energy drain and recharge
- radar range degradation under jamming
- lock quality degradation and lock break behavior
- HUD-style state reporting

## Build

```bash
mkdir build
cd build
cmake ..
cmake --build .
./ysflight_ecm_demo
```

## Behavior model

The prototype uses these rules:

- ECM is treated as an aircraft system, not as a weapon.
- When ECM is active, the aircraft consumes energy.
- While active, the target's radar detection range drops.
- Missile lock quality also decreases and may break if the jammer is strong enough.
- If the ECM is switched off, the unit recharges.

## ECM States

- **OFF**: ECM is inactive or out of energy
- **ACTIVE**: Full power jamming, consuming energy quickly
- **LOW**: Energy below 35% threshold, reduced jamming effectiveness
- **CRITICAL**: Energy below 15% threshold, very weak jamming signal

## Radar Effects

When ECM is active:
- Effective radar range is reduced to 20-75% of normal, depending on energy
- Lock quality is degraded proportionally
- If ECM power exceeds 55%, lock can be broken entirely

## Notes

This is a design prototype for evaluating the behavior before integrating it into the full YSFLIGHT architecture.
