"""
Python script for looking up school FIPS codes
Author: Chris Baudouin, Jr <cbaudouinjr@mail.rit.edu>
"""
import os
import requests

SCHOOLS_INPUT_FILE = ""
SCHOOLS_OUTPUT_FILE = ""

GC_API_KEY = os.environ.get('GC_API_KEY')
checked_schools = {}  # Used to remove any possible duplicate schools
state_city_fips_cache = {}  # Used to reduce number of GC API requests


class APIKeyError(Exception):
    """
    Custom Exception to handle non-existent Google Cloud API key
    """
    pass


def build_school_csv():
    """
    Reads in schools.csv, calculates coordinates and identifies FIPS code
    :return: None
    """
    schools_file = open(SCHOOLS_INPUT_FILE, "r")
    school_line = schools_file.readline()

    if GC_API_KEY is None:
        raise APIKeyError('GC API key not found')

    while school_line != "":
        school_data = school_line.split(',')
        school = school_data[0].rstrip()
        address = school_data[1].replace(' ', '+').rstrip()
        city = school_data[2].replace(' ', '+').rstrip()
        state = school_data[3].replace(' ', '+').rstrip()

        if school == "name" \
                or school == "None" \
                or school == '' \
                or address == '' \
                or city == '' \
                or state == '' \
                or school in checked_schools:
            school_line = schools_file.readline()
            continue

        if state in state_city_fips_cache:
            if city in state_city_fips_cache[state]:
                write_to_file(school, address, city, state, state_city_fips_cache[state][city])
                print("Loading from cache: " + school)
                continue

        print("Fetching data for: " + school)
        address_lookup_endpoint = f'https://maps.googleapis.com/maps/api/geocode/json?' \
                                  f'address={address},+{city},+{state}&' \
                                  f'key={GC_API_KEY}'

        response = requests.get(address_lookup_endpoint).json()

        if len(response['results']) == 0 or response['status'] != "OK":
            abort(school, address, city, state)
            continue

        try:
            location = response['results'][0]['geometry']['location']
            lat = location['lat']
            lng = location['lng']

            fips_endpoint = f'https://geo.fcc.gov/api/census/area?lat={lat}&lon={lng}&format=json'
            fips_response = requests.get(fips_endpoint).json()

            if len(fips_response['results']) == 0 or len(fips_response['results'][0]["county_fips"]) == 0:
                abort(school, address, city, state)
                continue

            fips_code = fips_response['results'][0]["county_fips"]
            write_to_file(school, address, city, state, fips_code)

        except KeyError:
            abort(school, address, city, state)
            continue

        school_line = schools_file.readline()


def abort(school, address, city, state):
    """
    Called if no FIPS code could be found or if any other error occurred, saves school with FIPS as None
    :param school: School that was attempted
    :param address: Address of school
    :param city: City of school
    :param state: State of school
    :return: None
    """
    print(f'Could not find data for {school}')
    write_to_file(school, address, city, state)


def write_to_file(school, address, city, state, fips=None):
    """
    Writes school with possible FIPS code to the SCHOOL_OUTPUT_FILE
    :param school: School that was queried
    :param address: Address of school
    :param city: City of school
    :param state: State of school
    :param fips: FIPS code for school, None if not found or error
    :return: None
    """
    output_file = open(SCHOOLS_OUTPUT_FILE, "a")
    address = address.replace('+', ' ')

    if fips is not None:
        output_file.write(school + ',' + address + ',' + city + ',' + state + ',' + fips + '\n')
    else:
        output_file.write(school + ',' + address + ',' + city + ',' + state + ',' + "NONE" + '\n')
    if state in state_city_fips_cache:
        state_city_fips_cache[state][city] = fips
    else:
        state_city_fips_cache[state] = {}
        state_city_fips_cache[state][city] = fips
    checked_schools[school] = None
    output_file.close()


if __name__ == "__main__":
    build_school_csv()
