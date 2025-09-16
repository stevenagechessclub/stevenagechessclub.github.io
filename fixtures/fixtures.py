import csv
import datetime
import urllib.request
import json
import sys


def get_current_season_year():
    now = datetime.datetime.now()
    year = now.year
    if now.month < 7:
        year -= 1
    return year


def get_club_nights():
    dates = []
    year = get_current_season_year()
    date_time = datetime.datetime(year, 9, 7)
    date_time += datetime.timedelta(-date_time.weekday())
    while date_time.month != 7:
        dates.append(date_time)
        date_time += datetime.timedelta(7)
    return dates


def get_bank_holidays():
    dates = []
    with urllib.request.urlopen("https://www.gov.uk/bank-holidays.json") as url:
        data = json.loads(url.read().decode())
        events = data['england-and-wales']['events']
        for event in events:
            date_time = datetime.datetime.strptime(event['date'],"%Y-%m-%d")
            dates.append(date_time)
    return dates


def get_closed_nights():
    dates = []
    year = get_current_season_year()
    date_time = datetime.datetime(year, 12, 22)
    while date_time.month != 1:
        if date_time.weekday() == 0:
            dates.append(date_time)
        date_time += datetime.timedelta(7)
    return dates


def get_christmas_blitz_date():
    dates = []
    year = get_current_season_year()
    date_time = datetime.datetime(year, 12, 21)
    date_time -= datetime.timedelta(date_time.weekday())
    return date_time


def add_fixture(fixtures, date_time, column_header, row_entry):
    date_ymd = date_time.strftime("%Y-%m-%d")
    if date_ymd in fixtures:
        fixture = fixtures[date_ymd]
        if column_header in fixture:
            raise ValueError(f'Duplicate entry for {date_ymd} {column_header}: {fixture[column_header]} and {row_entry}')
        fixture[column_header] = row_entry
    else:
        fixtures[date_ymd] = {
            'DATE': date_time.strftime("%a %d-%b-%Y"),
            column_header: row_entry
        }


def add_club_nights(fixtures, table_format):
    club_nights          = get_club_nights()
    bank_holidays        = get_bank_holidays()
    closed_nights        = get_closed_nights()
    christmas_blitz_date = get_christmas_blitz_date()

    for night in club_nights:
        if table_format == 'dates':
            if night not in bank_holidays and night not in closed_nights:
                add_fixture(fixtures, night, 'CLUB', 'Club Night')
        elif table_format == 'csv':
            if night in bank_holidays:
                add_fixture(fixtures, night, 'CLUB', 'CLOSED')
            elif night in closed_nights:
                add_fixture(fixtures, night, 'CLUB', 'CLOSED')
            elif night == christmas_blitz_date:
                add_fixture(fixtures, night, 'CLUB', 'Christmas Blitz')
            else:
                add_fixture(fixtures, night, 'CLUB', '')
        elif table_format == 'md':
            if night in bank_holidays:
                add_fixture(fixtures, night, 'H & D / Other', '**CLOSED**')
            elif night in closed_nights:
                add_fixture(fixtures, night, 'H & D / Other', '**CLOSED**')
            elif night == christmas_blitz_date:
                add_fixture(fixtures, night, 'H & D / Other', '**Christmas Blitz**')
            else:
                add_fixture(fixtures, night, 'PLACEHOLDER', 'Open')
        else:
            raise ValueError('Unsupported table_format {table_format}')


def add_e2e4_fixtures(fixtures, fixtures_path, table_format):
    line_number = 1
    num_fixtures = 0
    unique_columns = []
    with open(fixtures_path, newline='') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            if len(row) == 7:
                day_date_str = row[0]
                org          = row[1]
                competition  = row[2]
                division     = row[3]
                home         = row[4]
                away         = row[5]
                date_time    = datetime.datetime.strptime(day_date_str,"%a %d-%b-%Y")

                if "Stevenage" in home:
                    my_team = home
                    versus_team = away
                    home_fixture = True
                elif "Stevenage" in away:
                    my_team = away
                    versus_team = home
                    home_fixture = False
                else:
                    raise ValueError(f'line {line_number}: expected Stevenage in either home "{home}" or away "{away}" team')

                column_header = None
                row_entry     = None

                if table_format == 'csv':
                    if competition == "Herts League":
                        row_entry = versus_team
                        if my_team == "Stevenage 1":
                            column_header = "1ST TEAM"
                        elif my_team == "Stevenage 2":
                            column_header = "2ND TEAM"
                        elif my_team == "Stevenage 3":
                            column_header = "3RD TEAM"
                    elif competition == "H&D League":
                        row_entry = versus_team
                        if my_team == "Stevenage":
                            column_header = "Herts & District"
                    elif competition == "U1600 League":
                        if my_team == "Stevenage":
                            column_header = "U1600"
                            row_entry = f'{versus_team}'
                    elif competition == "Knock Out":
                        if my_team == "Stevenage":
                            if division == "Sharp Trophy":
                                column_header = "K/O Cups"
                                row_entry = f'{versus_team} (Sharp)'
                            elif division == "Under 1750 Cup":
                                column_header = "K/O Cups"
                                row_entry = f'{versus_team} (U1750 KO)'
                            elif division == "Under 1600 Cup":
                                column_header = "K/O Cups"
                                row_entry = f'{versus_team} (U1600 KO)'
                    if not column_header or not row_entry:
                        raise ValueError(f'line {line_number}: unexpected team {my_team} in {competition}')
                    if home_fixture:
                        row_entry = row_entry.upper()
                    else:
                        row_entry = row_entry.lower()
                elif table_format == 'md':
                    if competition == "Herts League":
                        row_entry = versus_team
                        if my_team == "Stevenage 1":
                            column_header = "1ST TEAM / SHARP"
                        elif my_team == "Stevenage 2":
                            column_header = "2ND TEAM / U1750 KO"
                        elif my_team == "Stevenage 3":
                            column_header = "3RD TEAM / U1600"
                    elif competition == "H&D League":
                        row_entry = versus_team
                        if my_team == "Stevenage":
                            column_header = "H & D / Other"
                    elif competition == "U1600 League":
                        if my_team == "Stevenage":
                            column_header = "3RD TEAM / U1600"
                            row_entry = f'{versus_team} (U1600 League)'
                    elif competition == "Knock Out":
                        if my_team == "Stevenage":
                            if division == "Sharp Trophy":
                                column_header = "1ST TEAM / SHARP"
                                row_entry = f'{versus_team} (Sharp)'
                            elif division == "Under 1750 Cup":
                                column_header = "2ND TEAM / U1750 KO"
                                row_entry = f'{versus_team} (U1750 KO)'
                            elif division == "Under 1600 Cup":
                                column_header = "3RD TEAM / U1600"
                                row_entry = f'{versus_team} (U1600 KO)'
                    if not column_header or not row_entry:
                        raise ValueError(f'line {line_number}: unexpected team {my_team} in {competition}')
                    if home_fixture:
                        row_entry = f'**{row_entry}**'
                    else:
                        row_entry = f'*{row_entry}*'
                else:
                    raise ValueError('Unsupported table_format {table_format}')
                if column_header not in unique_columns:
                    unique_columns.append(column_header)
                add_fixture(fixtures, date_time, column_header, row_entry)
                num_fixtures += 1
            else:
                raise ValueError(f'line {line_number}: badly formatted line {" ".join(row)}')
            line_number += 1
    return (unique_columns, num_fixtures)


def fixtures_to_table(fixtures, columns, table_format):
    num_fixtures = 0
    max_fixtures_on_date = 0
    ignored_columns = []
    if table_format == 'md':
        dashes = []
        for column in columns:
            dashes.append('-----------')
        print(f'| {" | ".join(columns)} |')
        print(f'| {" | ".join(dashes)} |')
    elif table_format == 'csv':
        print(','.join(columns))
    else:
        raise ValueError(f'unsupported table_format {table_format}')

    for date in sorted(fixtures.keys()):
        fixture = fixtures[date]
        num_fixtures_on_date = 0
        for column in columns:
            if column in fixture and column not in ['DATE', 'CLUB', 'PLACEHOLDER'] and fixture[column] not in ['CLOSED', 'Christmas Blitz', '**CLOSED**', '**Christmas Blitz**']:
                num_fixtures_on_date += 1
        for fixture_key in fixture:
            if fixture_key not in columns and fixture_key not in ['DATE', 'CLUB', 'PLACEHOLDER']:
                if fixture_key not in ignored_columns:
                    ignored_columns.append(fixture_key)
        num_fixtures += num_fixtures_on_date
        club_night = ''
        if 'CLUB' in fixture:
            club_night = fixture['CLUB']
        if num_fixtures_on_date >= 0:
            if num_fixtures_on_date > max_fixtures_on_date:
                max_fixtures_on_date = num_fixtures_on_date
            row = []
            for column in columns:
                if column in fixture:
                    row.append(fixture[column])
                else:
                    row.append('')
            if table_format == 'md':
                print(f'| {" | ".join(row)} |')
            elif table_format == 'csv':
                print(','.join(row))
    return (num_fixtures, max_fixtures_on_date, ignored_columns)


def print_club_nights():
    fixtures = {}
    add_club_nights(fixtures, 'dates')
    fixtures_to_table(fixtures, ['DATE'], 'csv')


def print_fixtures_csv():
    fixtures = {}
    add_club_nights(fixtures, 'csv')

    (unique_columns, num_fixtures) = add_e2e4_fixtures(fixtures, './fixtures.txt', 'csv')
    (num_fixtures_on_date_check, max_fixtures_on_date, ignored_columns) = fixtures_to_table(fixtures, ['DATE', 'CLUB', '1ST TEAM', '2ND TEAM', '3RD TEAM', 'U1600', 'K/O Cups', 'Herts & District'], 'csv')
    if max_fixtures_on_date != 2:
        raise ValueError(f'failed max fixtures on date check {max_fixtures_on_date}')
    if num_fixtures_on_date_check != num_fixtures:
        raise ValueError(f'failed fixture count check {num_fixtures_on_date_check} {num_fixtures} {",".join(ignored_columns)}')


def print_fixtures_md():
    fixtures = {}
    add_club_nights(fixtures, 'md')

    (unique_columns, num_fixtures) = add_e2e4_fixtures(fixtures, './fixtures.txt', 'md')
    (num_fixtures_on_date_check, max_fixtures_on_date, ignored_columns) = fixtures_to_table(fixtures, ['DATE', 'H & D / Other', '1ST TEAM / SHARP', '2ND TEAM / U1750 KO', '3RD TEAM / U1600'], 'md')
    if max_fixtures_on_date != 2:
        raise ValueError(f'failed max fixtures on date check {max_fixtures_on_date}')
    if num_fixtures_on_date_check != num_fixtures:
        raise ValueError(f'failed fixture count check {num_fixtures_on_date_check} {num_fixtures} {",".join(ignored_columns)}')


if len(sys.argv) != 2:
    print(f'Usage: {sys.argv[0]} dates|csv|md')
elif sys.argv[1] == 'dates':
    print_club_nights()
elif sys.argv[1] == 'csv':
    print_fixtures_csv()
elif sys.argv[1] == 'md':
    print_fixtures_md()
else:
    raise ValueError(f'Unrecognised command line option {sys.argv[1]}')
