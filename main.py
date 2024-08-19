from flask import Flask, jsonify, request, session
from model import db, Destinations
from config import Config
from uuid import uuid4
import cryptography


app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()

def add_destination_to_db(new_name, new_temperature):
    new_id = uuid4().hex
    new_destination = Destinations(Id=new_id, Name=new_name, Temperature=new_temperature)

    db.session.add(new_destination)
    db.session.commit()
    return new_destination

@app.route('/destinations', methods = ['POST'])
def create_destination():
    try:
     name = request.json.get('name')
     existing_destination = Destinations.query.filter_by(Name=name).first()
     if name is None:
         return jsonify({'error':"Destination Name cannot be null"}), 422
     if existing_destination is not None:
         return jsonify({'error':"Destination Name already exists"}), 409

     temperature = request.json.get('temperature')

     new_destination = add_destination_to_db(new_name=name, new_temperature=temperature)
     return jsonify(new_destination.serialize()), 201
    except Exception as e:
        return jsonify({'error':str(e)}), 500

@app.route('/destinations/<destination_name>', methods=['DELETE'])
def delete_destination(destination_name):
    try:
        destination_delete = Destinations.query.filter_by(Name=destination_name).first()
        if destination_delete is None:
            return jsonify({'error':'Destination not found' }), 404

        db.session.delete(destination_delete)
        db.session.commit()
        return jsonify ({'message':'Destination deleted Succesfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/destinations', methods=['PATCH'])
def update_ideal_temp():
    try:
        destination_name = request.json.get('destination_name')

        if destination_name is None:
            return jsonify({'error' : 'Destination name is required'}), 422

        destination_update = Destinations.query.filter_by(Name=destination_name).first()
        if destination_update is None:
            return jsonify ({'error':'Destination not found'}), 404

        new_temperature = request.json.get('new_temperature')
        if new_temperature is None:
            return jsonify({'error': 'New temperature is required'}), 422

        destination_update.Temperature = new_temperature
        db.session.commit()

        return jsonify({'message': 'Destination temperature updated successfully',
                        'updated_destination': destination_update.serialize()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_destination', methods = ['GET'])
def get_destination():
    try:
        args = request.args
        destination_name = args.get('destination')
        destination_to_find = Destinations.query.filter_by(Name=destination_name).first()
        if destination_to_find is None:
            return jsonify({'error': 'Destination not found'}), 404

        return jsonify(destination_to_find.serialize()), 200
    except Exception as e:
        return jsonify({'error': 'Please try again'}), 500

if __name__ == '__main__' :
    app.run(debug=True, port=8080)