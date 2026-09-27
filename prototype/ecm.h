#pragma once

#include <algorithm>
#include <cmath>
#include <string>

namespace ysflight {

enum class EcmState {
    Off,
    Active,
    Low,
    Critical
};

struct EcmConfig {
    double maxEnergy = 120.0;
    double drainRate = 8.0;
    double rechargeRate = 12.0;
    double power = 0.9;
    double lowThreshold = 0.35;
    double criticalThreshold = 0.15;
};

class AircraftEcm {
public:
    AircraftEcm();
    explicit AircraftEcm(const EcmConfig& config);

    void initialize();
    bool hasEcm() const;
    bool isActive() const;
    double energy() const;
    double maxEnergy() const;
    double power() const;
    EcmState state() const;

    void setInstalled(bool installed);
    void toggle();
    void update(double dt);
    double effectivePower() const;
    double radarReductionFactor() const;
    double lockPenaltyFactor() const;
    bool shouldBreakLock() const;

private:
    EcmConfig config_;
    bool installed_ = true;
    bool active_ = false;
    double energy_ = 0.0;
};

class RadarLockModel {
public:
    RadarLockModel();
    RadarLockModel(double baseRange, double baseLockQuality, const AircraftEcm* targetEcm = nullptr);

    void setBaseRange(double baseRange);
    void setBaseLockQuality(double baseLockQuality);
    void setTargetEcm(const AircraftEcm* targetEcm);

    double effectiveRange() const;
    double lockQuality() const;
    bool canTrack() const;
    bool canMaintainLock() const;
    bool lockBroken() const;

private:
    double baseRange_ = 5000.0;
    double baseLockQuality_ = 1.0;
    const AircraftEcm* targetEcm_ = nullptr;
};

std::string toString(EcmState state);

} // namespace ysflight
