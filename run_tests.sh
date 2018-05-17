#!/bin/bash
DIR=$(cd -P -- "$(dirname -- "$0")" && pwd -P)

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
echo "ISORT"
echo "############################"
isort -rc --check --diff karaage
if [ "$?" -ne 0 ]
then
    exit 1
fi

echo ""
echo "FLAKE8"
echo "############################"
flake8 karaage
if [ "$?" -ne 0 ]
then
    exit 1
fi

echo -e "\n\n"

for values in $TESTS; do
    conf=$(echo $values | cut -f1 -d:)
    tests=$(echo $values | cut -f2 -d: | sed 's/,/ /g')

    echo ""
    echo "MIGRATIONS - $conf"
    echo "############################"
    ./manage.py makemigrations --settings="$conf" --check --dry-run
    if [ "$?" -ne 0 ]
    then
        exit 1
    fi

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
    echo "TESTS - Python 3 - $conf - $tests"
    echo "############################"
    python3 ./manage.py test --settings="$conf" -v 2 $tests
    if [ "$?" -ne 0 ]
    then
        exit 1
    fi
done

exit "$RETURN"
