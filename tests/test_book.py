import unittest
from LMS import Book

class TestBook(unittest.TestCase):
    def test_to_from_dict(self):
        b = Book("123", "Title", "Author", 2020, copies=2)
        d = b.to_dict()
        self.assertEqual(d["isbn"], "123")
        b2 = Book.from_dict(d)
        self.assertEqual(b2.title, "Title")
        self.assertEqual(b2.copies, 2)

if __name__ == "__main__":
    unittest.main()
