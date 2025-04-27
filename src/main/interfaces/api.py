#API using flask
import flask


@app.route('/', methods=['GET'])
def index():
    return "Hello, World!"

@app.route('/api/v1/recon', methods=['POST'])
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