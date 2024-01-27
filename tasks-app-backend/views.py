from flask import jsonify, request, make_response
from flask_jwt_extended import create_access_token
from db import get_db_connection
from auth import auth, users
from utils import is_valid_date
from werkzeug.security import check_password_hash

def configure_routes(app):
    @app.errorhandler(401)
    def unauthorized(error):
        return make_response(jsonify({'error': 'Nieautoryzowany dostęp'}), 401)
    
    @app.route('/tasks', methods=['GET'])
    def get_tasks():
        conn = get_db_connection()
        tasks = conn.execute('SELECT * FROM tasks').fetchall()
        conn.close()
        return jsonify([dict(row) for row in tasks])

    @app.route('/tasks/<int:task_id>', methods=['GET'])
    def get_task(task_id):
        conn = get_db_connection()
        task = conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()
        conn.close()
        return jsonify(dict(task)) if task else ('', 404)

        
    @app.route('/tasks', methods=['POST'])
    @auth.login_required
    def create_task():
        new_task = request.json

        # Validate the existence of required fields
        if not new_task or 'title' not in new_task or 'description' not in new_task or 'date_done' not in new_task:
            return jsonify({'error': 'Brakuje wymaganych pól'}), 400

        # Validate data types and content
        title = new_task['title']
        description = new_task['description']
        date_done = new_task['date_done']

        if not isinstance(title, str) or not title:
            return jsonify({'error': 'Niepoprawny tytuł'}), 400

        if not isinstance(description, str):
            return jsonify({'error': 'Niepoprawny opis'}), 400

        #SQLittle doesn't provide data type thats why str is used
        #SQLite only has 4 primitive data types: INTEGER, REAL, TEXT, and BLOB
        if not isinstance(date_done, str) or not is_valid_date(date_done):
            return jsonify({'error': 'Błedna data. Powinna być w formacie YYYY-MM-DD'}), 400

        # Insert the new task into the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO tasks (title, description, date_done) VALUES (?, ?, ?)',
                    (title, description, date_done))
        conn.commit()
        task_id = cursor.lastrowid
        conn.close()

        return jsonify({'message': 'Zadanie utworzone', 'task_id': task_id}), 201


    @app.route('/tasks/<int:task_id>', methods=['PUT'])
    @auth.login_required
    def update_task(task_id):
        updated_task = request.json

        # Validate the existence of required fields
        if not updated_task or 'title' not in updated_task or 'description' not in updated_task or 'date_done' not in updated_task:
            return jsonify({'error': 'Brakuje ywmaganych pól'}), 400

        # Validate data types and content
        title = updated_task['title']
        description = updated_task['description']
        date_done = updated_task['date_done']

        if not isinstance(title, str) or not title:
            return jsonify({'error': 'Niepoprawn tytuł'}), 400

        if not isinstance(description, str):
            return jsonify({'error': 'Niepoprawny opis'}), 400

        if not isinstance(date_done, str) or not is_valid_date(date_done):
            return jsonify({'error': 'Niepoprawna data. Powinna być w formacie YYYY-MM-DD'}), 400

        # Update the task in the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE tasks SET title = ?, description = ?, date_done = ? WHERE id = ?',
                    (title, description, date_done, task_id))
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()

        if rows_affected == 0:
            return jsonify({'error': 'Zadanie nieznalezione'}), 404

        return jsonify({'message': 'Zadanie zaaktualizowane', 'task_id': task_id}), 200


    @app.route('/tasks/<int:task_id>', methods=['DELETE'])
    @auth.login_required
    def delete_task(task_id):
        conn = get_db_connection()
        conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        conn.commit()
        conn.close()
        # Code 204 nothing to return
        return ('', 204)
           
        
    @app.route('/login', methods=['POST'])
    def login():
        if not request.is_json:
            return jsonify({"msg": "Missing JSON in request"}), 400

        username = request.json.get('username', None)
        password = request.json.get('password', None)

        if not username or not password:
            return jsonify({"msg": "Missing username or password"}), 400

        # Validate user credentials
        user_password = users.get(username)
        if not user_password or not user_password==password:
            return jsonify({"msg": "Bad username or password"}), 401

        # Create JWT token
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200