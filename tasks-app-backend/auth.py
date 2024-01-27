from flask_httpauth import HTTPTokenAuth
from flask_jwt_extended import decode_token
from werkzeug.security import check_password_hash, generate_password_hash

# Username and password authentification
auth = HTTPTokenAuth(scheme='Bearer')

# Acceptable user credentials
users = {
    "admin": "12345",
    "user": "12345"
}


@auth.verify_token
def verify_token(token):
    try:
        # Decode the token
        decoded_token = decode_token(token)
        user_identity = decoded_token['sub']  # 'sub' is the subject, which is the user identity

        # Perform additional verification if necessary
        if user_identity in users:
            return user_identity

    except:
        
        pass

    return False
