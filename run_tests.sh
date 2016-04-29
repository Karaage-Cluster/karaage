#!/bin/bash
DIR=$(cd -P -- "$(dirname -- "$0")" && pwd -P)

FLAKE=0
RETURN=0
cd $DIR

if [ -n "$*" ]; then
    TESTS="$@"
else
    TESTS="karaage.tests.settings:karaage.tests
        karaage.plugins.kgapplications.tests.settings:karaage.plugins.kgapplications
        karaage.plugins.kgsoftware.tests.settings:karaage.plugins.kgsoftware.tests
        karaage.plugins.kgsoftware.applications.tests.settings:karaage.plugins.kgsoftware
        karaage.plugins.kgusage.tests.settings:karaage.plugins.kgusage"
fi

echo ""
echo "FLAKE8"
echo "############################"
find -path "*/south_migrations/*.py" -print0 | xargs -0 flake8 --ignore=E501
if [ ! $? -eq 0 ]; then FLAKE=1; fi

find -path "*/migrations/*.py" -print0 | xargs -0 flake8 --ignore=E501
if [ ! $? -eq 0 ]; then FLAKE=1; fi

flake8 --exclude="south_migrations,migrations" .
if [ ! $? -eq 0 ]; then FLAKE=1; fi

echo -e "\n\n"

for values in $TESTS; do
    conf=$(echo $values | cut -f1 -d:)
    tests=$(echo $values | cut -f2 -d: | sed 's/,/ /g')

    echo ""
    echo "STATIC FILES - $conf"
    echo "############################"
    rm -rf tmp
    ./manage.py collectstatic --settings="$conf" -v 2 --noinput
    if [ "$?" -ne 0 ]
    then
        exit 1
    fi

    echo ""
    echo "TESTS - Python 2 - $conf - $tests"
    echo "############################"
    python2 ./manage.py test --settings="$conf" -v 2 $tests
    if [ "$?" -ne 0 ]
    then
        RETURN=1
    fi

    echo ""
    echo "TESTS - Python 3 - $conf - $tests"
    echo "############################"
    python3 ./manage.py test --settings="$conf" -v 2 $tests
    if [ "$?" -ne 0 ]
    then
        RETURN=1
    fi

    if [ "$RETURN" -ne 0 ]; then
        echo "ERROR: Some tests failed for $values" >&2
        exit "$RETURN"
    fi
done

if [ "$FLAKE" -ne 0 ]; then
    echo "ERROR: flake8 tests failed" >&2
    exit "$FLAKE"
fi


exit "$RETURN"
