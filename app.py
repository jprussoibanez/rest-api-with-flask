from flask import Flask, jsonify, request, render_template
from flask_restful import Resource, Api, reqparse
from flask_jwt import JWT, jwt_required
from security import authenticate, identity

app = Flask(__name__)
app.secret_key = "jp"
api = Api(app)

jwt = JWT(app, authenticate, identity)

stores = [
    {
        'name': 'My store',
        'items': [
            {
                'name': 'My item',
                'price': 15.99
            }
        ]
    }
]

class Home(Resource):
    def get(self):
        return render_template("index.html"), 200

class StoreList(Resource):
    @jwt_required()
    def get(self):
        return {'stores': stores}, 200
    
    def post(self):
        request_data = request.get_json()
        new_store = {
            'name': request_data['name'],
            'items': []
        }
        stores.append(new_store)
        return new_store, 201

class Store(Resource):
    def get_store_by_name(self, name):
        return next(filter(lambda store: store['name'] == name, stores), None)

    def get(self, name):
        store = self.get_store_by_name(name)
        if store is not None:
            return store, 200
        else:
            return { 'message': f'{name} not found'}, 404

class ItemList(Resource):
    def get_store_by_name(self, name):
        return next(filter(lambda store: store['name'] == name, stores), None)
    
    def get(self, name):
        store = self.get_store_by_name(name)
        if store is not None:
            return store['items'], 200
        else:
            return { 'message': f'{name} not found'}, 404

    def post(self, name):
        store = self.get_store_by_name(name)
        if store is not None:
            request_data = request.get_json()
            new_item = {
                'name': request_data['name'],
                'price': request_data['price']
            }
            store['items'].append(new_item)
            return new_item, 201
        else:
            return { 'message': f'{name} not found'}, 404

class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        'price',
        type = float,
        required = True,
        help = 'This field is required'
    )

    def get_store_by_name(self, store_name):
        return next(filter(lambda store: store['name'] == store_name, stores), None)
    
    def get_item_by_name(self, store_name, item_name):
        store = self.get_store_by_name(store_name)
        return next(filter(lambda item: item['name'] == item_name, store['items']), None)

    def get(self, store_name, item_name):
        item = self.get_item_by_name(store_name, item_name)
        if item is not None:
            return item, 200
        else:
            return { 'message': f'{item_name} not found'}, 404
    
    def delete(self, store_name, item_name):
        store = self.get_store_by_name(store_name)
        if store:
            store['items'] = list(filter(lambda item: item['name'] != item_name, store['items']))
            return { 'message': f'{item_name} deleted'}, 200
        else:
            return { 'message': f'{store_name} not found'}, 404

    def put(self, store_name, item_name):
        request_data = Item.parser.parse_args()
        item = self.get_item_by_name(store_name, item_name)
        
        if item:
            item.update(request_data)
            return item, 200
        else:
            return { 'message': f'{item_name} not found'}, 404
        
        

api.add_resource(Home, '/')
api.add_resource(StoreList, '/store')
api.add_resource(Store, '/store/<string:name>')
api.add_resource(ItemList, '/store/<string:name>/item')
api.add_resource(Item, '/store/<string:store_name>/item/<string:item_name>')

app.run(port=5000, debug=True)

