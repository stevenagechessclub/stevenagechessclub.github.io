#!/bin/bash
python3 fixtures.py csv > fixtures.csv

echo '# Club Fixture Calendar

See [fixtures.csv](/fixtures/fixtures.csv) for detailed fixture list.

Or the below table where **bold teams** are home fixtures and *italic teams* are away fixtures.

NOTE: We have a bye in the first round of the Sharp Knockout Trophy. The Field Trophy, AGM and
subsequent Knockout rounds are still to be scheduled.

' > fixtures.md
python3 fixtures.py md >> fixtures.md

cp fixtures.md ../test/md/
cp fixtures.md ../md/
rm fixtures.md
