# see pyproject.toml for settings
echo "Sorting imports"
isort custom_components/ics_calendar tests

echo "Formatting files"
black custom_components/ics_calendar tests

echo "Formatting json files"
for i in custom_components/ics_calendar/*.json custom_components/ics_calendar/translations/*.json
do
    echo "    $i"
    python -m json.tool $i > /dev/null || exit
    python -m json.tool $i > $i.new
    if diff $i $i.new >/dev/null 2>/dev/null
    then
        cat $i.new > $i
    fi
    rm $i.new
done

echo "flake8 style and complexity checks"
flake8 || exit

echo "pydocstyle checks"
pydocstyle -v custom_components/ics_calendar tests || exit

echo "pylint checks"
pylint custom_components/ics_calendar || exit
