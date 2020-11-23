import unittest
import bot

class Testbot(unittest.TestCase):
    
    def test_getAGenreId(self):
        genre_Id = bot.getGenreId('horror')
        self.assertEqual(genre_Id, 27)

    def test_getGenreList(self):
        txt = bot.getGenreList()
        self.assertEqual(txt, 'Action, Adventure, Animation, Comedy, Crime, Documentary, Drama, Family, Fantasy, History, Horror, Music, Mystery, Romance, Science Fiction, TV Movie, Thriller, War, Western')

if __name__ == '__main__':
    unittest.main()