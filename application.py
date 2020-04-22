from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import config

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

if __name__ == '__main__':
    app.run()


