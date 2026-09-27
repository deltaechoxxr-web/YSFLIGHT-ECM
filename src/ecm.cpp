#include "ecm.h"

#include <algorithm>
#include <cmath>
#include <string>

namespace ysflight {

namespace {

inline double clamp01(double value) {
    return std::max(0.0, std::min(1.0, value));
}

} // namespace

AircraftEcm::AircraftEcm() {
    initialize();
}

AircraftEcm::AircraftEcm(const EcmConfig& config)
    : config_(config) {
    initialize();
}

void AircraftEcm::initialize() {
    energy_ = config_.maxEnergy;
    active_ = false;
}

bool AircraftEcm::hasEcm() const {
    return installed_;
}

bool AircraftEcm::isActive() const {
    return installed_ && active_ && energy_ > 0.0;
}

double AircraftEcm::energy() const {
    return energy_;
}

double AircraftEcm::maxEnergy() const {
    return config_.maxEnergy;
}

double AircraftEcm::power() const {
    return config_.power;
}

EcmState AircraftEcm::state() const {
    if (!installed_ || energy_ <= 0.0) {
        return EcmState::Off;
    }

    if (active_) {
        const double ratio = energy_ / config_.maxEnergy;
        if (ratio <= config_.criticalThreshold) {
            return EcmState::Critical;
        }
        if (ratio <= config_.lowThreshold) {
            return EcmState::Low;
        }
        return EcmState::Active;
    }

    return EcmState::Off;
}

void AircraftEcm::setInstalled(bool installed) {
    installed_ = installed;
    if (!installed_) {
        active_ = false;
        energy_ = 0.0;
    } else {
        energy_ = std::min(energy_, config_.maxEnergy);
    }
}

void AircraftEcm::toggle() {
    if (!installed_) {
        return;
    }
    active_ = !active_;
}

void AircraftEcm::update(double dt) {
    if (!installed_) {
        return;
    }

    if (active_) {
        energy_ -= config_.drainRate * dt;
        if (energy_ <= 0.0) {
            energy_ = 0.0;
            active_ = false;
        }
        return;
    }

    energy_ += config_.rechargeRate * dt;
    if (energy_ > config_.maxEnergy) {
        energy_ = config_.maxEnergy;
    }
}

double AircraftEcm::effectivePower() const {
    if (!isActive()) {
        return 0.0;
    }

    const double energyRatio = clamp01(energy_ / config_.maxEnergy);
    return config_.power * energyRatio;
}

double AircraftEcm::radarReductionFactor() const {
    if (!isActive()) {
        return 1.0;
    }

    const double ecm = effectivePower();
    return 1.0 - std::min(0.75, 0.8 * ecm);
}

double AircraftEcm::lockPenaltyFactor() const {
    if (!isActive()) {
        return 1.0;
    }

    const double ecm = effectivePower();
    return 1.0 - std::min(0.9, 0.85 * ecm);
}

bool AircraftEcm::shouldBreakLock() const {
    if (!isActive()) {
        return false;
    }

    const double ecm = effectivePower();
    return ecm >= 0.55;
}

RadarLockModel::RadarLockModel() = default;

RadarLockModel::RadarLockModel(double baseRange, double baseLockQuality, const AircraftEcm* targetEcm)
    : baseRange_(baseRange), baseLockQuality_(baseLockQuality), targetEcm_(targetEcm) {}

void RadarLockModel::setBaseRange(double baseRange) {
    baseRange_ = baseRange;
}

void RadarLockModel::setBaseLockQuality(double baseLockQuality) {
    baseLockQuality_ = clamp01(baseLockQuality);
}

void RadarLockModel::setTargetEcm(const AircraftEcm* targetEcm) {
    targetEcm_ = targetEcm;
}

double RadarLockModel::effectiveRange() const {
    double range = baseRange_;
    if (targetEcm_ != nullptr && targetEcm_->isActive()) {
        range *= targetEcm_->radarReductionFactor();
    }
    return std::max(0.0, range);
}

double RadarLockModel::lockQuality() const {
    double quality = baseLockQuality_;
    if (targetEcm_ != nullptr && targetEcm_->isActive()) {
        quality *= targetEcm_->lockPenaltyFactor();
    }
    return clamp01(quality);
}

bool RadarLockModel::canTrack() const {
    return effectiveRange() > 0.0;
}

bool RadarLockModel::canMaintainLock() const {
    if (targetEcm_ != nullptr && targetEcm_->shouldBreakLock()) {
        return lockQuality() >= 0.25;
    }
    return lockQuality() >= 0.15;
}

bool RadarLockModel::lockBroken() const {
    if (targetEcm_ == nullptr) {
        return false;
    }
    return targetEcm_->shouldBreakLock() && lockQuality() < 0.25;
}

std::string toString(EcmState state) {
    switch (state) {
        case EcmState::Off:
            return "OFF";
        case EcmState::Active:
            return "ACTIVE";
        case EcmState::Low:
            return "LOW";
        case EcmState::Critical:
            return "CRITICAL";
        default:
            return "UNKNOWN";
    }
}

} // namespace ysflight
