# Keep it simple, use the defaults, except where they conflict;
# prefer black defaults (except line-length) for style conflicts!

echo "Sorting imports"
isort --combine-as --line-length 79 --multi-line 3 --trailing-comma custom_components/ics_calendar tests

echo "Formatting files"
black --line-length 79 custom_components/ics_calendar tests

echo "flake8 style and complexity checks"
flake8 --doctests --max-complexity 7 --radon-max-cc 8 --exclude .venv,.git,__pycahce__ --max-line-length 88 --extend-ignore E722 || exit 

echo "pydocstyle checks"
pydocstyle -v custom_components/ics_calendar tests || exit

echo "pylint checks"
pylint -f colorized --disable=R0801 custom_components/ics_calendar || exit
