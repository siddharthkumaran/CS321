import unittest
import bot

class Testbot(unittest.TestCase):

    def test_getYoutubeTrailer(self):
        movie=tmdb.Movies(607)
        url=getYoutubeTrailer(movie)
        self.assertFalse(url=='')

if __name__ == '__main__':
    unittest.main()