#!/bin/bash
python3 fixtures.py csv > fixtures.csv

echo '# Club Fixture Calendar

See below for club fixtures.
Bold **team name** fixtures are at home; italic *team name* fixtures are away.

See [fixtures.csv](/fixtures/fixtures.csv)

' > fixtures.md
python3 fixtures.py md >> fixtures.md

cp fixtures.md ../test/md/
cp fixtures.md ../md/
rm fixtures.md
