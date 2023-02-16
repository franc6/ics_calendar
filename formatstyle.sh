# see pyproject.toml for settings
echo "Sorting imports"
isort custom_components/ics_calendar tests

echo "Formatting files"
black custom_components/ics_calendar tests

echo "flake8 style and complexity checks"
flake8 || exit

echo "pydocstyle checks"
pydocstyle -v custom_components/ics_calendar tests || exit

echo "pylint checks"
pylint custom_components/ics_calendar || exit
