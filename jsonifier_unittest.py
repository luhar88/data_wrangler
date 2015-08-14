__author__ = 'panchal'

import unittest
import os
import json
import re

from jsonifier import Jsonifier

TEMP_TEST_DIRECTORY = 'tmp_jsonifier_test'
TEST_DATA_FILE = os.path.join(TEMP_TEST_DIRECTORY, 'test_data.in')
TEST_OUTPUT_FILE = os.path.join(TEMP_TEST_DIRECTORY, 'test.out')

# First 6 invalid entries, next 4 valid entries
TEST_DATA = """0.547777482345
McGrath, Luke, (555)-11111-11111111, gray, 70646
Julian, Fanning, 82820, 555 11111 11111111, red

asdfsdafdsa
Marita Haugland, red, 21231, 034 614 7966
Ria Tillotson, aqua marine, 97671, 196 910 5548
Annalee, Loftis, 97296, 905 329 2054, blue
James Johnston, gray, 38410, 628 102 3672
Liptak, Quinton, (653)-889-7235, yellow, 70703"""

INVALID_ENTRY_COUNT = 6
VALID_ENTRY_COUNT = 4


class JsonifierCheckDataTestCase(unittest.TestCase):
    def setUp(self):
        """ Setup the initial data for the tests"""
        if not os.path.exists(TEMP_TEST_DIRECTORY):
            os.mkdir(TEMP_TEST_DIRECTORY)
        # Create test data file with valid entries
        with open(TEST_DATA_FILE, 'w') as f:
            for entry in TEST_DATA.splitlines():
                f.write("{0}\n".format(entry))
        j = Jsonifier(data_file=TEST_DATA_FILE, output_file=TEST_OUTPUT_FILE)
        j.jsonify_data()

    def test_output_file_created(self):
        """ Tests if test.out is created"""
        self.assertTrue(os.path.exists(TEST_OUTPUT_FILE))

    def test_valid_phone_numbers(self):
        """ Tests if phone numbers in the processed entries are valid"""
        with open(TEST_OUTPUT_FILE, 'r') as f:
            data = json.load(f)
        phone_numbers = [x['phonenumber'] for x in data['entries']]
        pattern = re.compile(r'^[\d]{3}-[\d]{3}-[\d]{4}$')
        validation = True
        for p in phone_numbers:
            if not pattern.match(p):
                validation = False
        self.assertTrue(validation)

    def test_valid_zipcodes(self):
        """ Tests if zipcodes in the processed entries are valid"""
        with open(TEST_OUTPUT_FILE, 'r') as f:
            data = json.load(f)
        zipcode = [x['zipcode'] for x in data['entries']]
        pattern = re.compile(r'^[\d]{5}$')
        validation = True
        for z in zipcode:
            if not pattern.match(z):
                validation = False
        self.assertTrue(validation)

    def test_valid_entry_count(self):
        """ Checks the valid entry count"""
        with open(TEST_OUTPUT_FILE, 'r') as f:
            data = json.load(f)
        self.assertTrue(len(data['entries']) == VALID_ENTRY_COUNT)

    def test_invalid_invalid_count(self):
        """ Checks the invalid entry count"""
        with open(TEST_OUTPUT_FILE, 'r') as f:
            data = json.load(f)
        self.assertTrue(len(data['error']) == INVALID_ENTRY_COUNT)

    def tearDown(self):
        """ Cleanup data after tests are complete"""
        if os.path.exists(TEMP_TEST_DIRECTORY):
            if os.path.exists(TEST_DATA_FILE):
                os.remove(TEST_DATA_FILE)
            if os.path.exists(TEST_OUTPUT_FILE):
                os.remove(TEST_OUTPUT_FILE)
            os.removedirs(TEMP_TEST_DIRECTORY)

if __name__ == '__main__':
    unittest.main()
