#!/bin/bash
set -ev

# Create deps dir
mkdir ${ENV_DIR}
cd ${ENV_DIR}

PIPI="pip install $EXTRA_PIP_FLAGS"

$PIPI --upgrade setuptools pip

if [ "$USE_PRE" == "1" ]; then
    PIPI="$PIPI $PRE_PIP_FLAGS";
fi

$PIPI -r ${TRAVIS_BUILD_DIR}requirements.txt
$PIPI -r ${TRAVIS_BUILD_DIR}requirements_dev.txt


set +ev