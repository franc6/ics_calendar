if test -n "$1" ; then
    TEST=$1
else
    TEST=tests/
fi

TOP=`pwd`
rm -rf htmlcov/*
pytest --allow-unix-socket --cov=custom_components.ics_calendar --cov-branch --cov-report html ${TEST}
echo "To view coverage, open ${TOP}/htmlcov/index.html"
