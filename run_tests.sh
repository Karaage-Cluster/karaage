#!/bin/bash
DIR=$(cd -P -- "$(dirname -- "$0")" && pwd -P)
REQUIREMENTS="-r ./requirements.txt -r ./requirements-usage.txt -r ./requirements-tests.txt"

RETURN=0
cd $DIR

if [ -n "$*" ]; then
    TESTS="$@"
else
    TESTS="karaage kgapplications kgsoftware kgusage"
fi

echo ""
echo "FLAKE8"
echo "############################"
flake8 --ignore=E501 --filename="south_migrations" .
flake8 --ignore=E501 --filename="migrations" .
flake8 --exclude="south_migrations,migrations" .
if [ ! $? -eq 0 ]
then
    RETURN=1
fi
echo -e "\n\n"

echo ""
echo "STATIC FILES"
echo "############################"
./manage.py collectstatic --settings=karaage.tests.settings -v 2 --noinput

echo ""
echo "TESTS - Python 2"
echo "############################"
pip2 install $REQUIREMENTS
python2 ./manage.py test --settings=karaage.tests.settings -v 2 $TESTS
if [ ! $? -eq 0 ]
then
    RETURN=1
fi

echo ""
echo "TESTS - Python 3"
echo "############################"
pip3 install $REQUIREMENTS
python3 ./manage.py test --settings=karaage.tests.settings -v 2 $TESTS
if [ ! $? -eq 0 ]
then
    RETURN=1
fi

exit $RETURN
