#!/bin/bash
set -ev

hash -r

# Install and test FURY
cd ${TRAVIS_BUILD_DIR}
python3 setup.py install
# Change folder
mkdir for_testing
cd for_testing
# We need the setup.cfg for the pytest settings
cp ../setup.cfg .
python3 -c "import helios; print('Helios Version:', helios.__version__)"

if [[ "${COVERAGE}" == "1" ]]; then
  cp ../.coveragerc .;
  cp ../.codecov.yml .;
  coverage run -m pytest -svv --pyargs fury  # Run the tests and check for test coverage.
  coverage report -m  # Generate test coverage report.
  codecov  # Upload the report to codecov.
else
    pytest -svv --pyargs fury
fi

set +ev