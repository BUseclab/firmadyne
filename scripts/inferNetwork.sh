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
    echo "Usage: inferNetwork.sh <image ID> [<architecture>]"
    exit 1
fi
IID=${1}

arch=`${SCRIPT_DIR}/get_arch_version.py "${IID}" "${SCRATCH_DIR}" "${FS_OUT_DIR}" "${FS_SCRIPT_DIR}"`

echo "Running firmware ${IID} with arch ${arch}: terminating after 100 secs..."
timeout --preserve-status --signal SIGINT 100 "${SCRIPT_DIR}/run.${arch}.sh" "${IID}"
sleep 1

echo "Inferring network..."
"${SCRIPT_DIR}/makeNetwork.py" -i "${IID}" -q -o -a "${arch}" -S "${SCRATCH_DIR}"

echo "Done!"
