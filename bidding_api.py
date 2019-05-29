from flask import Flask, request, Response, json
from flask_restful import Resource, Api
from http import HTTPStatus


app = Flask(__name__)
api = Api(app)

response_messages = {'not_ready': "Results not ready",
                     'bid_low': "Bid is too low",
                     'item_not_found': "Item not found",
                     'user_not_found': "User not found"}


def create_response(data, status):
    """
    Simple function to create responses
    """
    return Response(response=json.dumps(data), status=status, mimetype='application/json')


class DataStore:
    """
    Data storage mock-up with _save and _get functions
    Simulates database with 2D tables 'users', 'items' and 'results'
    """
    def __init__(self):
        self.data_store = {'users': {}, 'items': {}, 'results': {}}

    def _save(self, table, some_id, value):
        """
        Saving a new row in a table
        some_id - id (index) of a new entry
        value - columns values for that entry
        """
        if some_id in self.data_store[table]:
            self.data_store[table][some_id].update(value)
        else:
            self.data_store[table][some_id] = value

    def save_users(self, user_id, value):
        self._save('users', user_id, value)

    def save_items(self, item_id, value):
        self._save('items', item_id, value)

    def save_results(self, result_id, value):
        self._save('results', result_id, value)

    def _get(self, table, row=None, column=None):
        """
        Getting a specified table, row or cell
        """
        if column:
            return self.data_store[table][row][column]
        elif row:
            return self.data_store[table][row]
        else:
            return self.data_store[table]

    def get_users(self, row=None, column=None):
        return self._get('users', row, column)

    def get_items(self, row=None, column=None):
        return self._get('items', row, column)

    def get_results(self, row=None, column=None):
        return self._get('results', row, column)

    def truncate_ds(self):
        """
        Simulates truncation of all tables
        """
        self.data_store = {'users': {}, 'items': {}, 'results': {}}


class Auction(Resource):
    """
    Class for Auctioneer role to create item bidding list and initiate bid award process
    """
    def get(self):
        """
        Initiates bid award process
        Returns the result
        """
        # getting all items
        items = bidding_ds.get_items()
        for item in items:
            user, bid = items[item]['lowest_bid']
            # checking for the lowest bid
            if bid is not None:
                bidding_ds.save_results(result_id=item, value=(user, bid))
        # creating a response
        response_data = bidding_ds.get_results()
        status = HTTPStatus.OK
        return create_response(response_data, status)

    def post(self):
        """
        Creates item bidding list
        """
        # assuming that we need to delete previous auction
        bidding_ds.truncate_ds()
        # getting new item bidding list
        item_list = request.form.to_dict()
        # adding each item
        for item in item_list:
            bidding_ds.save_items(item_id=item, value={'starting_bid': float(item_list[item]),
                                                       'lowest_bid': (None, None)})
        # creating a response
        response_data = bidding_ds.get_items()
        status = HTTPStatus.ACCEPTED
        return create_response(response_data, status)


class Bidding(Resource):
    """
    Class for bidder role to bid on items, view their current bids and auction results
    """
    def get(self, user_id=None):
        """
        Bidders can view their current bids and auction results
        if user_id is used then current bids for user are returned
        else auction results are returned, if available
        """
        # getting user bids and results, if available
        users_bids = bidding_ds.get_users()
        results = bidding_ds.get_results()
        # creating a response
        if user_id in users_bids:
            response_data = users_bids[user_id]
            status = HTTPStatus.OK
        elif not user_id and results:
            response_data = results
            status = HTTPStatus.OK
        elif not user_id and not results:
            response_data = response_messages['not_ready']
            status = HTTPStatus.NOT_FOUND
        else:
            response_data = response_messages['user_not_found']
            status = HTTPStatus.NOT_FOUND
        return create_response(response_data, status)

    def post(self, user_id=None):
        """
        Bid on item
        """
        user = request.form.get('user_id')
        item = request.form.get('item_id')
        # getting all items
        items = bidding_ds.get_items()
        # checking item existence in bidding list
        if item in items:
            bid = float(request.form.get('bid'))
            starting_bid = items[item]['starting_bid']
            _, lowest_bid = items[item]['lowest_bid']
            # checking bid for eligibility
            if bid >= starting_bid:
                bidding_ds.save_users(user_id=user, value={item: bid})
                # checking bid for lowest
                if not lowest_bid or bid < lowest_bid:
                    bidding_ds.save_items(item_id=item, value={'lowest_bid': (user, bid)})
                # creating a response
                response_data = {user: {item: bid}}
                status = HTTPStatus.ACCEPTED
            else:
                response_data = response_messages['bid_low']
                status = HTTPStatus.NOT_ACCEPTABLE
        else:
            response_data = response_messages['item_not_found']
            status = HTTPStatus.NOT_FOUND
        return create_response(response_data, status)


# mapping classes to roles' URLs
api.add_resource(Bidding, '/bidding/<string:user_id>', '/bidding/')
api.add_resource(Auction, '/auction/')

if __name__ == '__main__':
    # creating a mock-up data storage
    bidding_ds = DataStore()
    app.run(port=5000)
