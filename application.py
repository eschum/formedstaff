from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import config

#####Code additions to test the rendering of Plotly map.#####
import pandas as pd
import plotly
import plotly.graph_objects as go
import json
df = pd.read_csv('static/mapdata.csv')

for col in df.columns:
    if col == 'packages' or col =='hosp_count':
        df[col] = df[col].astype(int)
    df[col] = df[col].astype(str)

df = df.dropna(axis=0)
df = df.dropna(axis=1)
df.reset_index(drop=True)


df['text'] = df['packages'] + ' Packages' + '<br>' + \
    df['state'] + '<br>' + df['spend'] + ' Spent' + '<br><br>' + \
    'Hospitals Served (' + df['hosp_count'] + '):' + '<br>' + df['hospitals']

#have a state variable to test whether or not the plot is loaded
#graph_loaded = False
######## end of code addition######


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
    return render_template('progress.html')

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

@app.route('/test')
def map_test():
    # if not graph_loaded:
    
    fig = go.Figure(data=go.Choropleth(
        locations=df['code'],
        z=df['packages'].astype(float),
        zmin=11,
        hoverinfo = "location+text",
        locationmode='USA-states',
        colorscale=[[0, 'rgb(132,203,131)'], [1, 'rgb(0, 68, 27)']],
        #colorscale='Greens',
        autocolorscale=False,
        text=df['text'], # hover text
        marker_line_color='grey', # line markers between states
        colorbar_title="Packages", 
        colorbar=dict(len=0.5, thickness=10),
    ))

    fig.update_layout(
        # title_text='Packages, SPend, and Hospitals Served Per State',
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
    return render_template('progress-test.html', plot=graphJSON)


if __name__ == '__main__':
    app.run()


