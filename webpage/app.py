from flask import Flask, render_template
import datetime
app = Flask(__name__)

sensor1Value = 1000
sensor2Value = 2000

@app.route("/")
def hello():
   now = datetime.datetime.now()
   timeString = now.strftime("%Y-%m-%d %H:%M")
   templateData = {
      'sensor1' : sensor1Value,
      'sensor2': sensor2Value
      }
   return render_template('index.html', **templateData)
 
if __name__ == "__main__":
   app.run(host='0.0.0.0', port=80, debug=True)
