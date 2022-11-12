from flask import (Flask, render_template, request,session,flash)
from flask_sessionstore import Session
from flask_session_captcha import FlaskSessionCaptcha
import MySQLdb

import re

import requests

API_KEY = ""
token_response = requests.post('https://iam.cloud.ibm.com/identity/token', data={"apikey":
 API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
mltoken = token_response.json()["access_token"]

header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}

db = MySQLdb.connect("localhost", "root", "Thenu@12", "ckdsystem")

app = Flask(__name__)
app.secret_key=''

app.config['CAPTCHA_ENABLE'] = True
app.config['CAPTCHA_LENGTH'] = 5
app.config['CAPTCHA_WIDTH'] = 160
app.config['CAPTCHA_HEIGHT'] = 50
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
app.config['CAPTCHA_SESSION_KEY'] = 'captcha_image'
app.config['SESSION_TYPE'] = 'sqlalchemy'
Session(app)
captcha = FlaskSessionCaptcha(app)

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
decimal= r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"

  
@app.route('/')
@app.route('/home')
def home():
    return render_template("home.html")

@app.route('/login', methods =['GET', 'POST'])
def login():
    if (request.method == 'POST'):
        credential = request.form.get('credential')
        password = request.form.get('password')
        cursor = db.cursor()
        if(re.fullmatch(regex, credential)):
            cursor.execute('SELECT * FROM users WHERE email = % s AND password = % s', (credential, password,))
        else:
            cursor.execute('SELECT * FROM users WHERE phone = % s AND password = % s', (credential, password,))

        account = cursor.fetchone()
        if account:
            session["loggedin"] = True
            session['id'] = account[1]
            if captcha.validate():
                return render_template("home.html")
            else:
                flash('Wrong captcha', 'error')
                return render_template("login.html")
            
        flash('Wrong username or password', 'error')
        return render_template("login.html")

    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop('id',None)
    return render_template("home.html")

@app.route('/register', methods =['GET', 'POST'])
def register():
    if (request.method == 'POST'):
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        repassword = request.form.get('confirmpassword')
        correctpass=re.fullmatch(decimal, password)
        if not correctpass:
            flash('Password not strong enough','error')
        else:
            if (password!=repassword):
                flash("Passwords don't match", 'error')
            else:
                cursor = db.cursor()
                cursor.execute('SELECT * FROM users WHERE email= % s', (email, ))
                account = cursor.fetchone()
                if account:
                    flash('User already registered', 'error')
                    return render_template("register.html")
                else:  
                    cursor.execute('INSERT INTO users VALUES (% s, % s, % s, % s)', (name, email, phone, password, ))
                    db.commit()
                    return render_template("login.html")

    return render_template("register.html")

@app.route('/testform', methods =['GET', 'POST'])
def testform():
    session["loggedin"] = False
    if 'id' in session:
        session["loggedin"] = True
    else:
        flash('Please login first','error')
        return render_template("login.html")
    if (request.method == 'POST'):
      id=10
      age =request.form.get('age')
      bp = request.form.get('blood pressure')
      sg = request.form.get('specific gravity')
      al = request.form.get('albumin')
      su = request.form.get('sugar')
      rbc = request.form.get('red blood cells')
      pc = request.form.get('pus cell')
      pcc = request.form.get('pus cell clumps')
      ba = request.form.get('bacteria')
      bgr = request.form.get('blood glucose random')
      bu = request.form.get('blood urea')
      sc = request.form.get('serum creatinine')
      sod = request.form.get('sodiu')
      pot = request.form.get('potassium')
      hemo = request.form.get('hemoglobin')
      pcv = request.form.get('packed cell volume')
      wc = request.form.get('white blood cell count')
      rc = request.form.get('red blood cell count')
      htn = request.form.get('hypertension')
      dm = request.form.get('diabetes mellitus')
      cad = request.form.get('coronary artery disease')
      appet = request.form.get('appetite')
      pe = request.form.get('pedal edema')
      ane = request.form.get('anemia')
    
      t=[[id,age,bp,sg,al,su,rbc,pc,pcc,ba,bgr,bu,sc,sod,pot,hemo,pcv,wc,rc,htn,dm,cad,appet,pe,ane]]
        
      payload_scoring = {"input_data": [{"fields": [['id','age','bp','sg','al','su','rbc','pc','pcc','ba','bgr','bu','sc','sod','pot','hemo','pcv','wc','rc','htn','dm','cad','appet','pe','ane']], "values": t}]}

      response_scoring = requests.post('https://us-south.ml.cloud.ibm.com/ml/v4/deployments/c7d79b2c-9171-449a-903d-cb3dc1038fd2/predictions?version=2022-10-29', json=payload_scoring,
      headers={'Authorization': 'Bearer ' + mltoken})
      print("Scoring response")
      pred=response_scoring.json()
      output=pred['predictions'][0]['values'][0][0]
      print(output)
      if (output=="ckd"):
        output="Positive"
      else:
        output="Negative"
      return render_template("result.html",y=output)

    return render_template("testform.html")

if __name__ == "__main__":
     app.run(debug=True)