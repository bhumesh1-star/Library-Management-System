import unittest
import os
from LMS import LibrarySystem, Book

TEST_FILE = "test_books.json"

class TestLibrarySystem(unittest.TestCase):
    def setUp(self):
        if os.path.exists(TEST_FILE):
            os.remove(TEST_FILE)
        self.system = LibrarySystem(data_file=TEST_FILE)

    def tearDown(self):
        if os.path.exists(TEST_FILE):
            os.remove(TEST_FILE)

    def test_add_get_delete(self):
        b = Book("111", "A", "B", 2000, 1)
        added = self.system.add_book(b)
        self.assertTrue(added)
        fetched = self.system.get_book("111")
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.title, "A")
        deleted = self.system.delete_book("111")
        self.assertTrue(deleted)
        self.assertIsNone(self.system.get_book("111"))

    def test_update(self):
        b = Book("222", "Old", "Auth", 1990, 1)
        self.system.add_book(b)
        updated = self.system.update_book("222", title="New", copies=5)
        self.assertTrue(updated)
        b2 = self.system.get_book("222")
        self.assertEqual(b2.title, "New")
        self.assertEqual(b2.copies, 5)

if __name__ == "__main__":
    unittest.main()
