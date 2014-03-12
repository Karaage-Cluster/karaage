#!/bin/bash
DIR=$(cd -P -- "$(dirname -- "$0")" && pwd -P)

# Print some diagnostics

python -c 'import karaage.conf.defaults; print karaage.conf.defaults.__file__'

RETURN=0
cd $DIR

if [ -n "$*" ]; then
    TESTS="$@"
else
    TESTS="karaage"
fi

echo "FLAKE8"
echo "############################"
./flake8.py
if [ ! $? -eq 0 ]
then
    RETURN=1
fi
echo -e "\n\n"

echo "TESTS"
echo "############################"
./manage.py test --settings=karaage.tests.settings -v 2 $TESTS
if [ ! $? -eq 0 ]
then
    RETURN=1
fi

exit $RETURN
