# Dependencies
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def home_page():    
    return"""
    <html>
        <h1>My Solo Trip!</h1>
        <h3>Available Routes:</h3>
            <ul>
                <br>
                    <li>
                        Precipitation Records:
                        <br>
                        <a href="/api/v1.0/precipitation">/api/v1.0/precipitation</a>
                    </li>
                <br>
                    <li>
                        Station Records:
                        <br>
                        <a href="/api/v1.0/stations">/api/v1.0/stations</a>
                    </li>
                <br>
                    <li>
                        TOBS Records:
                        <br>
                        <a href="/api/v1.0/tobs">/api/v1.0/tobs</a>
                    </li>
                <br>
                    <li>
                        Start Date Records:
                        <br>
                        <a href="/api/v1.0/2017-07-08">/api/v1.0/2017-07-08</a>
                    </li>
                <br>
                    <li>
                        Start/End Date Records:
                        <br>
                        <a href="/api/v1.0/2017-07-08/2017-07-18">/api/v1.0/2017-07-08/2017-07-18</a>
                <br>
            </ul>
    </html>
    """


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Precipitation Records"""
    
    session = Session(engine)

    # Query precipitation records
    twelve_months = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # Calculate the date 1 year ago from the last data point in the database
    one_yr = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    rain = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date > one_yr).order_by(Measurement.date).all()
    
    session.close()

    # Convert results into a dictionary
    prcp_dict = dict(rain)

    return jsonify(prcp_dict)
  

@app.route("/api/v1.0/stations")
def stations():
    """Station Records"""

    session = Session(engine)
    
    # Query stations records
    stations = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    
    session.close()

    # Convert results into a list
    station_list = [list(i) for i in stations]

    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def tobs():
    """TOBS Records"""

    session = Session(engine)

    # Query stations records & pull the most active station
    stations = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()

    # Calculate the date 1 year ago from the last data point in the database
    one_yr = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query tobs records
    tobs = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date > one_yr).all()
    
    session.close()

    # Convert results into a list
    tobs_list = [list(t) for t in tobs]

    return jsonify(tobs_list)


@app.route("/api/v1.0/2017-07-08")
def start(start_date='2017-07-08'):
    """Start Date Records
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVG, and TMAX
    """

    session = Session(engine)

    # Query start date records
    start = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).group_by(Measurement.date).all()

    session.close()

    # Convert results into a list
    start_list = [list(s) for s in start]

    return jsonify(start)


@app.route("/api/v1.0/2017-07-08/2017-07-18")
def start_end(start_date='2017-07-08', end_date='2017-07-18'):
    """Start/End Date Records

    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVG, and TMAX
    """

    session = Session(engine)

    # Query start date records
    start_end = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).group_by(Measurement.date).all()

    session.close()

    # Convert results into a list
    start_end_list = [list(e) for e in start_end]

    return jsonify(start_end_list)


if __name__ == '__main__':
    app.run(debug=True)