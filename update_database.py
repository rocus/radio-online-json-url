#!/usr/bin/env python3

import gzip
import json
import re
import unicodedata
from collections import defaultdict


INPUT_FILE = "radiobrowser_stations_latest.json.gz"
OUTPUT_DIR = "."
MAX_SOURCES = 6


# ISO 3166-1 country names.
COUNTRY_NAMES = {
    "AD": "Andorra",
    "AE": "United Arab Emirates",
    "AF": "Afghanistan",
    "AG": "Antigua and Barbuda",
    "AI": "Anguilla",
    "AL": "Albania",
    "AM": "Armenia",
    "AO": "Angola",
    "AQ": "Antarctica",
    "AR": "Argentina",
    "AS": "American Samoa",
    "AT": "Austria",
    "AU": "Australia",
    "AW": "Aruba",
    "AX": "Åland Islands",
    "AZ": "Azerbaijan",
    "BA": "Bosnia and Herzegovina",
    "BB": "Barbados",
    "BD": "Bangladesh",
    "BE": "Belgium",
    "BF": "Burkina Faso",
    "BG": "Bulgaria",
    "BH": "Bahrain",
    "BI": "Burundi",
    "BJ": "Benin",
    "BL": "Saint Barthélemy",
    "BM": "Bermuda",
    "BN": "Brunei",
    "BO": "Bolivia",
    "BQ": "Bonaire, Sint Eustatius and Saba",
    "BR": "Brazil",
    "BS": "Bahamas",
    "BT": "Bhutan",
    "BV": "Bouvet Island",
    "BW": "Botswana",
    "BY": "Belarus",
    "BZ": "Belize",
    "CA": "Canada",
    "CC": "Cocos Islands",
    "CD": "Democratic Republic of the Congo",
    "CF": "Central African Republic",
    "CG": "Republic of the Congo",
    "CH": "Switzerland",
    "CI": "Ivory Coast",
    "CK": "Cook Islands",
    "CL": "Chile",
    "CM": "Cameroon",
    "CN": "China",
    "CO": "Colombia",
    "CR": "Costa Rica",
    "CU": "Cuba",
    "CV": "Cape Verde",
    "CW": "Curaçao",
    "CX": "Christmas Island",
    "CY": "Cyprus",
    "CZ": "Czech Republic",
    "DE": "Germany",
    "DJ": "Djibouti",
    "DK": "Denmark",
    "DM": "Dominica",
    "DO": "Dominican Republic",
    "DZ": "Algeria",
    "EC": "Ecuador",
    "EE": "Estonia",
    "EG": "Egypt",
    "EH": "Western Sahara",
    "ER": "Eritrea",
    "ES": "Spain",
    "ET": "Ethiopia",
    "FI": "Finland",
    "FJ": "Fiji",
    "FK": "Falkland Islands",
    "FM": "Micronesia",
    "FO": "Faroe Islands",
    "FR": "France",
    "GA": "Gabon",
    "GB": "United Kingdom",
    "GD": "Grenada",
    "GE": "Georgia",
    "GF": "French Guiana",
    "GG": "Guernsey",
    "GH": "Ghana",
    "GI": "Gibraltar",
    "GL": "Greenland",
    "GM": "Gambia",
    "GN": "Guinea",
    "GP": "Guadeloupe",
    "GQ": "Equatorial Guinea",
    "GR": "Greece",
    "GS": "South Georgia and the South Sandwich Islands",
    "GT": "Guatemala",
    "GU": "Guam",
    "GW": "Guinea-Bissau",
    "GY": "Guyana",
    "HK": "Hong Kong",
    "HM": "Heard Island and McDonald Islands",
    "HN": "Honduras",
    "HR": "Croatia",
    "HT": "Haiti",
    "HU": "Hungary",
    "ID": "Indonesia",
    "IE": "Ireland",
    "IL": "Israel",
    "IM": "Isle of Man",
    "IN": "India",
    "IO": "British Indian Ocean Territory",
    "IQ": "Iraq",
    "IR": "Iran",
    "IS": "Iceland",
    "IT": "Italy",
    "JE": "Jersey",
    "JM": "Jamaica",
    "JO": "Jordan",
    "JP": "Japan",
    "KE": "Kenya",
    "KG": "Kyrgyzstan",
    "KH": "Cambodia",
    "KI": "Kiribati",
    "KM": "Comoros",
    "KN": "Saint Kitts and Nevis",
    "KP": "North Korea",
    "KR": "South Korea",
    "KW": "Kuwait",
    "KY": "Cayman Islands",
    "KZ": "Kazakhstan",
    "LA": "Laos",
    "LB": "Lebanon",
    "LC": "Saint Lucia",
    "LI": "Liechtenstein",
    "LK": "Sri Lanka",
    "LR": "Liberia",
    "LS": "Lesotho",
    "LT": "Lithuania",
    "LU": "Luxembourg",
    "LV": "Latvia",
    "LY": "Libya",
    "MA": "Morocco",
    "MC": "Monaco",
    "MD": "Moldova",
    "ME": "Montenegro",
    "MF": "Saint Martin",
    "MG": "Madagascar",
    "MH": "Marshall Islands",
    "MK": "North Macedonia",
    "ML": "Mali",
    "MM": "Myanmar",
    "MN": "Mongolia",
    "MO": "Macao",
    "MP": "Northern Mariana Islands",
    "MQ": "Martinique",
    "MR": "Mauritania",
    "MS": "Montserrat",
    "MT": "Malta",
    "MU": "Mauritius",
    "MV": "Maldives",
    "MW": "Malawi",
    "MX": "Mexico",
    "MY": "Malaysia",
    "MZ": "Mozambique",
    "NA": "Namibia",
    "NC": "New Caledonia",
    "NE": "Niger",
    "NF": "Norfolk Island",
    "NG": "Nigeria",
    "NI": "Nicaragua",
    "NL": "Netherlands",
    "NO": "Norway",
    "NP": "Nepal",
    "NR": "Nauru",
    "NU": "Niue",
    "NZ": "New Zealand",
    "OM": "Oman",
    "PA": "Panama",
    "PE": "Peru",
    "PF": "French Polynesia",
    "PG": "Papua New Guinea",
    "PH": "Philippines",
    "PK": "Pakistan",
    "PL": "Poland",
    "PM": "Saint Pierre and Miquelon",
    "PN": "Pitcairn",
    "PR": "Puerto Rico",
    "PS": "Palestine",
    "PT": "Portugal",
    "PW": "Palau",
    "PY": "Paraguay",
    "QA": "Qatar",
    "RE": "Réunion",
    "RO": "Romania",
    "RS": "Serbia",
    "RU": "Russia",
    "RW": "Rwanda",
    "SA": "Saudi Arabia",
    "SB": "Solomon Islands",
    "SC": "Seychelles",
    "SD": "Sudan",
    "SE": "Sweden",
    "SG": "Singapore",
    "SH": "Saint Helena",
    "SI": "Slovenia",
    "SJ": "Svalbard and Jan Mayen",
    "SK": "Slovakia",
    "SL": "Sierra Leone",
    "SM": "San Marino",
    "SN": "Senegal",
    "SO": "Somalia",
    "SR": "Suriname",
    "SS": "South Sudan",
    "ST": "São Tomé and Príncipe",
    "SV": "El Salvador",
    "SX": "Sint Maarten",
    "SY": "Syria",
    "SZ": "Eswatini",
    "TC": "Turks and Caicos Islands",
    "TD": "Chad",
    "TF": "French Southern Territories",
    "TG": "Togo",
    "TH": "Thailand",
    "TJ": "Tajikistan",
    "TK": "Tokelau",
    "TL": "Timor-Leste",
    "TM": "Turkmenistan",
    "TN": "Tunisia",
    "TO": "Tonga",
    "TR": "Turkey",
    "TT": "Trinidad and Tobago",
    "TV": "Tuvalu",
    "TW": "Taiwan",
    "TZ": "Tanzania",
    "UA": "Ukraine",
    "UG": "Uganda",
    "UM": "United States Minor Outlying Islands",
    "US": "United States",
    "UY": "Uruguay",
    "UZ": "Uzbekistan",
    "VA": "Vatican City",
    "VC": "Saint Vincent and the Grenadines",
    "VE": "Venezuela",
    "VG": "British Virgin Islands",
    "VI": "United States Virgin Islands",
    "VN": "Vietnam",
    "VU": "Vanuatu",
    "WF": "Wallis and Futuna",
    "WS": "Samoa",
    "YE": "Yemen",
    "YT": "Mayotte",
    "ZA": "South Africa",
    "ZM": "Zambia",
    "ZW": "Zimbabwe",
}

def download_database():
    import os
    import tempfile
    import urllib.request

    database_url = (
        "https://backups.radio-browser.info/"
        "radiobrowser_stations_latest.json.gz"
    )

    print("Downloading latest Radio-Browser database...")

    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=".",
            delete=False
        ) as tmp:
            temp_file = tmp.name

            with urllib.request.urlopen(database_url, timeout=120) as response:
                while True:
                    data = response.read(1024 * 1024)
                    if not data:
                        break
                    tmp.write(data)

        os.replace(temp_file, INPUT_FILE)
        print(f"Database downloaded to {INPUT_FILE}")

    except Exception as e:
        print(f"Database download failed: {e}")
        try:
            os.unlink(temp_file)
        except (UnboundLocalError, FileNotFoundError):
            pass
        raise

def country_filename(country_code):
    if not country_code:
        return "unknown"

    name = COUNTRY_NAMES.get(country_code.upper())

    if not name:
        return "unknown"

    # Remove accents.
    name = unicodedata.normalize("NFKD", name)
    name = "".join(
        char for char in name
        if not unicodedata.combining(char)
    )

    # Keep letters and numbers only.
    name = re.sub(r"[^A-Za-z0-9]", "", name)

    return name or "unknown"

def clean_text(value):
    if value is None:
        return ""
    return str(value).strip()


print(f"Downloading {INPUT_FILE} ...")
download_database()

with gzip.open(INPUT_FILE, "rt", encoding="utf-8") as f:
    stations = json.load(f)

print(f"Radio-Browser records: {len(stations)}")


# Count usage of fields that are copied to the output.
field_counts = {
    "iso_639": 0,
    "iso_3166_2": 0,
    "geo_lat": 0,
    "geo_long": 0,
    "tags": 0,
    "url_favicon": 0,
}

for station in stations:
    for field in field_counts:
        value = station.get(field)
        if value is not None and str(value).strip():
            field_counts[field] += 1


# Group records that appear to describe the same station.
groups = defaultdict(list)

for station in stations:
    name = clean_text(station.get("name"))

    country = clean_text(
        station.get("iso_3166_1")
    ).upper()

    homepage = clean_text(
        station.get("url_homepage")
    )

    key = (
        name.lower(),
        country,
        homepage.lower(),
    )

    groups[key].append(station)


# Combine records and collect distinct stream URLs.
combined_by_country = defaultdict(list)

for key, records in groups.items():

    first = records[0]

    name = clean_text(first.get("name"))

    country_code = clean_text(
        first.get("iso_3166_1")
    ).upper()

    country = country_filename(country_code)

    homepage = clean_text(
        first.get("url_homepage")
    )

    station = {
        "Title": name,
        "Country": country,
    }

    tags = clean_text(first.get("tags"))
    if tags:
        station["Tags"] = tags

    favicon = clean_text(first.get("url_favicon"))
    if favicon:
        station["Favicon"] = favicon

    language = clean_text(first.get("iso_639"))
    if language:
        station["Language"] = language

    region = clean_text(first.get("iso_3166_2"))
    if region:
        station["Region"] = region

    if homepage:
        station["Homepage"] = homepage

    # Geographic coordinates.
    for source_field, output_field in (
        ("geo_lat", "Latitude"),
        ("geo_long", "Longitude"),
    ):
        value = first.get(source_field)

        if value is not None and str(value).strip():
            try:
                station[output_field] = float(value)
            except (ValueError, TypeError):
                pass

    # Collect distinct stream URLs from all records
    # belonging to this station.
    sources = []

    for record in records:
        url = clean_text(record.get("url_stream"))

        if not url:
            continue

        if url not in sources:
            sources.append(url)

    sources = sources[:MAX_SOURCES]

    for number, url in enumerate(sources, 1):
        station[f"Source{number}"] = url

    combined_by_country[country].append(station)


print()
print("Writing country files ...")
print()

total_entries = 0
total_sources = 0

for country in sorted(combined_by_country):

    filename = f"{OUTPUT_DIR}/{country}.json"
    entries = combined_by_country[country]

    entries.sort(
        key=lambda x: x["Title"].lower()
    )

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(
            entries,
            f,
            ensure_ascii=False,
            indent=4,
        )

    source_count = sum(
        sum(
            1
            for key in station
            if key.startswith("Source")
        )
        for station in entries
    )

    total_entries += len(entries)
    total_sources += source_count

    print(
        f"{filename:40s} "
        f"{len(entries):6d} stations, "
        f"{source_count:6d} sources"
    )


print()
print("----------------------------------------")
print(f"Input records       : {len(stations)}")
print(f"Combined stations   : {total_entries}")
print(f"Stream sources kept : {total_sources}")
print(f"Country files       : {len(combined_by_country)}")
print("----------------------------------------")

print()
print("Field usage in input data:")
print()

for field, count in field_counts.items():
    percentage = count / len(stations) * 100
    print(
        f"{field:20s}: "
        f"{count:6d} "
        f"({percentage:5.1f}%)"
    )

print()
print("Country files are written to:")
print(f"    {OUTPUT_DIR}")
print("Next push it to the repository:")
print("git remote set-url origin git@github.com:rocus/radio-online-json-url.git")
print("git push -u origin main")
print()
