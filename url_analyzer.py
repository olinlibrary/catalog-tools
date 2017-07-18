from models import *


class URLAnalyzer:

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
        records_with_two_urls = []
        for record in records:
            # Count the number of records with each number of associated URLs
            num_urls = len(record.urls)
            if num_urls == 2:
                records_with_two_urls.append(record)
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

        return domain_groups, url_counts, records_with_two_urls
