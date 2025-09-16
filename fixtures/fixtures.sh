#!/bin/bash
python3 fixtures.py csv > fixtures.csv

echo '# Club Fixture Calendar

See [fixtures.csv](/fixtures/fixtures.csv) for detailed fixture list
where UPPERCASE teams are home fixtures and lowercase teams are away fixtures.

Or the below table where bold **teams** are home fixtures and italic *teams* are away fixtures.

' > fixtures.md
python3 fixtures.py md >> fixtures.md

cp fixtures.md ../test/md/
cp fixtures.md ../md/
rm fixtures.md
