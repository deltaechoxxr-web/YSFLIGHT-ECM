#include "laser.h"

#include <algorithm>
#include <cmath>

namespace ysflight {

LaserWeapon::LaserWeapon()
    : LaserWeapon(LaserConfig{}) {}

LaserWeapon::LaserWeapon(const LaserConfig& config)
    : config_(config), energy_(config.maxEnergy) {}

double LaserWeapon::energy() const {
    return energy_;
}

double LaserWeapon::maxEnergy() const {
    return config_.maxEnergy;
}

double LaserWeapon::range() const {
    return config_.maxRange;
}

double LaserWeapon::cooldownRemaining() const {
    return cooldownRemaining_;
}

void LaserWeapon::update(double dt) {
    if (!std::isfinite(dt) || dt <= 0.0) {
        return;
    }

    cooldownRemaining_ = std::max(0.0, cooldownRemaining_ - dt);
    energy_ = std::min(config_.maxEnergy, energy_ + config_.rechargeRate * dt);
}

LaserShotResult LaserWeapon::fire(double targetDistance) {
    if (!std::isfinite(targetDistance) || targetDistance < 0.0 || targetDistance > config_.maxRange) {
        return {LaserFireStatus::OutOfRange, 0.0};
    }
    if (cooldownRemaining_ > 0.0) {
        return {LaserFireStatus::CoolingDown, 0.0};
    }
    if (energy_ < config_.energyPerShot) {
        return {LaserFireStatus::NoEnergy, 0.0};
    }

    energy_ -= config_.energyPerShot;
    cooldownRemaining_ = config_.cooldownSeconds;
    return {LaserFireStatus::Hit, config_.damagePerShot};
}

const char* toString(LaserFireStatus status) {
    switch (status) {
        case LaserFireStatus::Hit:
            return "HIT";
        case LaserFireStatus::OutOfRange:
            return "OUT OF RANGE";
        case LaserFireStatus::CoolingDown:
            return "COOLING DOWN";
        case LaserFireStatus::NoEnergy:
            return "NO ENERGY";
        default:
            return "UNKNOWN";
    }
}

} // namespace ysflight
