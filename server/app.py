from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, jsonify, make_response
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route("/")
def index():
    
    return "<h1>Code challenge</h1>"


@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return [restaurant.to_dict(rules=['-restaurant_pizzas']) for restaurant in restaurants], 200


@app.route("/restaurants/<int:id>", methods=['GET', 'DELETE'])
def get_restaurant(id):
    
    restaurant_by_id = Restaurant.query.filter(Restaurant.id == id).first()
    if not restaurant_by_id:
        return {"error": "Restaurant not found"}, 404
    
    if request.method == 'GET':
        return restaurant_by_id.to_dict(), 200
    elif request.method == 'DELETE':
        db.session.delete(restaurant_by_id)
        db.session.commit()
        return {}, 204


@app.route("/pizzas", methods=["GET"])
def get_pizzas():
   

    return [pizza.to_dict(rules=['-restaurant_pizzas']) for pizza in Pizza.query.all()], 200


@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    
    data = request.get_json()

    try:
        new_pizza = RestaurantPizza(
            price=data.get("price"),
            pizza_id=data.get("pizza_id"),
            restaurant_id=data.get("restaurant_id"),
        )
    except ValueError as e:
        return {"errors": ["validation errors"]}, 400 
    
    db.session.add(new_pizza)
    db.session.commit()

    return new_pizza.to_dict(), 201


if __name__ == "__main__":
    app.run(port=5555, debug=True)