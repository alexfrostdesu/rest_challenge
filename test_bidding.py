import requests
import unittest
from http import HTTPStatus

LOCAL_URL = "http://127.0.0.1:5000/"
item_list = {'car': 100, 'house': 500, 'yacht': 800, 'airplane': 1000}


def get_request(url):
    return requests.get(url)


def post_request(url, data):
    return requests.post(url, data)


class TestGetPostMethods(unittest.TestCase):
    def test_items_import(self):
        # starting auction
        start_auction = post_request(LOCAL_URL + 'auction', item_list)
        self.assertEqual(start_auction.status_code, HTTPStatus.ACCEPTED)
        fail_start_auction = post_request(LOCAL_URL + 'auction', {})
        self.assertEqual(fail_start_auction.status_code, HTTPStatus.BAD_REQUEST)

    def test_user_bids(self):
        # placing correct bid
        right_bid = post_request(LOCAL_URL + 'bidding', {'user_id': 'Adam', 'item_id': 'car', 'bid': 120})
        # placing bid on non-existent item
        wrong_item = post_request(LOCAL_URL + 'bidding', {'user_id': 'Mark', 'item_id': 'helicopter', 'bid': 700})
        # placing too low bid
        wrong_bid = post_request(LOCAL_URL + 'bidding', {'user_id': 'Lena', 'item_id': 'house', 'bid': 400})
        self.assertEqual(right_bid.status_code, HTTPStatus.ACCEPTED)
        self.assertEqual(wrong_item.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(wrong_bid.status_code, HTTPStatus.BAD_REQUEST)

    def test_user_gets(self):
        # placing multiple bids with one user
        post_request(LOCAL_URL + 'bidding', {'user_id': 'Adam', 'item_id': 'car', 'bid': 110})
        post_request(LOCAL_URL + 'bidding', {'user_id': 'Adam', 'item_id': 'house', 'bid': 900})
        post_request(LOCAL_URL + 'bidding', {'user_id': 'Adam', 'item_id': 'yacht', 'bid': 1000})
        user_bids = get_request(LOCAL_URL + 'bidding/Adam')
        self.assertEqual(user_bids.status_code, HTTPStatus.OK)
        self.assertEqual(len(user_bids.json()), 3)

    def test_results(self):
        # starting auction
        post_request(LOCAL_URL + 'auction', item_list)
        # placing multiple bids with multiple users
        post_request(LOCAL_URL + 'bidding', {'user_id': 'Adam', 'item_id': 'car', 'bid': 110})  # lowest car bid
        post_request(LOCAL_URL + 'bidding', {'user_id': 'Adam', 'item_id': 'house', 'bid': 900})
        post_request(LOCAL_URL + 'bidding', {'user_id': 'Adam', 'item_id': 'yacht', 'bid': 1000})
        post_request(LOCAL_URL + 'bidding', {'user_id': 'Adam', 'item_id': 'airplane', 'bid': 700})  # incorrect ap bid
        post_request(LOCAL_URL + 'bidding', {'user_id': 'Mark', 'item_id': 'car', 'bid': 120})
        post_request(LOCAL_URL + 'bidding', {'user_id': 'Mark', 'item_id': 'house', 'bid': 800})  # lowest house bid
        post_request(LOCAL_URL + 'bidding', {'user_id': 'Mark', 'item_id': 'airplane', 'bid': 1000})  # lowest ap bid
        post_request(LOCAL_URL + 'bidding', {'user_id': 'Lena', 'item_id': 'car', 'bid': 90})  # incorrect car bid
        post_request(LOCAL_URL + 'bidding', {'user_id': 'Lena', 'item_id': 'car', 'bid': 130})
        post_request(LOCAL_URL + 'bidding', {'user_id': 'Lena', 'item_id': 'yacht', 'bid': 900})  # lowest yacht bid
        post_request(LOCAL_URL + 'bidding', {'user_id': 'Lena', 'item_id': 'airplane', 'bid': 1200})
        # getting results
        auction_results = get_request(LOCAL_URL + 'auction').json()
        self.assertEqual(auction_results['car']['lowest_bid'], 110.0)
        self.assertEqual(auction_results['car']['lowest_bidder'], 'Adam')
        self.assertEqual(auction_results['house']['lowest_bid'], 800.0)
        self.assertEqual(auction_results['house']['lowest_bidder'], 'Mark')
        self.assertEqual(auction_results['yacht']['lowest_bid'], 900.0)
        self.assertEqual(auction_results['yacht']['lowest_bidder'], 'Lena')
        self.assertEqual(auction_results['airplane']['lowest_bid'], 1000.0)
        self.assertEqual(auction_results['airplane']['lowest_bidder'], 'Mark')
        auction_bidder_results = get_request(LOCAL_URL + 'bidding')
        self.assertEqual(auction_bidder_results.status_code, HTTPStatus.OK)


if __name__ == '__main__':
    unittest.main()
