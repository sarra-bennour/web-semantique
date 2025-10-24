from flask import Flask, jsonify, request
from flask_cors import CORS
from api.routes import api_routes
import os

app = Flask(__name__)
CORS(app)

# Enregistrement des routes
app.register_blueprint(api_routes, url_prefix='/api')

@app.route('/')
def home():
    return jsonify({"message": "Eco Platform API is running!"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)