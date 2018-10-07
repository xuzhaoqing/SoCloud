from crawler import crawler
crawler = crawler(None,'urls.txt')
inverted_index = crawler.get_inverted_index()
print inverted_index
resolved_inverted_index = crawler.get_resolved_inverted_index()
print resolved_inverted_index
