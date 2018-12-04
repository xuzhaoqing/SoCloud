
# Copyright (C) 2011 by Peter Goodman
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import urllib2
import urlparse
from BeautifulSoup import *
from collections import defaultdict
import re
import numpy as np
import sqlite3 as lite

def attr(elem, attr):
    """An html attribute from an html element. E.g. <a href="">, then
    attr(elem, "href") will get the href or an empty string."""
    try:
        return elem[attr]
    except:
        return ""

WORD_SEPARATORS = re.compile(r'\s|\n|\r|\t|[^a-zA-Z0-9\-_]')

class crawler(object):
    """Represents 'Googlebot'. Populates a database by crawling and indexing
    a subset of the Internet.

    This crawler keeps track of font sizes and makes it simpler to manage word
    ids and document ids."""

    def __init__(self, db_conn, url_file):
        """Initialize the crawler with a connection to the database to populate
        and with the file containing the list of seed URLs to begin indexing."""
        self._url_queue = [ ]
        self._doc_id_cache = { }
        self._word_id_cache = { }

        self._con = None
        self._cur = None
        self._word_inv_idx = defaultdict(set)
        # functions to call when entering and exiting specific tags
        self._enter = defaultdict(lambda *a, **ka: self._visit_ignore)
        self._exit = defaultdict(lambda *a, **ka: self._visit_ignore)

        # add a link to our graph, and indexing info to the related page
        self._enter['a'] = self._visit_a

        # record the currently indexed document's title an increase
        # the font size
        def visit_title(*args, **kargs):
            self._visit_title(*args, **kargs)
            self._increase_font_factor(7)(*args, **kargs)

        # increase the font size when we enter these tags
        self._enter['b'] = self._increase_font_factor(2)
        self._enter['strong'] = self._increase_font_factor(2)
        self._enter['i'] = self._increase_font_factor(1)
        self._enter['em'] = self._increase_font_factor(1)
        self._enter['h1'] = self._increase_font_factor(7)
        self._enter['h2'] = self._increase_font_factor(6)
        self._enter['h3'] = self._increase_font_factor(5)
        self._enter['h4'] = self._increase_font_factor(4)
        self._enter['h5'] = self._increase_font_factor(3)
        self._enter['title'] = visit_title

        # decrease the font size when we exit these tags
        self._exit['b'] = self._increase_font_factor(-2)
        self._exit['strong'] = self._increase_font_factor(-2)
        self._exit['i'] = self._increase_font_factor(-1)
        self._exit['em'] = self._increase_font_factor(-1)
        self._exit['h1'] = self._increase_font_factor(-7)
        self._exit['h2'] = self._increase_font_factor(-6)
        self._exit['h3'] = self._increase_font_factor(-5)
        self._exit['h4'] = self._increase_font_factor(-4)
        self._exit['h5'] = self._increase_font_factor(-3)
        self._exit['title'] = self._increase_font_factor(-7)

        # never go in and parse these tags
        self._ignored_tags = set([
            'meta', 'script', 'link', 'meta', 'embed', 'iframe', 'frame', 
            'noscript', 'object', 'svg', 'canvas', 'applet', 'frameset', 
            'textarea', 'style', 'area', 'map', 'base', 'basefont', 'param',
        ])

        # set of words to ignore
        self._ignored_words = set([
            '', 'the', 'of', 'at', 'on', 'in', 'is', 'it',
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
            'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
            'u', 'v', 'w', 'x', 'y', 'z', 'and', 'or',
        ])

        # TODO remove me in real version
        self._mock_next_doc_id = 1
        self._mock_next_word_id = 1

        # keep track of some info about the page we are currently parsing
        self._curr_depth = 0
        self._curr_url = ""
        self._curr_doc_id = 0
        self._font_size = 0
        self._curr_words = None  #This is the list of words id

        # get all urls into the queue
        try:
            with open(url_file, 'r') as f:
                for line in f:
                    self._url_queue.append((self._fix_url(line.strip(), ""), 0))
        except IOError:
            pass
    
    def create_db(self,db_name):
        self._con = lite.connect(db_name)
        self._cur = self._con.cursor()
        self._cur.execute("DROP TABLE IF EXISTS lexicon;")
        self._cur.execute("DROP TABLE IF EXISTS document;")
        self._cur.execute("DROP TABLE IF EXISTS inv_idx;")
        self._cur.execute("DROP TABLE IF EXISTS relation;")
        self._cur.execute("DROP TABLE IF EXISTS score;")
        self._cur.execute("CREATE TABLE IF NOT EXISTS lexicon (word_idx INTEGER, word TEXT); ")
        self._cur.execute("CREATE TABLE IF NOT EXISTS document (doc_idx INTEGER, link TEXT UNIQUE);")
        self._cur.execute("CREATE TABLE IF NOT EXISTS inv_idx (word_idx INTEGER, doc_idx INTEGER);")
        self._cur.execute("CREATE TABLE IF NOT EXISTS relation (from_url INTEGER, to_url INTEGER);")
        self._cur.execute("CREATE TABLE IF NOT EXISTS score  (doc_idx INTEGER, rank INTEGER);")

    # TODO remove me in real version
    def _mock_insert_document(self, url):
        """A function that pretends to insert a url into a document db table
        and then returns that newly inserted document's id."""
        ret_id = self._mock_next_doc_id
        self._mock_next_doc_id += 1
        if self._con != None and url != "":
            self._cur.execute("INSERT INTO document VALUES('%s', '%s');" % (ret_id, url))
            self._con.commit()
        return ret_id 
    
    # TODO remove me in real version
    def _mock_insert_word(self, word):
        """A function that pretends to instrt a word into the lexicon db table
        and then returns that newly inserted word's id."""
        ret_id = self._mock_next_word_id
        self._mock_next_word_id += 1
        if self._con != None:
            self._cur.execute("INSERT INTO lexicon VALUES ('%s', '%s');" % (ret_id, word))
            self._con.commit()
        return ret_id
    
    def word_id(self, word):
        """Get the word id of some specific word."""
        if word in self._word_id_cache:
            return self._word_id_cache[word]
        
        # TODO: 1) add the word to the lexicon, if that fails, then the
        #          word is in the lexicon
        #       2) query the lexicon for the id assigned to this word, 
        #          store it in the word id cache, and return the id.

        word_id = self._mock_insert_word(word)
        self._word_id_cache[word] = word_id
        return word_id
    
    def document_id(self, url):
        """Get the document id for some url."""
        if url in self._doc_id_cache:
            return self._doc_id_cache[url]
        
        # TODO: just like word id cache, but for documents. if the document
        #       doesn't exist in the db then only insert the url and leave
        #       the rest to their defaults.
        
        doc_id = self._mock_insert_document(url)
        self._doc_id_cache[url] = doc_id
        return doc_id
    
    def _fix_url(self, curr_url, rel):
        """Given a url and either something relative to that url or another url,
        get a properly parsed url."""

        rel_l = rel.lower()
        if rel_l.startswith("http://") or rel_l.startswith("https://"):
            curr_url, rel = rel, ""
            
        # compute the new url based on import 
        curr_url = urlparse.urldefrag(curr_url)[0]
        parsed_url = urlparse.urlparse(curr_url)
        return urlparse.urljoin(parsed_url.geturl(), rel)

    def add_link(self, from_doc_id, to_doc_id):
        """Add a link into the database, or increase the number of links between
        two pages in the database."""
        # TODO
        if self._con != None:
            self._cur.execute("INSERT INTO relation VALUES('%s', '%s');" % (from_doc_id, to_doc_id))
            self._con.commit()

    def _visit_title(self, elem):
        """Called when visiting the <title> tag."""
        title_text = self._text_of(elem).strip()
        print("document title="+ repr(title_text))

        # TODO update document title for document id self._curr_doc_id
    
    def _visit_a(self, elem):
        """Called when visiting <a> tags."""

        dest_url = self._fix_url(self._curr_url, attr(elem,"href"))

        #print "href="+repr(dest_url), \
        #      "title="+repr(attr(elem,"title")), \
        #      "alt="+repr(attr(elem,"alt")), \
        #      "text="+repr(self._text_of(elem))

        # add the just found URL to the url queue
        self._url_queue.append((dest_url, self._curr_depth))
        
        # add a link entry into the database from the current document to the
        # other document
        self.add_link(self._curr_doc_id, self.document_id(dest_url))

        # TODO add title/alt/text to index for destination url
    
    def _add_words_to_document(self):
        # TODO: knowing self._curr_doc_id and the list of all words and their
        #       font sizes (in self._curr_words), add all the words into the
        #       database for this document
        print("    num words="+ str(len(self._curr_words)))
        for (curr_word_id, _) in self._curr_words:
            self._word_inv_idx[curr_word_id].add(self._curr_doc_id)
            self._cur.execute("INSERT INTO inv_idx VALUES('%s', '%s');" % (curr_word_id, self._curr_doc_id))
        self._con.commit()

    def _increase_font_factor(self, factor):
        """Increade/decrease the current font size."""
        def increase_it(elem):
            self._font_size += factor
        return increase_it
    
    def _visit_ignore(self, elem):
        """Ignore visiting this type of tag"""
        pass

    def _add_text(self, elem):
        """Add some text to the document. This records word ids and word font sizes
        into the self._curr_words list for later processing."""
        words = WORD_SEPARATORS.split(elem.string.lower())
        for word in words:
            word = word.strip()
            if word in self._ignored_words:
                continue
            self._curr_words.append((self.word_id(word), self._font_size))
        
    def _text_of(self, elem):
        """Get the text inside some element without any tags."""
        if isinstance(elem, Tag):
            text = [ ]
            for sub_elem in elem:
                text.append(self._text_of(sub_elem))
            
            return " ".join(text)
        else:
            return elem.string

    def _index_document(self, soup):
        """Traverse the document in depth-first order and call functions when entering
        and leaving tags. When we come accross some text, add it into the index. This
        handles ignoring tags that we have no business looking at."""
        class DummyTag(object):
            next = False
            name = ''
        
        class NextTag(object):
            def __init__(self, obj):
                self.next = obj
        
        tag = soup.html
        stack = [DummyTag(), soup.html]

        while tag and tag.next:
            tag = tag.next

            # html tag
            if isinstance(tag, Tag):

                if tag.parent != stack[-1]:
                    self._exit[stack[-1].name.lower()](stack[-1])
                    stack.pop()

                tag_name = tag.name.lower()

                # ignore this tag and everything in it
                if tag_name in self._ignored_tags:
                    if tag.nextSibling:
                        tag = NextTag(tag.nextSibling)
                    else:
                        self._exit[stack[-1].name.lower()](stack[-1])
                        stack.pop()
                        tag = NextTag(tag.parent.nextSibling)
                    
                    continue
                
                # enter the tag
                self._enter[tag_name](tag)
                stack.append(tag)

            # text (text, cdata, comments, etc.)
            else:
                self._add_text(tag)

    # This is a reference algorithm for PageRank 
    def page_rank(self, num_iterations=20, initial_pr=1.0):
        if self._cur != None:
            self._cur.execute("SELECT * FROM relation;")
            links = self._cur.fetchall()
            page_rank = defaultdict(lambda: float(initial_pr))
            num_outgoing_links = defaultdict(float)
            incoming_link_sets = defaultdict(set)
            incoming_links = defaultdict(lambda: np.array([]))
            damping_factor = 0.85

            # collect the number of outbound links and the set of all incoming documents
            # for every document
            for (from_id,to_id) in links:
                num_outgoing_links[int(from_id)] += 1.0
                incoming_link_sets[to_id].add(int(from_id))
            
            # convert each set of incoming links into a numpy array
            for doc_id in incoming_link_sets:
                incoming_links[doc_id] = np.array([from_doc_id for from_doc_id in incoming_link_sets[doc_id]])

            num_documents = float(len(num_outgoing_links))
            lead = (1.0 - damping_factor) / num_documents 
            partial_PR = np.vectorize(lambda doc_id: page_rank[doc_id] / num_outgoing_links[doc_id])

            for _ in xrange(num_iterations):
                for doc_id in num_outgoing_links:
                    tail = 0.0
                    if len(incoming_links[doc_id]):
                        tail = damping_factor * partial_PR(incoming_links[doc_id]).sum()
                    page_rank[doc_id] = lead + tail
            for item in page_rank:
                self._cur.execute("INSERT OR REPLACE INTO score VALUES ('%s', '%s');" % (item, page_rank[item]))
            self._con.commit()

    def get_inverted_index(self):
	"""for every index of the word, given the indexes of the documents that reference them"""
	    # if we didn't call the crawl function, call it	
        if not self._curr_words:  
            self.crawl(depth=1) 
        # we have saved the results into _word_inv_idx, so just return it
        return self._word_inv_idx 
  
    def get_resolved_inverted_index(self):
	"""for every word, given the documents that reference them"""
	# a dict that saves the word and related documents	
        word_res_inv_idx = defaultdict(set) 
        # id_word_cache is a dict that is like: word = id_word_cache[index]
        id_word_cache = {idx:word for word,idx in self._word_id_cache.items()}
        # id_doc_cache is a dict: docs = id_doc_cache[index]
        id_doc_cache = {idx:doc for doc,idx in self._doc_id_cache.items()}

        for (word_idx, docs_idx) in self._word_inv_idx.items():
            # find the word according to its index
            word = id_word_cache[word_idx] 
            # find the dics according to their indexes
            docs = set([id_doc_cache[doc_idx] for doc_idx in list(docs_idx)])
            # link the docs with words
            word_res_inv_idx[word] = docs
        return word_res_inv_idx


 

    
        
    def crawl(self, depth=2, timeout=3):
        """Crawl the web!"""
        seen = set()
        self.create_db("links.db")

        while len(self._url_queue):

            url, depth_ = self._url_queue.pop()

            # skip this url; it's too deep
            if depth_ > depth:
                continue

            doc_id = self.document_id(url)

            # we've already seen this document
            if doc_id in seen:
                continue

            seen.add(doc_id) # mark this document as haven't been visited
            
            socket = None
            try:
                socket = urllib2.urlopen(url, timeout=timeout)
                soup = BeautifulSoup(socket.read())

                self._curr_depth = depth_ + 1
                self._curr_url = url
                self._curr_doc_id = doc_id
                self._font_size = 0
                self._curr_words = [ ]
                self._index_document(soup)
                self._add_words_to_document()
                print("    url="+repr(self._curr_url))

            except Exception as e:
                print(e)
                pass
            finally:
                if socket:
                    socket.close()

        self.page_rank()
        self._con.close()

if __name__ == "__main__":
    bot = crawler(None, "urls.txt")
    bot.crawl(depth=1)

