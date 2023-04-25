#!/bin/bash

#set -e
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
    echo "Usage: makeImage.sh <image ID> [<architecture]"
    exit 1
fi
IID=${1}
Mode=${2}

if check_root; then
    echo "Error: This script requires root privileges!"
    exit 1
fi

if [ $# -gt 2 ]; then
    if check_arch "${3}"; then
        echo "Error: Invalid architecture!"
        exit 1
    fi

    ARCH=${3}
else
    echo -n "Querying database for architecture... "
    ARCH=$(psql -d firmware -U firmadyne -h 127.0.0.1 -t -q -c "SELECT arch from image WHERE id=${1};")
    ARCH="${ARCH#"${ARCH%%[![:space:]]*}"}"
    echo "${ARCH}"
    if [ -z "${ARCH}" ]; then
        echo "Error: Unable to lookup architecture. Please specify {armel,mipseb,mipsel} as the second argument!"
        exit 1
    fi
fi


USER=`whoami`

echo "----Running----"
WORK_DIR=`get_scratch ${IID}`
IMAGE=`get_fs ${IID}`
IMAGE_DIR=`get_fs_mount ${IID}`

echo "----Copying Filesystem Tarball----"
mkdir -p "${WORK_DIR}"
chmod a+rwx "${WORK_DIR}"
chown -R "${USER}" "${WORK_DIR}"
chgrp -R "${USER}" "${WORK_DIR}"

if [ ! -e "${WORK_DIR}/${IID}.tar.gz" ]; then
    if [ ! -e "${TARBALL_DIR}/${IID}.tar.gz" ]; then
        echo "Error: Cannot find tarball of root filesystem for ${IID}!"
        exit 1
    else
        cp "${TARBALL_DIR}/${IID}.tar.gz" "${WORK_DIR}/${IID}.tar.gz"
    fi
fi

echo "----Creating QEMU Image----"
qemu-img create -f raw "${IMAGE}" 512M
chmod a+rw "${IMAGE}"

echo "----Creating Partition Table----"
echo -e "o\nn\np\n1\n\n\nw" | /sbin/fdisk -c=dos "${IMAGE}"

echo "----Mounting QEMU Image----"
DEVICE=$(get_device "$(kpartx -a -s -v "${IMAGE}")")
DEV=$(get_loop_dev "$(losetup -j "${IMAGE}")")
sleep 1

echo "----Creating Filesystem----"
mkfs.ext2 "${DEVICE}"
#sync

echo "----Making QEMU Image Mountpoint----"
if [ ! -e "${IMAGE_DIR}" ]; then
    mkdir "${IMAGE_DIR}"
    chown "${USER}" "${IMAGE_DIR}"
fi

echo "----Mounting QEMU Image Partition 1----"
mount "${DEVICE}" "${IMAGE_DIR}"

echo "----Extracting Filesystem Tarball----"
tar -zxf "${WORK_DIR}/$IID.tar.gz" -C "${IMAGE_DIR}"
rm "${WORK_DIR}/${IID}.tar.gz"

echo "----Creating FIRMADYNE Directories----"
mkdir "${IMAGE_DIR}/firmadyne/"
mkdir "${IMAGE_DIR}/firmadyne/libnvram/"
mkdir "${IMAGE_DIR}/firmadyne/libnvram.override/"


echo "----Patching Filesystem (chroot)----"
cp $(which busybox) "${IMAGE_DIR}"
cp "${SCRIPT_DIR}/fixImage.sh" "${IMAGE_DIR}"
chroot "${IMAGE_DIR}" /busybox ash /fixImage.sh
rm "${IMAGE_DIR}/fixImage.sh"
rm "${IMAGE_DIR}/busybox"

echo "----Finding the FirmSolo upstream module directory----"
KERN=`find ${FS_OUT_DIR}/results/${IID} -name linux-* -type d`

echo "----Setting up FIRMADYNE----"
${SCRIPT_DIR}/copy_binaries.py ${FIRMWARE_DIR} ${KERN} ${ARCH} ${IMAGE_DIR} ${WORK_DIR}

chmod a+x "${IMAGE_DIR}/firmadyne/console"

if [[ ${ARCH} == mips* ]];
then
	mknod -m 666 "${IMAGE_DIR}/firmadyne/ttyS1" c 4 65
else
	mknod -m 666 "${IMAGE_DIR}/firmadyne/ttyS1" c 204 65
fi

chmod a+x "${IMAGE_DIR}/firmadyne/libnvram.so"

cp "${SCRIPT_DIR}/preInit.sh" "${IMAGE_DIR}/firmadyne/preInit.sh"
chmod a+x "${IMAGE_DIR}/firmadyne/preInit.sh"


echo "----Copying the TriforceAFL bugs in the filesystem----"
cp -r ${FIRMWARE_DIR}/TriforceAFL_bugs/ ${IMAGE_DIR} 

echo "----Creating upstream module directory----"
mkdir "${IMAGE_DIR}/upstream"

echo "----Copying the upstream modules to the filesystem----"
cp -r ${KERN}/lib/modules/* ${IMAGE_DIR}/upstream/

echo "------Erasing Bad Modules------"
${SCRIPT_DIR}/erase_bad_modules.py ${IID} ${IMAGE_DIR} ${FS_SCRIPT_DIR}

########### Edit the rcS script to load the upstream modules before the shipped ones ###############
init=`find ${IMAGE_DIR} -name rcS | head -1`
echo "${init}"

if [ -z "$init" ]
then
	echo "RCS does not exist!!"
	if [ -d "${IMAGE_DIR}/etc/init.d/" ]
	then
		touch ${IMAGE_DIR}/etc/init.d/rcS
		init=${IMAGE_DIR}/etc/init.d/rcS
		echo "#!/bin/sh" > $init
		chmod a+x $init
	else
		mkdir ${IMAGE_DIR}/etc/init.d
		touch ${IMAGE_DIR}/etc/init.d/rcS
		init=${IMAGE_DIR}/etc/init.d/rcS
		echo "#!/bin/sh" > $init
		chmod a+x $init
	fi
else
	echo "RCS exists!!"
	echo "${init}"

fi

${SCRIPT_DIR}/insert_line.py "${init}" "${FS_OUT_DIR}/Loaded_Modules/${IID}/${IID}_ups_subs.order"

echo "----Unmounting QEMU Image----"
sync
umount "${DEVICE}"
e2fsck -fy "${DEVICE}"
losetup -d "${DEV}" &>/dev/null
kpartx -d "${DEV}"
dmsetup remove $(basename "$DEVICE") &>/dev/null
