from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import config

import pandas as pd
import plotly
import plotly.graph_objects as go
import json

import datetime



##Read and process data for populating choropleth map.
df = pd.read_csv('static/mapdata.csv')
for col in df.columns:
    if col == 'meals' or col =='hosp_count':
        df[col] = df[col].astype(int)
    else:
        df[col] = df[col].astype(str)

df['text'] = df['meals'].astype(str) + ' Meals' + '<br>' + \
    df['state'] + '<br>' + df['spend'] + ' Spent' + '<br><br>' + \
    'Hospitals Served (' + df['hosp_count'].astype(str) + '):' + '<br>' + df['hospitals']

##Read and process data for populating progress table and dashboard entries.
td_df = pd.read_csv('static/tabledata.csv')
for col in td_df.columns:
    if col == 'Dollar Value':
        td_df[col] = td_df[col].astype(float)

#Calculate remainder of summary statistics
#First sum the value, then convert to currency and reformat for displaying in html.
value_count_float = round(sum(td_df[td_df.columns[3]]), 2)
value_count = str(value_count_float)
td_df[td_df.columns[3]] = td_df[td_df.columns[3]].map('${:,.2f}'.format)

table_data = td_df.to_html(index=False, classes='table table-hover', justify='center', border=0)
#table_data = zip(td_df['date'], td_df['hospital'], td_df['restaurant'], td_df['value'])

##Calcuate remaining parameters.
hosp_count = df['hosp_count'].sum(axis=0)
curr_donation = 15715  ##Manually enter the donation amount.
curr_date = datetime.date(2020, 4, 30)  ##Manually enter the current date of update
meal_count = df['meals'].sum(axis=0)
average_daily = round(value_count_float  / (curr_date - datetime.date(2020, 3, 20)).days, 2)
days_remaining = int((curr_donation - float(value_count)) / average_daily)     




app = Flask(__name__)
app.config.from_object('config.Config')


db = SQLAlchemy(app)

class HospitalDB(db.Model):
    __tablename__ = 'hospitaldata'
    id = db.Column(db.Integer, primary_key=True)
    hosp_db = db.Column(db.String(200))
    contact_name_db = db.Column(db.String(200))
    contact_email_db = db.Column(db.String(200))
    contact_phone_db = db.Column(db.String(200))
    comments_db = db.Column(db.Text())

    def __init__(self, hospital, contname, contemail, contphone, com):
        self.hosp_db = hospital
        self.contact_name_db = contname
        self.contact_email_db = contemail
        self.contact_phone_db = contphone
        self.comments_db = com



@app.route('/')
def index():
    #for testing, go right to the press page
    return render_template('index.html')
    # return render_template('index.html')

@app.route('/progress')
def progress():
    fig = go.Figure(data=go.Choropleth(
        locations=df['code'],
        z=df['meals'].astype(float),
        zmin=11,
        hoverinfo = "location+text",
        locationmode='USA-states',
        colorscale=[[0, 'rgb(132,203,131)'], [1, 'rgb(0, 68, 27)']],
        #colorscale='Greens',
        autocolorscale=False,
        text=df['text'], # hover text
        marker_line_color='grey', # line markers between states
        colorbar_title="Meals Served", 
        colorbar=dict(len=0.5, thickness=10),
    ))

    fig.update_layout(
        # title_text='Meals, Spend, and Hospitals Served Per State',
        dragmode = False,
        margin = dict(
            l=0,
            r=0,
            t=0,
            b=0,
            pad=0
        ),
        font=dict(
            family="'Poppins', sans-serif",
            color="#00B964"
        ),
        geo = dict(
            scope='usa',
            projection=go.layout.geo.Projection(type = 'albers usa'),
            showlakes=True, # lakes
            lakecolor='rgb(255, 255, 255)'),
    )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('progress.html', plot=graphJSON, table_data=table_data, test_var = table_data, 
    hosp_count = hosp_count, meal_count = meal_count, value_count = value_count, 
    average_daily = average_daily, days_remaining = days_remaining)

@app.route('/suggest')
def suggest():
    return render_template('contact.html')

@app.route('/partners')
def partners():
    return render_template('partners.html')

@app.route('/press')
def press():
    return render_template('press.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        #get data from form.
        hospital_name = request.form['hospital_name']
        contact_name = request.form['contact_name']
        contact_email = request.form['contact_email']
        contact_phone = request.form['contact_phone']
        comment_field = request.form['comment_field']
        #print(hospital_name,  contact_name, contact_email, contact_phone, comment_field)
        if hospital_name == '':
            return render_template('contact.html', message='Please Enter a Hospital Name!')
        
        data = HospitalDB(hospital_name, contact_name, contact_email, contact_phone, comment_field)
        db.session.add(data)
        db.session.commit()

        return render_template('contact_success.html')


if __name__ == '__main__':
    app.run()


