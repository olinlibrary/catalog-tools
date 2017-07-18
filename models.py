from urllib.parse import urlparse
import re
import string


class CallNumber:

    def __init__(self, a, b):
        # Part a
        self.a = a
        a = a.replace('.', '')
        self.part_one = re.search(r'^[a-zA-Z]+', a)
        self.part_one = self.part_one.group(0).upper() if self.part_one else '0'
        self.part_two = re.search(r'\d+', a)
        self.part_two = self.part_two.group(0) if self.part_two else '0'

        # Part b
        self.b = b
        if b is not None:
            b = b.replace('.', '')
            self.cutter_alpha = re.search(r'^[a-zA-Z]+', b)
            self.cutter_alpha = self.cutter_alpha.group(0).upper() if self.cutter_alpha else ''
            if len(self.cutter_alpha) > 0:  # There is a letter in the second half
                self.cutter_number = re.search(r'[a-zA-z]*\d*\d+', b).group(0)
                self.edition = b[len(self.cutter_alpha)+len(self.cutter_number):]  # The rest (if any) is the edition
            else:  # There is no letter in the second half
                self.edition = b
            # decimal_and_year = re.findall(r'\d+', b)
            # for i, item in iter(decimal_and_year):

            # self.part_three = parts_three_and_five[0].upper() if len(parts_three_and_five) > 0 else 0
            # self.part_four = re.findall(r'\d+', b).group(0)
            # self.part_five = parts_three_and_five[1].upper() if len(parts_three_and_five) > 1 else 0
        else:
            # No part b defined
            self.part_three = ''
            self.part_four = self.part_five = 0

    def __str__(self):
        return self.a + self.b


class CallNumberComparator:
    @staticmethod
    def compare(a, b):
        # Look at the first components
        if a.part_one > b.part_one:
            return -1
        elif a.part_one < b.part_one:
            return 1
        # First components are equal, so look at the second component
        elif a.part_two > b.part_two:
            return -1
        elif a.part_two < b.part_two:
            return 1
        # First two components are equal, look at the third component
        elif a.cutter_alpha > b.cutter_alpha:
            return -1
        elif a.cutter_alpha < b.cutter_alpha:
            return 1
        # First three components are equal, look at the fourth component
        elif a.cutter_number > b.cutter_number:
            return -1
        elif a.cutter_number < b.cutter_number:
            return 1
        # First four components are equal, look at the fifth component
        elif a.edition > b.edition:
            return -1
        elif a.edition < b.edition:
            return 1
        # Call numbers are identical
        else:
            return 0


class Record:
    """ Model for storing information about a catalog record. """

    def __init__(self, record_id, call_number, urls):
        self.id = record_id
        self.call_number = call_number
        self.urls = urls

    def __str__(self):
        return str(self.id)


class RecordGroup:
    """ Model for keeping track of a group of records """

    def __init__(self, name, records=None):
        self.name = name
        self.records = records if records else []

    def add_record(self, record):
        self.records.append(record)

    def __str__(self):
        # record_numbers_list = ','.join([record.id for record in self.records])
        result = 'Record group {}:\n\tRecord count: {}'.format(self.name, len(self.records))
        return result


class URL:
    """ Model for keeping track of a URL and its components """

    def __init__(self, url_string):
        self.full_url = url_string
        parse_result = urlparse(url_string)
        self.protocol = parse_result.scheme  # e.g. http, ftp
        self.port = parse_result.port  # e.g. 80 for http, 21 for ftp (may be None)

        # netloc gives you the domain name with the port appended, which we'd like to separate
        self.domain = parse_result.netloc  # e.g. www.google.com:80
        # Strip the port number, if present
        if ':' in self.domain:
            colon_index = self.domain.find(':')  # Index of the colon in the string, e.g. 14
            self.domain = self.domain[:colon_index]  # e.g. www.google.com

        self.path = parse_result.path  # e.g. /resources/56.html

    @staticmethod
    def is_url(string):
        """ Determines whether or not a string is a URL
            :param string: a string to analyze
            :return True if the string is a URL, False otherwise
        """
        return '.com' in string
