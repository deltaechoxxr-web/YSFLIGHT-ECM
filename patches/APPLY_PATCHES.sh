#!/bin/bash
# Script to apply all ECM patches to YSFLIGHT
# Run from the YSFLIGHT root directory

echo "Applying ECM patches to YSFLIGHT..."
echo ""

echo "[1/4] Applying fsairplaneproperty.h patch..."
patch -p1 < patches/fsairplaneproperty.h.patch
if [ $? -eq 0 ]; then
    echo "✓ fsairplaneproperty.h patched successfully"
else
    echo "✗ Error patching fsairplaneproperty.h"
    exit 1
fi

echo ""
echo "[2/4] Applying fsairplaneproperty.cpp patch..."
patch -p1 < patches/fsairplaneproperty.cpp.patch
if [ $? -eq 0 ]; then
    echo "✓ fsairplaneproperty.cpp patched successfully"
else
    echo "✗ Error patching fsairplaneproperty.cpp"
    exit 1
fi

echo ""
echo "[3/4] Applying fsinstreading.h patch..."
patch -p1 < patches/fsinstreading.h.patch
if [ $? -eq 0 ]; then
    echo "✓ fsinstreading.h patched successfully"
else
    echo "✗ Error patching fsinstreading.h"
    exit 1
fi

echo ""
echo "[4/4] Applying fsweapon.cpp patch..."
patch -p1 < patches/fsweapon.cpp.patch
if [ $? -eq 0 ]; then
    echo "✓ fsweapon.cpp patched successfully"
else
    echo "✗ Error patching fsweapon.cpp"
    exit 1
fi

echo ""
echo "✓ All ECM patches applied successfully!"
echo ""
echo "Next steps:"
echo "1. Add UpdateEcm(dt) call to FsAirplaneProperty::Move()"
echo "2. Fill FsInstrumentIndication with ECM state in cockpit code"
echo "3. Compile and test"
