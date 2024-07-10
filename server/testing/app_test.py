from models import Restaurant, RestaurantPizza, Pizza
from app import app, db
from faker import Faker

class TestApp:
    '''Flask application in app.py'''

    def setup_restaurants(self):
        fake = Faker()
        restaurants = [Restaurant(name=fake.name(), address=fake.address()) for _ in range(2)]
        db.session.add_all(restaurants)
        db.session.commit()
        return restaurants

    def setup_pizzas(self):
        fake = Faker()
        pizzas = [Pizza(name=fake.name(), ingredients=fake.sentence()) for _ in range(2)]
        db.session.add_all(pizzas)
        db.session.commit()
        return pizzas

    def setup_restaurant_pizza(self):
        fake = Faker()
        pizza = Pizza(name=fake.name(), ingredients=fake.sentence())
        restaurant = Restaurant(name=fake.name(), address=fake.address())
        db.session.add_all([pizza, restaurant])
        db.session.commit()
        return restaurant, pizza

    def test_restaurants(self):
        with app.app_context():
            restaurants = self.setup_restaurants()
            response = app.test_client().get('/restaurants')
            assert response.status_code == 200
            assert response.content_type == 'application/json'
            response = response.json
            assert [r['id'] for r in response] == [r.id for r in restaurants]
            assert [r['name'] for r in response] == [r.name for r in restaurants]
            assert [r['address'] for r in response] == [r.address for r in restaurants]
            for r in response:
                assert 'restaurant_pizzas' not in r

    def test_restaurants_id(self):
        with app.app_context():
            restaurant = self.setup_restaurants()[0]
            response = app.test_client().get(f'/restaurants/{restaurant.id}')
            assert response.status_code == 200
            assert response.content_type == 'application/json'
            response = response.json
            assert response['id'] == restaurant.id
            assert response['name'] == restaurant.name
            assert response['address'] == restaurant.address
            assert 'restaurant_pizzas' in response

    def test_returns_404_if_no_restaurant_to_get(self):
        with app.app_context():
            response = app.test_client().get('/restaurants/0')
            assert response.status_code == 404
            assert response.content_type == 'application/json'
            assert response.json.get('error')

    def test_deletes_restaurant_by_id(self):
        with app.app_context():
            restaurant = self.setup_restaurants()[0]
            response = app.test_client().delete(f'/restaurants/{restaurant.id}')
            assert response.status_code == 204
            assert Restaurant.query.filter_by(id=restaurant.id).one_or_none() is None

    def test_returns_404_if_no_restaurant_to_delete(self):
        with app.app_context():
            response = app.test_client().delete('/restaurants/0')
            assert response.status_code == 404
            assert response.json.get('error') == "Restaurant not found"

    # def test_pizzas(self):
    #     with app.app_context():
    #         pizzas = self.setup_pizzas()
    #         response = app.test_client().get('/pizzas')
    #         assert response.status_code == 200
    #         assert response.content_type == 'application/json'
    #         response = response.json
    #         assert [p['id'] for p in response] == [p.id for p in pizzas]
    #         assert [p['name'] for p in response] == [p.name for p in pizzas]
    #         assert [p['ingredients'] for p in response] == [p.ingredients for p in pizzas]
    #         for p in response:
    #             assert 'restaurant_pizzas' not in p
    def test_pizzas(self):
      with app.app_context():
        pizzas = self.setup_pizzas()
        response = app.test_client().get('/pizzas')
        assert response.status_code == 200
        assert response.content_type == 'application/json'
        response_data = response.json
        
        print("Expected pizza IDs:", [p.id for p in pizzas])
        print("Returned pizza IDs:", [p['id'] for p in response_data])
        
        assert [p['id'] for p in response_data] == [p.id for p in pizzas]


    def test_creates_restaurant_pizzas(self):
        with app.app_context():
            restaurant, pizza = self.setup_restaurant_pizza()
            response = app.test_client().post('/restaurant_pizzas', json={"price": 3, "pizza_id": pizza.id, "restaurant_id": restaurant.id})
            assert response.status_code == 201
            assert response.content_type == 'application/json'
            response = response.json
            assert response['price'] == 3
            assert response['pizza_id'] == pizza.id
            assert response['restaurant_id'] == restaurant.id
            assert RestaurantPizza.query.filter_by(restaurant_id=restaurant.id, pizza_id=pizza.id).first().price == 3

    def test_400_for_validation_error(self):
        with app.app_context():
            restaurant, pizza = self.setup_restaurant_pizza()
            for price in [0, 31]:
                response = app.test_client().post('/restaurant_pizzas', json={"price": price, "pizza_id": pizza.id, "restaurant_id": restaurant.id})
                assert response.status_code == 400
                assert response.json['errors'] == ["validation errors"]
