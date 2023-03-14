import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start        *introduce the start date after the /v1.0/ on this format YYYY-MM-DD*<br/>"
        f"/api/v1.0/start/end    *introduce the start and end date after the /v1.0/ on this format YYYY-MM-DD*"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of precipitation"""
    # Query precipitation
    last_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_year=dt.datetime.strptime(last_date,'%Y-%m-%d').date()-dt.timedelta(days=365)

    results = session.query(Measurement.date,Measurement.prcp).filter(Measurement.date>=last_year).order_by(Measurement.date).all()

    session.close()

    # Convert list of tuples into a dictionary
    all_precepitation=[{"date":date,"prcp":prcp} for date, prcp in results]

    return jsonify(all_precepitation)


@app.route("/api/v1.0/stations")
def station():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of Stations"""
    # Query stations
    results = session.query(Station.station,Station.name,Station.latitude,Station.longitude, Station.elevation).all()

    session.close()

    # Convert list of tuples into a normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of most active station"""

    # Query active station
    most_active_station = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count().desc()).first()[0]


    # Calculate last 12 months
    last_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_year=dt.datetime.strptime(last_date,'%Y-%m-%d').date()-dt.timedelta(days=365)

    results=session.query(Measurement.station,Measurement.date,Measurement.tobs).filter(Measurement.station==most_active_station).filter(Measurement.date>=last_year).order_by(Measurement.date).all()

    session.close()

    # Convert list of tuples into a normal list
    all_tobs=[{"station":station, "date":date,"tobs":tobs} for station, date, tobs in results]

    return jsonify(all_tobs)


@app.route("/api/v1.0/<start>")
def datestart(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return stats"""

    #Query and stats calculate
    date_query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).all()
    
    session.close()
    
    # Convert list of tuples into a normal list
    all_stats=[{"min":min, "avg":avg,"max":max} for min, avg, max in date_query]
    
    return jsonify(all_stats)


@app.route("/api/v1.0/<start>/<end>")
def date_started_end(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return stats"""

    #Query and stats calculate
    date_query2 = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    session.close()
    
    # Convert list of tuples into a normal list
    all_stats2=[{"min":min, "avg":avg,"max":max} for min, avg, max in date_query2]
    
    return jsonify(all_stats2)


if __name__ == '__main__':
    app.run(debug=True)