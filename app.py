import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func, select
from sqlalchemy import MetaData
from flask import Flask, jsonify
from sqlalchemy import desc

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///belly_button_biodiversity.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

OTU = Base.classes.otu
Samples = Base.classes.samples
Samples_metaData = Base.classes.samples_metadata
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
def index():
    return render_template('index.html')

@app.route("/")
def dashboard():
    """Return the dashboard homepage."""
    return (
        f"Available Routes:<br/>"
        f"/names<br/>"
        f"/otu<br/>"
        f"/metadata/<sample><br/>"
        f"/wfreq/<sample><br/>"
        f"/samples/<sample><br/>"
    )


@app.route("/names")
def names():
    sample_names = Samples.__table__.columns
    sample_names_ls = [name.key for name in sample_names]
    sample_names_ls.remove("otu_id")
    return jsonify(sample_names_ls)


@app.route("/otu")
def otu():
    results = session.query(OTU.lowest_taxonomic_unit_found).all()
    # Convert list of tuples into normal list
    otu_names = list(np.ravel(results))

    return jsonify(otu_names)


@app.route("/metadata/<sample>")
def sample_query(sample):
    sample_name = sample.replace("BB_", "")
    result = session.query(Samples_metaData.AGE, Samples_metaData.BBTYPE, Samples_metaData.ETHNICITY,
                           Samples_metaData.GENDER, Samples_metaData.LOCATION, Samples_metaData.SAMPLEID).filter_by(
        SAMPLEID=sample_name).all()

    record = result[0]
    record_dict = {
        "AGE": record[0],
        "BBTYPE": record[1],
        "ETHNICITY": record[2],
        "GENDER": record[3],
        "LOCATION": record[4],
        "SAMPLEID": record[5]
    }
    return jsonify(record_dict)


@app.route("/wfreq/<sample>")
def wfreq(sample):
    sample_name = sample.replace("BB_", "")
    result = session.query(Samples_metaData.WFREQ).all()

    record = result[0]
    record_dict = {
        "WFREQ": record[0]
    }

    return jsonify(record_dict)


@app.route('/samples/<sample>')
def get_sample_value(sample):
    otu_ids = []
    sample_values = []
    samples_result = {}

    my_query = "Samples." + sample

    query_result = session.query(Samples.otu_id, my_query).order_by(desc(my_query))

    for result in query_result:
        otu_ids.append(result[0])
        sample_values.append(result[1])

        # Add the above lists to the dictionary
        samples_result = {
            "otu_ids": otu_ids,
            "sample_values": sample_values
        }
        return jsonify(samples_result)




from flask import Flask, jsonify, render_template




@app.route("/data")
def dashboard():

    sel = [otu_ids, get_sample_value]
    results = session.query(*sel)
    labels, values = zip(*otu_ids.sample_values())
    data = [{
        "labels": otu_ids,
        "values": sample_values,
        "type": "pie"}]

    return jsonify(data)

@app.route("/")
def home():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True)