#pragma once

namespace ysflight {

struct LaserConfig {
    double maxEnergy = 100.0;
    double energyPerShot = 20.0;
    double rechargeRate = 8.0;
    double cooldownSeconds = 2.0;
    double maxRange = 3000.0;
    double damagePerShot = 25.0;
};

enum class LaserFireStatus {
    Hit,
    OutOfRange,
    CoolingDown,
    NoEnergy
};

struct LaserShotResult {
    LaserFireStatus status;
    double damage;
};

class LaserWeapon {
public:
    LaserWeapon();
    explicit LaserWeapon(const LaserConfig& config);

    double energy() const;
    double maxEnergy() const;
    double range() const;
    double cooldownRemaining() const;
    void update(double dt);
    LaserShotResult fire(double targetDistance);

private:
    LaserConfig config_;
    double energy_ = 0.0;
    double cooldownRemaining_ = 0.0;
};

const char* toString(LaserFireStatus status);

} // namespace ysflight
