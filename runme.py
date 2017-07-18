from record_parser import CatalogXMLParser
from url_analyzer import URLAnalyzer
from models import CallNumberComparator

# If this program is being run on its own (rather than imported
# from another module), run the following
if __name__ == '__main__':
    file_path = '/media/sf_ubuntu-vm-shared/Call Numbers.xml'
    parser = CatalogXMLParser(file_path)
    records = parser.parse()


    records_sorted = sorted(records, cmp=CallNumberComparator.compare)
    print(records_sorted)
    # groups, counts, records_with_2_urls = URLAnalyzer.group_records_by_domain(records)
    #
    # output_file = open(file_path + '-processed.txt', 'w+')
    #
    # for name, group in groups.items():
    #     print(group)
    #     output_file.write(str(group)+'\n')
    #
    # print('Number of records found with a given number of associated URLs (i.e. {url_count: record_count}):')
    # print(counts)
    # output_file.write(str(counts))
    #
    # output_file.write('\nRecords with 2 URLs:\n')
    # output_file.write(','.join((str(rec) for rec in records_with_2_urls)))
    # output_file.close()
