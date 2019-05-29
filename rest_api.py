from flask import Flask, request, Response, json
from flask_restful import Resource, Api


app = Flask(__name__)
api = Api(app)


def create_response(data, status):
    """
    Simple function to create responses
    """
    return Response(response=data, status=status, mimetype='application/json')


class DataStore:
    """
    Data storage mock-up with save and get functions
    Simulates database with 2D tables 'users', 'items' and 'results'
    """
    def __init__(self):
        self.data_store = {'users': {'nice': {'kek': 10}}, 'items': {}, 'results': {}}

    def save(self, table, row, value):
        """
        Saving a new row in a table
        row - row index
        value - columns values for that row
        """
        if row in self.data_store[table]:
            self.data_store[table][row].update(value)
        else:
            self.data_store[table][row] = value

    def get(self, table, row=None, column=None):
        """
        Getting a specified table, row or cell
        """
        if column:
            return self.data_store[table][row][column]
        elif row:
            return self.data_store[table][row]
        else:
            return self.data_store[table]


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
        items = bidding_ds.get(table='items')
        for item in items:
            user, bid = items[item]['lowest_bid']
            # checking for the lowest bid
            if bid is not None:
                result_entry = dict(table='results', row=item, value=(user, bid))
                bidding_ds.save(**result_entry)
        # creating a response
        response_data = json.dumps(bidding_ds.get(table='results'))
        status = 200
        return create_response(response_data, status)

    def post(self):
        """
        Creates item bidding list
        """
        # getting new item bidding list
        item_list = request.form.to_dict()
        # adding each item
        for item in item_list:
            item_entry = dict(table='items', row=item, value={'starting_bid': float(item_list[item]), 'lowest_bid': (None, None)})
            bidding_ds.save(**item_entry)
        # creating a response
        response_data = json.dumps(bidding_ds.get(table='items'))
        status = 201
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
        users_bids = bidding_ds.get(table='users')
        results = bidding_ds.get(table='results')
        # creating a response
        if user_id in users_bids:
            response_data = json.dumps(users_bids[user_id])
            status = 200
        elif not user_id and results:
            response_data = json.dumps(results)
            status = 200
        elif not user_id and not results:
            response_data = json.dumps("Results not ready")
            status = 404
        else:
            response_data = json.dumps("User not found")
            status = 404
        return create_response(response_data, status)

    def post(self, user_id=None):
        """
        Bid on item
        """
        user = request.form.get('user_id')
        item = request.form.get('item_id')
        # getting all items
        items = bidding_ds.get(table='items')
        # checking item existence in bidding list
        if item in items:
            bid = float(request.form.get('bid'))
            starting_bid = items[item]['starting_bid']
            _, lowest_bid = items[item]['lowest_bid']
            # checking bid for eligibility
            if bid >= starting_bid:
                user_entry = dict(table='users', row=user, value={item: bid})
                bidding_ds.save(**user_entry)
                # checking bid for lowest
                if not lowest_bid or bid < lowest_bid:
                    bidding_ds.save(table='items', row=item, value={'lowest_bid': (user, bid)})
                # creating a response
                response_data = json.dumps({user: {item: bid}})
                status = 201
            else:
                response_data = json.dumps("Bid is too low")
                status = 406
        else:
            response_data = json.dumps("Item not found")
            status = 404
        return create_response(response_data, status)


# mapping classes to roles' URLs
api.add_resource(Bidding, '/bidding/<string:user_id>', '/bidding/')
api.add_resource(Auction, '/auction/')

if __name__ == '__main__':
    # creating a mock-up data storage
    bidding_ds = DataStore()
    app.run()
