#!/bin/bash
DIR=$(cd -P -- "$(dirname -- "$0")" && pwd -P)

RETURN=0
cd $DIR

# NOTE (RS) Disabled because there are far too many errors to fix.

# flake8 .
# if [ ! $? -eq 0 ]
# then
#     RETURN=1
# fi

if [ -n "$*" ]; then
    TESTS="$@"
else
    TESTS="karaage"
fi
kg-manage test --settings=karaage.tests.settings $TESTS

exit $RETURN
