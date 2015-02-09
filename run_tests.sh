#!/bin/bash
DIR=$(cd -P -- "$(dirname -- "$0")" && pwd -P)

FLAKE=0
RETURN=0
cd $DIR

if [ -n "$*" ]; then
    TESTS="$@"
else
    TESTS="karaage.tests.settings:karaage.tests
        kgapplications.tests.settings:kgapplications
        kgsoftware.tests.settings:kgsoftware.tests
        kgsoftware.applications.tests.settings:kgsoftware
        kgusage.tests.settings:kgusage"
fi

echo ""
echo "FLAKE8"
echo "############################"
flake8 --ignore=E501 --filename="south_migrations" .
flake8 --ignore=E501 --filename="migrations" .
flake8 --exclude="south_migrations,migrations" .
if [ ! $? -eq 0 ]
then
    FLAKE=1
fi
echo -e "\n\n"

for values in $TESTS; do
    conf=$(echo $values | cut -f1 -d:)
    tests=$(echo $values | cut -f2 -d: | sed 's/,/ /g')

    echo ""
    echo "STATIC FILES - $conf"
    echo "############################"
    ./manage.py collectstatic --settings="$conf" -v 2 --noinput

    echo ""
    echo "TESTS - Python 2 - $conf - $tests"
    echo "############################"
    python2 ./manage.py test --settings="$conf" -v 2 $tests
    if [ ! $? -eq 0 ]
    then
        RETURN=1
    fi

    # FIXME: ugly hack because Python3 django celery not in wheezy
    if [ "$conf" -ne "kgusage.tests.settings" ]
    then
        echo ""
        echo "TESTS - Python 3 - $conf - $tests"
        echo "############################"
        python3 ./manage.py test --settings="$conf" -v 2 $tests
        if [ ! $? -eq 0 ]
        then
            RETURN=1
        fi
    fi

    if [ "$RETURN" -ne 0 ]; then
        echo "ERROR: Some tests failed for $valuetring" >&2
        exit "$RETURN"
    fi
done

if [ "$FLAKE" -ne 0 ]; then
    echo "ERROR: flake8 tests failed" >&2
    exit "$FLAKE"
fi


exit "$RETURN"
