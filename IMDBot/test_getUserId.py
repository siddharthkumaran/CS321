import unittest
import bot

class Testbot(unittest.TestCase):
    
    def test_getUserId(self):
        userId = bot.getSingleUserId(1328477170788945924)
        self.assertEqual(userId, 3371135375)

if __name__ == '__main__':
    unittest.main()