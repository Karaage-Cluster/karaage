#!/bin/bash
DIR=$(cd -P -- "$(dirname -- "$0")" && pwd -P)

RETURN=0
cd $DIR

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

conf="karaage.tests.settings"
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
pytest --cov=karaage "$@"
if [ "$?" -ne 0 ]
then
    exit 1
fi

exit "$RETURN"
