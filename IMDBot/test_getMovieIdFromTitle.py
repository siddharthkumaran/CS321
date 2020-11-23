import unittest
import bot

class Testbot(unittest.TestCase):

    def test_getMovieIdFromTitle(self):
        title="Men in Black"
        id=getMovieIdFromTitle(title)
        self.assertFalse(id==-1)

if __name__ == '__main__':
    unittest.main()