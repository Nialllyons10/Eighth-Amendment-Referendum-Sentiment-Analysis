import unittest
import twitter_streaming

class TestTwitterStreaming(unittest.TestCase):
    def test_add_tweet_location(self):
        self.assertEqual(("null"), twitter_streaming.add_tweet_location(None)) #should return null if the location is a None type
        self.assertEqual(("dublin"), twitter_streaming.add_tweet_location("Dublin, Ireland")) #should return the county in lowercase if supplied in a tuple format
        self.assertEqual(("other"), twitter_streaming.add_tweet_location("Paris, France")) #should return other if a country that's not Ireland
        self.assertEqual(("other"), twitter_streaming.add_tweet_location("Judge Judys Court Room")) #Should return other if it's a non valid location
        self.assertEqual(("wexford"), twitter_streaming.add_tweet_location("Wexford")) #should return the county in lowercase
        self.assertEqual(("other"), twitter_streaming.add_tweet_location("123")) #should reutn other if non valid place is entered
        self.assertEqual(("dublin"), twitter_streaming.add_tweet_location("my gaff, Dublin")) #should ignore the first bit and return dublin

if __name__ == "__main__":
    unittest.main()  # run all tests