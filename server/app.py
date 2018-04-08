from flask import Flask, request, jsonify, abort, json
from datetime import datetime, timedelta
from calendar import timegm
from .schema import validate_schema
from .schema.sensor_insert import insert_sensor_schema
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc


application = Flask(__name__)
application.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/test.db"
db = SQLAlchemy(application)


class SensorData(db.Model):
    __tablename__ = "sensordata"
    timestamp = db.Column(db.DateTime, primary_key=True)
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    pressure = db.Column(db.Float)
    luminosity = db.Column(db.Integer)

    def dict(self):
        return {
            "timestamp": timegm(self.timestamp.utctimetuple()) * 1000,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "pressure": self.pressure,
            "luminosity": self.luminosity
        }


db.create_all()
db.session.commit()

VALID_DURATIONS = {
    "day": timedelta(days=1),
    "week": timedelta(weeks=1),
    "month": timedelta(days=30),
    "year": timedelta(days=365),
}
VALID_SENSOR_TYPES = {
    "temperature": SensorData.temperature,
    "humidity": SensorData.humidity,
    "pressure": SensorData.pressure,
    "luminosity": SensorData.luminosity,
}


@application.route("/")
def index():
    return "Hello!"


# REST-ish Endpoints
# Sensor Data Insertion


@application.route("/api/insert", methods=["POST"])
@validate_schema(insert_sensor_schema)
def insert():
    data = json.loads(request.data)
    timestamp = datetime.utcnow()
    db_data = SensorData(
        timestamp=timestamp,
        temperature=data["temperature"],
        humidity=data["humidity"],
        pressure=data["pressure"],
        luminosity=data["luminosity"],
    )
    db.session.add(db_data)
    db.session.commit()
    return "", 201


# Sensor Data Retrieval

# Latest Values


@application.route("/api/latest", methods=["GET"])
def latest():
    latest = db.session.query(SensorData).order_by(desc("timestamp")).first()
    return jsonify(latest.dict())


# Specific Sensor Types


@application.route("/api/<string:sensor>/<string:duration>", methods=["GET"])
def sensorReadings(sensor, duration):
    if sensor not in VALID_SENSOR_TYPES or duration not in VALID_DURATIONS:
        abort(404)
    now = datetime.utcnow()
    values = db.session.query(getattr(SensorData, sensor)).filter(
        SensorData.timestamp >= now - VALID_DURATIONS[duration]
    ).all()
    return jsonify(values)


@application.route("/api/<string:sensor>/<string:duration>/<int:ts>", methods=["GET"])
def sensorReadingsSinceTimestamp(sensor, duration, ts):
    if sensor not in VALID_SENSOR_TYPES or duration not in VALID_DURATIONS:
        abort(404)
    dt = datetime.utcfromtimestamp(ts / 1000)
    values = db.session.query(getattr(SensorData, sensor)).filter(
        SensorData.timestamp > dt
    ).all()
    return jsonify(values)


if __name__ == "__main__":
    application.run(host="0.0.0.0")