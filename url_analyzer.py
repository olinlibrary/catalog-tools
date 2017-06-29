from urllib.parse import urlparse

try:
    import xml.etree.cElementTree as ElementTree
except ImportError:
    import xml.etree.ElementTree as ElementTree


def parse_xml(file_path):
    # Now that the XML is loaded into an object, we can reference the
    # elements in the tree (given the XML is formatted like so:
    # <collection>
    #   <record>
    #       <controlfield tag="###">...</controlfield>
    #       ...
    #   </record>
    #   ...
    # </collection>)
    tree = ElementTree.parse(file_path)

    # Create a list to store the processed records in
    records = []

    for record in tree.findall('./record'):
        # Pull out the record ID (<controlfield tag="001">...</controlfield>)
        record_id = record.find('./controlfield[@tag="001"]').text

        # Pull out all the potential URLs
        potential_url_subfields = record.findall('./datafield[@tag="856"]')

        # Extract the URls from those elements
        urls = get_urls(potential_url_subfields)

        # Create a new Record object to store the results and add it to our list
        rec = Record(record_id, urls)
        records.append(rec)

    return records


def get_urls(subfield_list):
    """ Takes a list of subfields and returns the URLs found in them
        :param subfield_list: a list of ElementTree elements
        :returns a list of URLs (as strings) found in the elements
    """
    urls = []
    for subfield in subfield_list:
        if len(subfield) > 0:
            # This element contains children, which means the URL is in one of them, not this element
            urls.extend(get_urls(subfield))
        else:
            # Since there are no children, this element might contain the URL
            value = subfield.text
            if URL.is_url(value):
                # Add this URL to our list
                urls.append(URL(value))

    # Return the list of found URLs
    return urls


def group_records_by_domain(records):
    groups = {}
    for record in records:
        for url in record.urls:
            if url.domain in groups:
                groups[url.domain].add_record(record)
            else:
                groups[url.domain] = RecordGroup(url.domain, [record])
    return groups


def print_records(records):
    for record in records:
        print(record)


class Record:

    def __init__(self, record_id, urls):
        self.id = record_id
        self.urls = urls

    def __str__(self):
        result = 'Record {} URLs:'.format(self.id)
        for url in self.urls:
            result += '\n\tDomain: ' + url.domain + ((' on port ' + str(url.port)) if url.port else '')
        return result


class RecordGroup:

    def __init__(self, name, records = None):
        self.name = name
        self.records = records if records else []

    def add_record(self, record):
        self.records.append(record)

    def __str__(self):
        record_numbers_list = ','.join([record.id for record in self.records])
        result = 'Record group {}:\n\tRecords: {}'.format(self.name, record_numbers_list)
        return result


class URL:

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


# If this program is being run on its own (rather than imported
# from another module), run the following
if __name__ == '__main__':
    file_path = '/media/sf_ubuntu-vm-shared/URLs-100.xml'
    records = parse_xml(file_path)
    # print_records(records)
    groups = group_records_by_domain(records)

    for name, group in groups.items():
        print(group)
