#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate

from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return '<h1>Bakery GET-POST-PATCH-DELETE API</h1>'


@app.route('/bakeries')
def bakeries():
    bakeries = [bakery.to_dict() for bakery in Bakery.query.all()]
    return make_response(bakeries,   200)


@app.route('/bakeries/<int:id>' , methods=["GET","PATCH","DELETE"])
def bakery_by_id(id):
     
    if request.method =="GET":
        
        bakery = Bakery.query.filter_by(id=id).first()
        bakery_serialized = bakery.to_dict()
        return make_response(bakery_serialized, 200)
    
    
    elif request.method == "PATCH":
        try:
            bakery = Bakery.query.get(id)
            if bakery is None:
                return make_response(jsonify({"error": "Bakery not found"}), 404)

            data = request.get_json()  # Get JSON data from the request body
            name = data.get("name")
            if name:
                bakery.name = name


            db.session.commit()
            return make_response(jsonify(bakery.to_dict()), 200)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({"error": str(e)}), 500)
        
    elif request.method == "DELETE":
        try:
            bakery = Bakery.query.get(id)
            if bakery is None:
                return make_response(jsonify({"error": "Bakery not found"}), 404)

            db.session.delete(bakery)
            db.session.commit()
            return make_response(jsonify({"message": "Bakery deleted successfully"}), 200)
        except Exception as e:
            db.session.rollback()
            print(f"Error in DELETE: {e}")  # Debug statement
            return make_response(jsonify({"error": str(e)}), 500)

        



@app.route('/baked_goods/by_price')
def baked_goods_by_price():
    baked_goods_by_price = BakedGood.query.order_by(
        BakedGood.price.desc()).all()
    baked_goods_by_price_serialized = [
        bg.to_dict() for bg in baked_goods_by_price
    ]
    return make_response(baked_goods_by_price_serialized, 200)


@app.route('/baked_goods/most_expensive')
def most_expensive_baked_good():
    most_expensive = BakedGood.query.order_by(
        BakedGood.price.desc()).limit(1).first()
    most_expensive_serialized = most_expensive.to_dict()
    return make_response(most_expensive_serialized,   200)


@app.route("/baked_goods", methods=["GET", "POST"])
def baked_goods():
    if request.method == "GET":

        baked_goods =  [baked_good.to_dict for baked_good in BakedGood.query.all()]
        
        return make_response(baked_goods, 200)

    elif request.method == "POST":
        new_baked_good=BakedGood(
           name=request.form.get("name") ,
           price=int(request.form.get("price")) ,
           bakery_id=int(request.form.get("bakery_id") )
        )
        
        db.session.add(new_baked_good)
        db.session.commit()
        return make_response(new_baked_good.to_dict(),201)
        


if __name__ == '__main__':
    app.run(port=5555, debug=True)
