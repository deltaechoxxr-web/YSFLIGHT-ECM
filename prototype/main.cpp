#include "ecm.h"

#include <iomanip>
#include <iostream>

int main() {
    using namespace ysflight;

    std::cout << "YSFLIGHT ECM prototype v2\n";
    std::cout << "------------------------\n\n";

    EcmConfig cfg;
    cfg.maxEnergy = 120.0;
    cfg.drainRate = 10.0;
    cfg.rechargeRate = 14.0;
    cfg.power = 0.9;
    cfg.lowThreshold = 0.35;
    cfg.criticalThreshold = 0.15;

    AircraftEcm jammer(cfg);
    RadarLockModel radar(5000.0, 1.0, &jammer);

    std::cout << "CASE 1: ECM OFF\n";
    std::cout << "  state: " << toString(jammer.state()) << "\n";
    std::cout << "  effective radar range: " << std::fixed << std::setprecision(1) << radar.effectiveRange() << " m\n";
    std::cout << "  lock quality: " << radar.lockQuality() << "\n\n";

    jammer.toggle();
    jammer.update(1.0);

    std::cout << "CASE 2: ECM ACTIVE for 1 second\n";
    std::cout << "  state: " << toString(jammer.state()) << "\n";
    std::cout << "  energy: " << jammer.energy() << "\n";
    std::cout << "  effective power: " << jammer.effectivePower() << "\n";
    std::cout << "  effective radar range: " << radar.effectiveRange() << " m\n";
    std::cout << "  lock quality: " << radar.lockQuality() << "\n";
    std::cout << "  can maintain lock: " << (radar.canMaintainLock() ? "yes" : "no") << "\n";
    std::cout << "  lock broken: " << (radar.lockBroken() ? "yes" : "no") << "\n\n";

    for (int i = 0; i < 8; ++i) {
        jammer.update(1.0);
    }

    std::cout << "CASE 3: ECM energy depleted\n";
    std::cout << "  state: " << toString(jammer.state()) << "\n";
    std::cout << "  energy: " << jammer.energy() << "\n";
    std::cout << "  effective radar range: " << radar.effectiveRange() << " m\n";
    std::cout << "  lock quality: " << radar.lockQuality() << "\n";
    std::cout << "  can maintain lock: " << (radar.canMaintainLock() ? "yes" : "no") << "\n\n";

    jammer.update(6.0);
    std::cout << "CASE 4: ECM recharging\n";
    std::cout << "  state: " << toString(jammer.state()) << "\n";
    std::cout << "  energy: " << jammer.energy() << "\n";
    std::cout << "  effective radar range: " << radar.effectiveRange() << " m\n";
    std::cout << "  lock quality: " << radar.lockQuality() << "\n\n";

    jammer.toggle();
    for (int i = 0; i < 5; ++i) {
        jammer.update(1.0);
    }

    std::cout << "CASE 5: ECM forced active again\n";
    std::cout << "  state: " << toString(jammer.state()) << "\n";
    std::cout << "  energy: " << jammer.energy() << "\n";
    std::cout << "  effective radar range: " << radar.effectiveRange() << " m\n";
    std::cout << "  lock quality: " << radar.lockQuality() << "\n";
    std::cout << "  can maintain lock: " << (radar.canMaintainLock() ? "yes" : "no") << "\n";

    return 0;
}
