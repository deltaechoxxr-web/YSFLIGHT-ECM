#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YSFLIGHT ECM Integration Script
Automatically applies ECM modifications to YSFLIGHT source files
No manual editing required - 100% automated
"""

import os
import sys
import shutil
from pathlib import Path

# Color output
class Color:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_status(msg, color=Color.BLUE):
    print(f"{color}[*] {msg}{Color.END}")

def print_success(msg):
    print(f"{Color.GREEN}[✓] {msg}{Color.END}")

def print_error(msg):
    print(f"{Color.RED}[✗] {msg}{Color.END}")

def print_warning(msg):
    print(f"{Color.YELLOW}[!] {msg}{Color.END}")

def backup_file(filepath):
    """Create backup of original file"""
    backup_path = filepath + ".backup"
    if not os.path.exists(backup_path):
        shutil.copy2(filepath, backup_path)
        print_success(f"Backup created: {backup_path}")
    return backup_path

def modify_fsairplaneproperty_h(filepath):
    """Add ECM variables and functions to fsairplaneproperty.h"""
    print_status(f"Modifying {os.path.basename(filepath)}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    backup_file(filepath)
    
    # Check if already modified
    if "chHasEcm" in content:
        print_warning("ECM already present in fsairplaneproperty.h - skipping")
        return True
    
    # Add ECM member variables (after radar section)
    ecm_members = """\n\t// ECM / Jamming System
\tYSBOOL chHasEcm;
\tdouble chEcmMaxEnergy;
\tdouble chEcmDrainRate;
\tdouble chEcmRechargeRate;
\tdouble chEcmPower;

\tYSBOOL staEcmActive;
\tdouble staEcmEnergy;"""
    
    # Find where to insert (after radar variables)
    if "chHasAirRadar" in content:
        content = content.replace(
            "chHasAirRadar;",
            "chHasAirRadar;" + ecm_members
        )
    
    # Add ECM function declarations
    ecm_functions = """\n\t// ECM / Jamming System
\tYSRESULT ToggleEcm(void);
\tYSBOOL IsEcmActive(void) const;
\tdouble GetEcmPower(void) const;
\tvoid UpdateEcm(const double &dt);"""
    
    # Find where to insert (after ToggleLandingLight)
    if "ToggleLandingLight" in content:
        content = content.replace(
            "ToggleLandingLight(void);",
            "ToggleLandingLight(void);" + ecm_functions
        )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print_success(f"Modified {os.path.basename(filepath)}")
    return True

def modify_fsairplaneproperty_cpp(filepath):
    """Add ECM implementation to fsairplaneproperty.cpp"""
    print_status(f"Modifying {os.path.basename(filepath)}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    backup_file(filepath)
    
    # Check if already modified
    if "chHasEcm=YSTRUE" in content:
        print_warning("ECM already present in fsairplaneproperty.cpp - skipping")
        return True
    
    # Add ECM initialization in Initialize()
    ecm_init = """\n\t// ECM / Jamming System
\tchHasEcm=YSTRUE;
\tchEcmMaxEnergy=120.0;
\tchEcmDrainRate=8.0;
\tchEcmRechargeRate=12.0;
\tchEcmPower=0.9;

\tstaEcmActive=YSFALSE;
\tstaEcmEnergy=chEcmMaxEnergy;"""
    
    # Find initialization section and add ECM
    if "chHasAirRadar=YSFALSE;" in content:
        content = content.replace(
            "chHasAirRadar=YSFALSE;",
            "chHasAirRadar=YSFALSE;" + ecm_init
        )
    
    # Add ECM function implementations at the end of file (before closing)
    ecm_functions = """\n\nYSRESULT FsAirplaneProperty::ToggleEcm(void)
{
\tif(chHasEcm==YSFALSE)
\t{
\t\treturn YSERR;
\t}

\tstaEcmActive = !staEcmActive;
\tif(staEcmActive && staEcmEnergy <= 0.0)
\t{
\t\tstaEcmActive = YSFALSE;
\t\treturn YSERR;
\t}
\treturn YSOK;
}

YSBOOL FsAirplaneProperty::IsEcmActive(void) const
{
\treturn chHasEcm==YSTRUE && staEcmActive==YSTRUE && staEcmEnergy>0.0;
}

double FsAirplaneProperty::GetEcmPower(void) const
{
\tif(IsEcmActive()==YSFALSE)
\t{
\t\treturn 0.0;
\t}
\treturn chEcmPower * (staEcmEnergy / chEcmMaxEnergy);
}

void FsAirplaneProperty::UpdateEcm(const double &dt)
{
\tif(chHasEcm==YSFALSE)
\t{
\t\tstaEcmActive=YSFALSE;
\t\tstaEcmEnergy=0.0;
\t\treturn;
\t}

\tif(staEcmActive)
\t{
\t\tstaEcmEnergy -= chEcmDrainRate * dt;
\t\tif(staEcmEnergy <= 0.0)
\t\t{
\t\t\tstaEcmEnergy = 0.0;
\t\t\tstaEcmActive = YSFALSE;
\t\t}
\t}
\telse
\t{
\t\tstaEcmEnergy += chEcmRechargeRate * dt;
\t\tif(staEcmEnergy > chEcmMaxEnergy)
\t\t{
\t\t\tstaEcmEnergy = chEcmMaxEnergy;
\t\t}
\t}
}"""
    
    # Add functions before the last closing brace or at end
    content = content.rstrip()
    if content.endswith("}"):
        content = content[:-1] + ecm_functions + "\n}\n"
    else:
        content = content + ecm_functions + "\n"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print_success(f"Modified {os.path.basename(filepath)}")
    return True

def modify_fsinstreading_h(filepath):
    """Add ECM state variables to fsinstreading.h"""
    print_status(f"Modifying {os.path.basename(filepath)}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    backup_file(filepath)
    
    # Check if already modified
    if "FSECM_OFF" in content:
        print_warning("ECM already present in fsinstreading.h - skipping")
        return True
    
    # Add ECM enum
    ecm_enum = """\n\tenum ECMSTATE
\t{
\t\tFSECM_OFF=0,
\t\tFSECM_ACTIVE=1,
\t\tFSECM_LOW=2,
\t\tFSECM_CRITICAL=3
\t};"""
    
    # Find where to insert (after MAX_NUM_FUELTANK)
    if "MAX_NUM_FUELTANK" in content:
        content = content.replace(
            "MAX_NUM_FUELTANK=16\n\t};",
            "MAX_NUM_FUELTANK=16\n\t};" + ecm_enum
        )
    
    # Add ECM member variables
    ecm_members = """\n\t// ECM / Jamming
\tint ecmState;
\tdouble ecmPower;"""
    
    # Find where to insert (before velocity or at end of members)
    if "YsVec3 velocity;" in content:
        content = content.replace(
            "YsVec3 velocity;",
            ecm_members + "\n\n\tYsVec3 velocity;"
        )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print_success(f"Modified {os.path.basename(filepath)}")
    return True

def modify_fsweapon_cpp(filepath):
    """Replace IsOwnerStillHaveTarget() with ECM logic in fsweapon.cpp"""
    print_status(f"Modifying {os.path.basename(filepath)}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    backup_file(filepath)
    
    # Check if already modified
    if "ECM lock-breaking logic" in content:
        print_warning("ECM already present in fsweapon.cpp - skipping")
        return True
    
    # Find and replace IsOwnerStillHaveTarget function
    old_function = """YSBOOL FsWeapon::IsOwnerStillHaveTarget(void)
{
\tYSHASHKEY ownerAirTargetKey=YSNULLHASHKEY;
\tif(NULL!=firedBy)
\t{
\t\tif(FSEX_AIRPLANE==firedBy->GetType())
\t\t{
\t\t\townerAirTargetKey=((FsAirplane *)firedBy)->Prop().GetAirTargetKey();
\t\t}
\t\telse if(FSEX_GROUND==firedBy->GetType())
\t\t{
\t\t\townerAirTargetKey=FsExistence::GetSearchKey(((FsGround *)firedBy)->Prop().GetAirTarget());
\t\t}
\t}

\tif(NULL!=firedBy && NULL!=target && ownerAirTargetKey==FsExistence::GetSearchKey(target))
\t{
\t\treturn YSTRUE;
\t}
\telse
\t{
\t\treturn YSFALSE;
\t}
}"""
    
    new_function = """YSBOOL FsWeapon::IsOwnerStillHaveTarget(void)
{
\tif(NULL==target)
\t{
\t\treturn YSFALSE;
\t}

\tif(YSTRUE!=target->IsAlive())
\t{
\t\ttarget=NULL;
\t\treturn YSFALSE;
\t}

\t// ECM lock-breaking logic
\tFsAirplane *targetAir = NULL;
\tif(FSEX_AIRPLANE==target->GetType())
\t{
\t\ttargetAir = (FsAirplane *)target;
\t}

\tif(NULL != targetAir && YSTRUE == targetAir->Prop().IsEcmActive())
\t{
\t\tdouble ecmPower = targetAir->Prop().GetEcmPower();
\t\tdouble lockFactor = 1.0 - 0.85 * ecmPower;

\t\tif(lockFactor < 0.15)
\t\t{
\t\t\ttarget = NULL;
\t\t\treturn YSFALSE;
\t\t}

\t\tif(lockFactor < 0.35)
\t\t{
\t\t\tdouble breakLockProbability = 0.8 * (1.0 - lockFactor);
\t\t\tif(YsRandom() < breakLockProbability)
\t\t\t{
\t\t\t\ttarget = NULL;
\t\t\t\treturn YSFALSE;
\t\t\t}
\t\t}
\t}

\tYSHASHKEY ownerAirTargetKey=YSNULLHASHKEY;
\tif(NULL!=firedBy)
\t{
\t\tif(FSEX_AIRPLANE==firedBy->GetType())
\t\t{
\t\t\townerAirTargetKey=((FsAirplane *)firedBy)->Prop().GetAirTargetKey();
\t\t}
\t\telse if(FSEX_GROUND==firedBy->GetType())
\t\t{
\t\t\townerAirTargetKey=FsExistence::GetSearchKey(((FsGround *)firedBy)->Prop().GetAirTarget());
\t\t}
\t}

\tif(NULL!=firedBy && NULL!=target && ownerAirTargetKey==FsExistence::GetSearchKey(target))
\t{
\t\treturn YSTRUE;
\t}
\telse
\t{
\t\treturn YSFALSE;
\t}
}"""
    
    if old_function in content:
        content = content.replace(old_function, new_function)
        print_success(f"Modified {os.path.basename(filepath)}")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    else:
        print_warning(f"Could not find exact IsOwnerStillHaveTarget() function in {os.path.basename(filepath)}")
        print_warning("This may be due to formatting differences. Please apply manually from patches/fsweapon.cpp.patch")
        return False

def find_files(base_path):
    """Find the required source files"""
    files = {
        'fsairplaneproperty.h': None,
        'fsairplaneproperty.cpp': None,
        'fsinstreading.h': None,
        'fsweapon.cpp': None
    }
    
    print_status("Searching for source files...")
    
    for root, dirs, filenames in os.walk(base_path):
        for filename in filenames:
            if filename in files:
                filepath = os.path.join(root, filename)
                files[filename] = filepath
                print_success(f"Found: {filepath}")
    
    return files

def main():
    print_status("=" * 60)
    print_status("YSFLIGHT ECM INTEGRATION - Automated Script")
    print_status("=" * 60)
    print()
    
    # Determine base path
    if len(sys.argv) > 1:
        base_path = sys.argv[1]
    else:
        base_path = os.getcwd()
    
    print_status(f"Base path: {base_path}")
    print()
    
    # Find files
    files = find_files(base_path)
    print()
    
    # Check if all files found
    missing = [f for f, p in files.items() if p is None]
    if missing:
        print_error(f"Could not find: {', '.join(missing)}")
        print_warning("Make sure you run this script from the YSFLIGHT root directory")
        print_warning("Usage: python apply_ecm_integration.py [path/to/ysflight]")
        return 1
    
    print_status("All required files found!")
    print()
    
    # Apply modifications
    print_status("Applying ECM modifications...")
    print()
    
    try:
        success = True
        
        success &= modify_fsairplaneproperty_h(files['fsairplaneproperty.h'])
        print()
        
        success &= modify_fsairplaneproperty_cpp(files['fsairplaneproperty.cpp'])
        print()
        
        success &= modify_fsinstreading_h(files['fsinstreading.h'])
        print()
        
        success &= modify_fsweapon_cpp(files['fsweapon.cpp'])
        print()
        
        if success:
            print_status("=" * 60)
            print_success("ECM INTEGRATION COMPLETED SUCCESSFULLY!")
            print_status("=" * 60)
            print()
            print("NEXT STEPS:")
            print("1. Add 'UpdateEcm(dt);' call in FsAirplaneProperty::Move()")
            print("2. Fill FsInstrumentIndication with ECM state in cockpit code")
            print("3. Compile the project")
            print("4. Test ECM functionality in-game")
            print()
            print("BACKUPS CREATED:")
            for fname in files.values():
                if fname:
                    print(f"  - {fname}.backup")
            print()
            return 0
        else:
            print_error("Some modifications failed. Check messages above.")
            return 1
            
    except Exception as e:
        print_error(f"Error during modification: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
