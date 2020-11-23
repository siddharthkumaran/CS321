import unittest
import bot

class Testbot(unittest.TestCase):

    def test_getRated(self):
        movie_id = bot.popular()
        self.assertEqual(movie_id, 340102) #update this movie id by going to https://developers.themoviedb.org/3/trending/get-trending 

if __name__ == '__main__':
    unittest.main()
