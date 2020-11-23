import unittest
import bot

class Testbot(unittest.TestCase):

    def test_getRated(self):
        list = bot.rated()
        self.assertEqual(len(list), 10)

if __name__ == '__main__':
    unittest.main()
