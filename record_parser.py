from models import Record, CallNumber
from url_analyzer import URLAnalyzer
try:
    import xml.etree.cElementTree as ElementTree
except ImportError:
    import xml.etree.ElementTree as ElementTree


class CatalogXMLParser:

    def __init__(self, file_path):
        self.file_path = file_path
        self.namespace_map = {}

    def parse(self):
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

        for event, elem in ElementTree.iterparse(self.file_path, events=('end', 'start-ns')):
            if event == 'start-ns':  # Namespace definition
                ns, url = elem
                self.namespace_map[ns] = url
            elif event == 'end':  # End of tag parse
                tag = self.fix_tag('', 'record')
                if elem.tag == tag:
                    rec = self.process_record(elem)
                    records.append(rec)  # Add parsed record to our list
                    elem.clear()  # Clear branch from memory so memory usage doesn't explode when handling massive XML files
                    if len(records) % 1000 == 0:
                        print('Processed {} records'.format(len(records)))

        return records

    def process_record(self, record_elem):

        # Pull out the record ID (<controlfield tag="001">...</controlfield>)
        record_id = record_elem.find(self.fix_tag('', 'controlfield[@tag="001"]')).text

        # Resolve the call number
        call_number = self.parse_record_call_number(record_elem)

        # Pull out all the potential URLs
        potential_url_subfields = record_elem.findall(self.fix_tag('', 'datafield[@tag="856"]'))

        # Extract the URLs from those elements
        urls = URLAnalyzer.get_urls(potential_url_subfields)

        # Create a new Record object to store the results and add it to our list
        return Record(record_id, call_number, urls)

    def fix_tag(self, namespace, tag):
        """ Returns the ElementTree tag given the tag name and namespace map (to deal with a quirk of ElementTree) """
        return '{{{}}}{}'.format(self.namespace_map[namespace], tag)  # Double-bracket weirdness is to escape bracket, renders: {ns_map[namespace]}tag

    def parse_record_call_number(self, elem):

        field_050 = elem.find(self.fix_tag('', 'datafield[@tag="050"]'))
        if field_050:  # There's a field 050, so pull the call number from there
            a = field_050.find(self.fix_tag('', 'subfield[@code="a"]'))
            if a is not None:
                a = a.text
            b = field_050.find(self.fix_tag('', 'subfield[@code="b"]'))
            if b is not None:
                b = b.text
        else:  # No field 050, so see if there's a field 090
            field_090 = elem.find(self.fix_tag('', 'datafield[@tag="090"]'))
            if field_090 is None:  # No call number for this record, so just return None
                return None

            # There is a field 090, so pull the call number from that
            a = field_090.find(self.fix_tag('', 'subfield[@code="a"]'))
            if a is not None:
                a = a.text
            b = field_090.find(self.fix_tag('', 'subfield[@code="b"]'))
            if b is not None:
                b = b.text
        cn = CallNumber(a, b)
        return cn
