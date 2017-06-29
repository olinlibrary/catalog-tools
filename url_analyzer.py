from urllib.parse import urlparse

try:
    import xml.etree.cElementTree as ElementTree
except ImportError:
    import xml.etree.ElementTree as ElementTree


class URLAnalyzer:

    @staticmethod
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
        # tree = ElementTree.parse(file_path)

        # Create a list to store the processed records in
        records = []
        namespace_map = {}

        # for record in tree.findall('./record'):
        for event, elem in ElementTree.iterparse(file_path, events=('end', 'start-ns')):
            if event == 'start-ns':  # Namespace definition
                ns, url = elem
                namespace_map[ns] = url
            elif event == 'end':  # End of tag parse
                tag = URLAnalyzer.fix_tag('', 'record', namespace_map)
                if elem.tag == tag:
                    rec = URLAnalyzer.process_record(elem, namespace_map)
                    records.append(rec)  # Add parsed record to our list
                    elem.clear()  # Clear branch from memory so memory usage doesn't explode when handling massive XML files
                    if len(records) % 1000 == 0:
                        print('Processed {} records'.format(len(records)))

        return records


    @staticmethod
    def process_record(record_elem, namespace_map):

        # Pull out the record ID (<controlfield tag="001">...</controlfield>)
        record_id = record_elem.find(URLAnalyzer.fix_tag('', 'controlfield[@tag="001"]', namespace_map)).text

        # Pull out all the potential URLs
        potential_url_subfields = record_elem.findall(URLAnalyzer.fix_tag('', 'datafield[@tag="856"]', namespace_map))

        # Extract the URLs from those elements
        urls = URLAnalyzer.get_urls(potential_url_subfields)

        # Create a new Record object to store the results and add it to our list
        return Record(record_id, urls)



    @staticmethod
    def fix_tag(ns, tag, ns_map):
        """ Returns the ElementTree tag given the tag name and namespace map (to deal with a quirk of ElementTree) """
        return '{{{}}}{}'.format(ns_map[ns], tag)  # Double-bracket weirdness is to escape bracket, renders: {ns_map[ns]}tag


    @staticmethod
    def get_urls(subfield_list):
        """ Takes a list of subfields and returns the URLs found in them
            :param subfield_list: a list of ElementTree elements
            :returns a list of URLs (as strings) found in the elements
        """
        urls = []
        for subfield in subfield_list:
            if len(subfield) > 0:
                # This element contains children, which means the URL is in one of them, not this element
                urls.extend(URLAnalyzer.get_urls(subfield))
            else:
                # Since there are no children, this element might contain the URL
                value = subfield.text
                if URL.is_url(value):
                    # Add this URL to our list
                    urls.append(URL(value))

        # Return the list of found URLs
        return urls


    @staticmethod
    def group_records_by_domain(records):
        domain_groups = {}  # Group each record by the domains of its URLs. If it is has multiple URLs with different domains,
                                # the record will be included in multiple groups
        url_counts = {}  # Keep track of how many records have 1 URL, 2 URLs, etc
        for record in records:
            # Count the number of records with each number of associated URLs
            num_urls = len(record.urls)
            if num_urls not in url_counts:
                url_counts[num_urls] = 1
            else:
                url_counts[num_urls] += 1

            # Group the records by domain
            for url in record.urls:
                if url.domain in domain_groups:
                    domain_groups[url.domain].add_record(record)
                else:
                    domain_groups[url.domain] = RecordGroup(url.domain, [record])

        return domain_groups, url_counts


class Record:
    """ Model for storing information about a catalog record. """

    def __init__(self, record_id, urls):
        self.id = record_id
        self.urls = urls

    def __str__(self):
        result = 'Record {} URLs:'.format(self.id)
        for url in self.urls:
            result += '\n\tDomain: ' + url.domain + ((' on port ' + str(url.port)) if url.port else '')
        return result


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


# If this program is being run on its own (rather than imported
# from another module), run the following
if __name__ == '__main__':
    file_path = '/media/sf_ubuntu-vm-shared/URLs.xml'
    records = URLAnalyzer.parse_xml(file_path)
    # print_records(records)
    groups, counts = URLAnalyzer.group_records_by_domain(records)

    output_file = open(file_path + '-processed.txt')

    for name, group in groups.items():
        print(group)
        output_file.write(group)

    print('Found the following number of records with specific numbers of URLs:')
    print(counts)
    output_file.write(counts)
    output_file.close()
