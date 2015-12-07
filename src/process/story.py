""" Defines a Story class, which contains the plain
text version of a story, in addition to the story broken
into various tokens that will be used multiple times
"""
import nltk.data
import unittest
from retrieval.get_book_by_id import main as get_book_by_id
from stat_parser import Parser

class Story:
    def __init__(self, book_id, plain_text=None):
        self.book_id = book_id
        if plain_text == None:
            self.plain_text = get_book_by_id(book_id)
        else:
            self.plain_text = plain_text
        # Remove whitespace
        self.plain_text = self.plain_text.replace("\r\n", " ")
        # Calculate these as needed
        self._sentences = None
        self._words = None
        self._pos = None
        self._tagged_sentences = None

    @property
    def sentences(self):
        if self._sentences == None:
            # Should this be moved to a global access place? To avoid re-reading?
            sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
            self._sentences = sent_detector.tokenize(self.plain_text.strip())
        return self._sentences

    @property
    def words(self):
        if self._words == None:
            self._words = nltk.word_tokenize(self.plain_text)
        return self._words
    @property
    def pos_words(self):
        if self._pos == None:
            self._pos = nltk.pos_tag(self.words)
        return self._pos
    
class StoryTests(unittest.TestCase):
    def setUp(self):
        self.book = Story(2701)
    def test_can_get_sentences(self):
        self.assertNotEqual(None, self.book.sentences)
    def test_can_get_words(self):
        self.assertNotEqual(None, self.book.words)
    def test_can_get_pos(self):
        self.assertNotEqual(None, self.book.pos_words)

if __name__ == "__main__":
    unittest.main()
