from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Destinations(db.Model):
    __tablename__ = "destinations"
    Destination_id = db.Column(db.String(70), primary_key=True, unique=True)
    Name = db.Column(db.String(70))
    Temperature = db.Column(db.String(70))

    def serialize(self):
        return{
            "Destination_id":self.Destination_id,
            "Name":self.Name,
            "Temperature":self.Temperature
        }

