import unittest

import create_statistics

class TestCreateStatistics(unittest.TestCase):

    def test_total_overall_sentiment(self):
        self.assertEqual((0.00, 0.00), create_statistics.total_overall_sentiment(1, 0, 0)) # check if there are 0 negative and 0 positive tweets
        self.assertEqual((0.00, 100.00), create_statistics.total_overall_sentiment(1, 1, 0)) # check if there is one positive tweet and no negative tweets
        self.assertEqual((100.00, 0.00), create_statistics.total_overall_sentiment(1, 0, 1)) # check if there is one negative tweet and no positive tweets
        self.assertEqual((82.00, 18.00), create_statistics.total_overall_sentiment(55555, 10000, 45555)) #check if it works with high numbers that create numbers with more than two decimal places and the decimal points are 0

    def test_calculate_location_stats(self):
        self.assertEqual((0.00), create_statistics.calculate_location_stats({"ireland": 0, "other": 0, "null": 0}, "null", 1)) #checks that the dictionary is empty and the total is one
        self.assertEqual((50.00), create_statistics.calculate_location_stats({"ireland": 5, "other": 4, "null": 1}, "ireland", 10)) #checks that the statistics works with ideal data


if __name__ == "__main__":
    unittest.main()  # run all tests
