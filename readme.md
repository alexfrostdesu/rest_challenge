# REST API challenge

This is a simple auction app, written in RESTful architectural style

## Installation

```bash
git clone https://github.com/alexfrostdesu/rest_challenge.git
cd rest_challenge
pip install -r requirements.txt
python bidding_api.py
```

## Testing

To test that the app is working correctly, run testing script

```bash
python test_bidding.py
```

## Usage

Two user roles are assumed - Bidder and Auctioneer

Both can use `POST` and `GET` methods on their respective entry points

Auctioneer uses `/auction` entry point and can initiate bidding with `POST` method and finish the auction with `GET` method

To start auction, send an item list formatted like: `{item: starting_bid}` with any number of items

To place bid, Bidder sends a bid `POST` request to `/bidding` with following data: `{user_id: user_id, item_id: item, bid: bid}`

Once first bid is placed, user can access his bid through `/bidding/<string:user_id>` with `GET` method

To finish auction, Auctioneer sends a `GET` request, and from that point, results are available to anyone

Bidders can access auction results through `/bidding` with a `GET` request


## License
[WTFPL](http://www.wtfpl.net/txt/copying/)