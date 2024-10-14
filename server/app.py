#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")



app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False



db.init_app(app)
migrate = Migrate(app, db)

api = Api(app)

@app.route("/")
def index():
    return "<h1>Code challenge-Pizza</h1>"

@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([restaurant.to_dict(rules=['-restaurant_pizzas']) for restaurant in restaurants]), 200

@app.route('/restaurants/<int:id>', methods=['GET', 'DELETE'])
def get_restaurant_by_id(id):
    restaurant = Restaurant.query.filter(Restaurant.id == id).first()
    if not restaurant:
        return {'error': 'Restaurant not found'}, 404

    if request.method == 'GET':
        return jsonify(restaurant.to_dict(rules=['restaurant_pizzas', 'restaurant_pizzas.pizza'])), 200

    elif request.method == 'DELETE':
        db.session.delete(restaurant)
        db.session.commit()
        return {}, 204

@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([pizza.to_dict(rules=['-restaurant_pizzas']) for pizza in pizzas]), 200

@app.route('/restaurant_pizzas', methods=['POST'])
def create_new_pizza():
    json_data = request.get_json()
    try:
        new_restaurant_pizza = RestaurantPizza(
            price=json_data.get('price'),
            pizza_id=json_data.get('pizza_id'),
            restaurant_id=json_data.get('restaurant_id')
        )
        db.session.add(new_restaurant_pizza)
        db.session.commit()
        return jsonify(new_restaurant_pizza.to_dict()), 201
    except ValueError as e:
        # Return the error message in the expected format
        return jsonify({'errors': ['validation errors']}), 400

if __name__ == "__main__":
    app.run(port=5555, debug=True)