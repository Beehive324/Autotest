#API using flask
"""
from flask import Flask
import requests
import requests 
import jsonify
from pyfiglet import Figlet


f = Figlet(font='slant')

app  = Flask(__name__)

#the index routin page
@app.route('/', methods=['GET'])
def index():
    return f"{f.renderText('AutoTest')}" #string interprolation

#the api routes of the application
@app.route(f'/api/v1/recon/{ip_port}', methods=['POST'])
def recon():
    data = request.json
    return jsonify({"message": "Reconnaissance phase started"})

@app.route('/api/v1/planning', methods=['POST'])
def planning():
    data = request.json
    return jsonify({"message": "Planning phase started"})


@app.route('/api/v1/access', methods=['POST'])
def access():
    data = request.json
    return jsonify({"message": "Access phase started"})


@app.route('/api/v1/reporting', methods=['POST'])
def reporting():
    data = request.json
    return jsonify({"message": "Reporting phase started"})


if __name__ == '__main__':
    app.run(debug=True)
"""