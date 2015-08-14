__author__ = 'mukulpanchal'

import os
import sys
import re
import json
import time
import logging

LOG_PATH = os.path.join('logs', '{0}_jsonifier.log'.format((str(time.time()).split('.')[0])))
OUTPUT_FILE = 'result.out'

if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(
    filename=LOG_PATH,
    filemode='w',
    format='%(asctime)s %(levelname)-5s : %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.INFO
)


class Jsonifier(object):
    """ Reads a data file, parses the information into json and writes to output file

    Reads the data file line by line, parses the entries.
    Checks for either of the following patterns in the entry:
        Lastname, Firstname, (703)-742-0996, Blue, 10013
        Firstname Lastname, Red, 11237, 703 955 0373
        Firstname, Lastname, 10013, 646 111 0101, Green
    creates a json object, and writes to OUTPUT_FILE
    Compatible with python 2.7.x

    Keyword Arguments:
    data_file -- Input data file that contains the entries to read
    output_file -- Output file to write the json object to (Default: result.out)

    Usage:
    >>> j = Jsonifier(data_file_path='data.in', output_file='result.out')
    >>> j.jsonify_data()

    Will read the entries in the data.in file and write a json object with 2 keys,
    'entries' and 'error'. Entries with invalid phone numbers or zipcode are
    classified as invalid entries

    i.e.

    For the input
        Booker T., Washington, 87360, 373 781 7380, yellow
        Chandler, Kerri, (623)-668-9293, pink, 123123121
        James Murphy, yellow, 83880, 018 154 6474
        asdfawefawea

    We should receive the output
        {
            "entries": [
                {
                "color": "yellow",
                "firstname": "James",
                "lastname": "Murphy",
                "phonenumber": "018-154-6474",
                "zipcode": "83880"
                },
                {
                "color": "yellow",
                "firstname": "Booker T.",
                "lastname": "Washington",
                "phonenumber": "373-781-7380",
                "zipcode": "87360"
                } ],
            "errors": [ 1,
                3 ]
        }
    Keys in entries are sorted bu key name, values are sorted by lastname, firstname.
    """
    def __init__(self, **kwargs):
        """Initialize the Jsonifier object with data file

        Keyword arguments:
        data_file -- The location of the data file to read
        output_file -- The output file to write to

        Raises:
        ValueError if data_file is not entered
        """
        self.__line = 0
        self.__error_count = 0
        self.__output = {}
        if 'data_file' in kwargs:
            self.data_file = kwargs['data_file']
        else:
            logging.error("Enter a data file path to read")
            raise ValueError
        if 'output_file' in kwargs:
            self.output_file = kwargs['output_file']
        else:
            self.output_file = OUTPUT_FILE

    def jsonify_data(self):
        """ Parses the entries in the data file, write json object to file

        Reads the data file line by line, parses the entries.
        Checks for either of the following patterns in the entry:
            Lastname, Firstname, (703)-742-0996, Blue, 10013
            Firstname Lastname, Red, 11237, 703 955 0373
            Firstname, Lastname, 10013, 646 111 0101, Green
        creates a json object, and writes to OUTPUT_FILE
         """
        self._process_data_file()
        self._write_json_output_to_file()
        logging.info("%s invalid entries", self.__error_count)
        logging.info("%s records processed", self.__line)

    def _process_data_file(self):
        """ Reads the data_file and generates the output"""
        errors = []
        entries = []
        if os.path.isfile(self.data_file):
            with open(self.data_file, 'r') as f:
                for entry in f:
                    parsed_entry = self._parse_record(entry)
                    if 'error' in parsed_entry:
                        # Append to error list
                        errors.append(self.__line)
                        self.__error_count += 1
                        logging.error("Invalid Entry Line %s -> %s",
                                      self.__line,
                                      ', '.join(parsed_entry['entry_information']))
                    else:
                        # Append to entry list
                        entries.append(parsed_entry)
                        logging.info("Successfully processed entry")
                    self.__line += 1
            # sort entries according to lastname, firstname
            entries_firstname_sorted = sorted(entries, key=lambda x: x['firstname'])
            entries_sorted = sorted(entries_firstname_sorted, key=lambda x: x['lastname'])
            self.__output = {
                'entries': entries_sorted,
                'error': errors
            }
        else:
            logging.error("Incorrect file_path - '%s'", self.data_file)

    def _write_json_output_to_file(self):
        """ Writes parsed information as json object to output file"""
        try:
            with open(self.output_file, 'w') as f:
                f.write(json.dumps(self.__output, f, sort_keys=True, indent=2))
        except IOError:
            logging.error("Unable to write to result.out")
        else:
            logging.info("Output written to result.out")

    def _parse_record(self, user_entry):
        """ Parses an entry and returns a dictionary object"""
        entry_information = map(lambda x: self._encode_if_possible(x.strip(), 'utf-8'),
                                user_entry.strip().split(','))
        user_entry_pattern = self._check_pattern(entry_information)
        if user_entry_pattern == 1:
            color = entry_information[3]
            first_name = entry_information[1]
            last_name = entry_information[0]
            phone_number = self._format_phone_number(
                str(self._clean_number(entry_information[2]))
            )
            zip_code = entry_information[4]

        elif user_entry_pattern == 2:
            color = entry_information[1]
            full_name = entry_information[0].split()
            first_name = " ".join(full_name[0:-1])
            last_name = full_name[-1]
            phone_number = self._format_phone_number(
                str(self._clean_number(entry_information[3]))
            )
            zip_code = entry_information[2]

        elif user_entry_pattern == 3:
            color = entry_information[4]
            first_name = entry_information[0]
            last_name = entry_information[1]
            phone_number = self._format_phone_number(
                str(self._clean_number(entry_information[3]))
            )
            zip_code = entry_information[2]

        else:
            return {
                'error': self.__line,
                'entry_information': entry_information
            }

        return {
            'color': color,
            'firstname': first_name,
            'lastname': last_name,
            'phonenumber': phone_number,
            'zipcode': zip_code
        }

    def _check_pattern(self, entry):
        """ Checks as to which pattern an entry belongs to and returns the pattern number"""
        entry_size = len(entry)
        pattern = 0
        # Check for "Firstname Lastname, Red, 11237, 703 955 0373" pattern
        if entry_size == 4:
            if self._check_entry_validity(phone_number=entry[3], zipcode=entry[2]):
                pattern = 2
        elif entry_size == 5:
            # Check for "Lastname, Firstname, (703)-742-0996, Blue, 10013" pattern
            if self._check_entry_validity(phone_number=entry[2], zipcode=entry[4]):
                pattern = 1
            # Check for "Firstname, Lastname, 10013, 646 111 0101, Green" pattern
            elif self._check_entry_validity(phone_number=entry[3], zipcode=entry[2]):
                pattern = 3
        return pattern

    def _check_entry_validity(self, **kwargs):
        """ Validates phone number and zipcode"""
        try:
            if 'phone_number' in kwargs and 'zipcode' in kwargs:
                # Remove non-digits
                cleaned_phone_number = self._clean_number(kwargs['phone_number'])
                cleaned_zipcode = self._clean_number(kwargs['zipcode'])

                # Remove leading 0's in the phone number
                temp_number = "0{}".format(cleaned_phone_number)
                p = re.match(r"^(0+)(\d+)$", temp_number)

                # Check if the phone number has 10 digits and the zipcode has 5 digits
                phone_number_pattern = r"^\d{10}$"
                zipcode_pattern = r"^\d{5}$"
                if re.match(phone_number_pattern, p.group(2)) and re.match(zipcode_pattern, cleaned_zipcode):
                    return True
            else:
                return False
        except AttributeError:
            return False

    @staticmethod
    def _clean_number(number):
        """ Removes ' ', '-', '(', ')' from the given number"""
        return filter(lambda x: x not in [' ', '-', '(', ')'], number)

    @staticmethod
    def _format_phone_number(phone_number):
        """ Formats a phone number as XXX-XXX-XXXX"""
        return "{}-{}-{}".format(phone_number[0:3],
                                 phone_number[3:6],
                                 phone_number[6:10])

    @staticmethod
    def _encode_if_possible(value, codec):
        """ Encodes the given value if possible into 'utf-8'"""
        if hasattr(value, 'utf-8'):
            return value.encode(codec)
        else:
            return value


def main():
    if len(sys.argv) > 1:
        j = Jsonifier(data_file=sys.argv[1])
        j.jsonify_data()
    else:
        print "Error: Please enter the data file path"
        print "Usage: "
        print ">python jsonifier.py data/data.in"


if __name__ == '__main__':
    main()
