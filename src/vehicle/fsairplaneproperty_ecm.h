// ============================================================
// ECM / JAMMING SYSTEM ADDITIONS
// Add these to class FsAirplaneProperty in fsairplaneproperty.h
// ============================================================

	// ECM / Jamming System - Characteristics
	YSBOOL chHasEcm;           // Aircraft equipped with ECM?
	double chEcmMaxEnergy;     // Maximum ECM energy (seconds)
	double chEcmDrainRate;     // Energy drain when active (units/sec)
	double chEcmRechargeRate;  // Energy recharge when inactive (units/sec)
	double chEcmPower;         // ECM effectiveness factor (0.0 to 1.0)

	// ECM / Jamming System - State
	YSBOOL staEcmActive;       // Currently active?
	double staEcmEnergy;       // Current energy level

	// ============================================================
	// PUBLIC METHODS
	// Add these to the public section of FsAirplaneProperty
	// ============================================================

	// ECM / Jamming System
	YSRESULT ToggleEcm(void);
	YSBOOL IsEcmActive(void) const;
	double GetEcmPower(void) const;
	void UpdateEcm(const double &dt);
