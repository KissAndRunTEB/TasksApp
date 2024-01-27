from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models import create_database, sample_data
from views import configure_routes

app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = 'sdfdssf90u'

jwt = JWTManager(app)

# Configure CORS
# For development:
CORS(app)

# For production, specify the origins:
# CORS(app, resources={r"/api/*": {"origins": "http://domain.com"}})


configure_routes(app)

if __name__ == '__main__':
    # Initial creation of db and filling with sample data
    create_database()
    sample_data()

    # Running flask app
    app.run(debug=app.config['DEBUG'])