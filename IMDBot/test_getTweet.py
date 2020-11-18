import unittest
import bot

class Testbot(unittest.TestCase):
    
    def test_getATweet(self):
        tweet = bot.getSingleStatus(1328477170788945924)
        self.assertEqual(tweet, '@botimd #genre5 action')

if __name__ == '__main__':
    unittest.main()