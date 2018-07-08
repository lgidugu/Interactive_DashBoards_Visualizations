import datetime as dt
import numpy as np
import pandas as pd
import os

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func, select
from sqlalchemy import MetaData
from flask import Flask, jsonify
from sqlalchemy import desc
from flask import Flask, jsonify, render_template


#################################################
# Database Setup
#################################################
dbfile = os.path.join('db', 'belly_button_biodiversity.sqlite')
engine = create_engine(f"sqlite:///{dbfile}")

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()

OTU = Base.classes.otu
Samples = Base.classes.samples
Samples_MetaData = Base.classes.samples_metadata
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
def home():
    """Render Home Page."""
    return render_template("index.html")

@app.route("/names")
def names():
    sample_names = session.query(Samples).statement
    df = pd.read_sql_query(sample_names, session.bind)
    df.set_index('otu_id', inplace=True)   
    
    return jsonify(list(df.columns))


@app.route("/otu")
def otu():
    results = session.query(OTU.lowest_taxonomic_unit_found).all()
    # Convert list of tuples into normal list
    otu_names = list(np.ravel(results))

    return jsonify(otu_names)


@app.route("/metadata/<sample>")
def sample_query(sample):
    sample_name = sample.replace("BB_", "")
    result = session.query(Samples_MetaData.AGE, Samples_MetaData.BBTYPE, Samples_MetaData.ETHNICITY,
                           Samples_MetaData.GENDER, Samples_MetaData.LOCATION, Samples_MetaData.SAMPLEID).filter_by(
        SAMPLEID=sample_name).all()

    record = result[0]
    data = {
        "AGE": record[0],
        "BBTYPE": record[1],
        "ETHNICITY": record[2],
        "GENDER": record[3],
        "LOCATION": record[4],
        "SAMPLEID": record[5]
    }
    return jsonify(data)


@app.route("/wfreq/<sample>")
def wfreq(sample):
    sample_name = sample.replace("BB_", "")
    result = session.query(Samples_MetaData.WFREQ).all()

    wfreq = np.ravel(result)   
    return jsonify(int(wfreq[0]))


@app.route('/samples/<sample>')
def samples(sample):
    """Return a list dictionaries containing `otu_ids` and `sample_values`."""
    stmt = session.query(Samples).statement
    df = pd.read_sql_query(stmt, session.bind)

    # Make sure that the sample was found in the columns, else throw an error
    if sample not in df.columns:
        return jsonify(f"Error! Sample: {sample} Not Found!"), 400

    # Return any sample values greater than 1
    df = df[df[sample] > 1]

    # Sort the results by sample in descending order
    df = df.sort_values(by=sample, ascending=0)

    # Format the data to send as json
    data = [{
        "otu_ids": df[sample].index.values.tolist(),
        "sample_values": df[sample].values.tolist()
    }]
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=False)