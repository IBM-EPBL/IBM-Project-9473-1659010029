import string
from flask import (Flask, render_template,request)
from numpy import double

import requests

API_KEY = ""
token_response = requests.post('https://iam.cloud.ibm.com/identity/token', data={"apikey":
 API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
mltoken = token_response.json()["access_token"]

header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}

app = Flask(__name__)
app.secret_key=''

  
@app.route('/')
@app.route('/testform', methods =['GET', 'POST'])
def testform():
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
      return render_template("result.html",y=str(output))

    return render_template("testform.html")

if __name__ == "__main__":
     app.run(debug=False)
