#!/bin/bash

set -u

if [ -e ./firmadyne.config ]; then
	source ./firmadyne.config
elif [ -e ../firmadyne.config ]; then
	source ../firmadyne.config
else
	echo "Error: Could not find 'firmadyne.config'!"
	exit 1
fi

IID=$1

${SCRIPT_DIR}/makeImages.py -i ${IID} -f ${FS_SCRIPT_DIR}

ENDIAN=`sed '2q;d' ${SCRATCH_DIR}/${IID}/image_data`

echo "${ENDIAN}"


echo "Detecting network configuration"
${SCRIPT_DIR}/inferNetwork.sh $IID $ENDIAN
if [ $? -eq 0 ]; then
    echo "Network conf for ${IID} run ok"
else
    echo "Network conf for ${IID} exited with errors"
fi

sleep 2

echo "Testing for kernel module bugs"
./run_exploits.py ${IID} ${SCRATCH_DIR} ${FS_SCRIPT_DIR}

echo "Booting..."
timeout --foreground 120s ${SCRATCH_DIR}/${IID}/run.sh

