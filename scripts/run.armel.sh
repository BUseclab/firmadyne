#!/bin/bash

set -e
set -u

if [ -e ./firmadyne.config ]; then
    source ./firmadyne.config
elif [ -e ../firmadyne.config ]; then
    source ../firmadyne.config
else
    echo "Error: Could not find 'firmadyne.config'!"
    exit 1
fi

if check_number $1; then
    echo "Usage: run.armel.sh <image ID>"
    exit 1
fi
IID=${1}

WORK_DIR=`get_scratch ${IID}`
IMAGE=`get_fs ${IID}`
KERNEL=`get_kernel "armel" ${IID}`

QEMU_AUDIO_DRV=none qemu-system-arm -m 256 -M versatilepb -kernel ${KERNEL} -drive file=${IMAGE},if=scsi -append "root=/dev/sda1 rootwait fdyne_syscall=1 fdyne_reboot=1 fdyne_execute=1 fdyne_devfs=1 firmadyne.procfs=1 console=ttyAMA0 nandsim.parts=64,64,64,64,64,64,64,64,64,64 rdinit=/firmadyne/preInit.sh rw print-fatal-signals=1 user_debug=31 mem=256M" -serial file:${WORK_DIR}/qemu.initial.serial.log -serial unix:/tmp/qemu.${IID}.S1,server,nowait -monitor unix:/tmp/qemu.${IID},server,nowait -display none -net nic,vlan=0 -net socket,vlan=0,listen=:2000 -net nic,vlan=1 -net socket,vlan=1,listen=:2001 -net nic,vlan=2 -net socket,vlan=2,listen=:2002 -net nic,vlan=3 -net socket,vlan=3,listen=:2003
