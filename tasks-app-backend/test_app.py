import base64
import unittest
import json
from app import app

class FlaskAppTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def login_and_get_token(self, username, password):
        response = self.app.post('/login', data=json.dumps({
            'username': username,
            'password': password
        }), content_type='application/json')

        if response.status_code == 200:
            data = json.loads(response.data)
            return data.get('access_token')
        else:
            return None


    def get_auth_headers(self, username, password):
        token = self.login_and_get_token(username, password)
        return {
            'Authorization': f'Bearer {token}'
        }


    def test_get_tasks(self):
        # Checking if tasks are visible for everyone, even with bad credentials
        headers = self.get_auth_headers('notuser', '55555')
    
        response = self.app.get('/tasks', headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_create_task(self):
        new_task = {
            "title": "Zadanie testowe",
            "description": "Opis zadania",
            "date_done": "2024-01-25"
        }

        headers = self.get_auth_headers('user', '12345')

        response = self.app.post('/tasks', data=json.dumps(new_task), content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 201)

        # Retrieve the task ID from the response JSON
        task_id = json.loads(response.data)['task_id']
        
        # Delete the task
        delete_response = self.app.delete(f'/tasks/{task_id}', headers=headers)
        #204 instead of 200, cause Rest API not providing extra message
        self.assertEqual(delete_response.status_code, 204)

    def test_put_task(self):
        # Create a new task
        new_task = {
            "title": "Zadanie testowe PUT",
            "description": "Opis zadania PUT",
            "date_done": "2024-01-25"
        }
        headers = self.get_auth_headers('user', '12345')
        response = self.app.post('/tasks', data=json.dumps(new_task), content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 201)

        # Retrieve the task ID from the response JSON
        task_id = json.loads(response.data)['task_id']

        # Update the task
        updated_task = {
            "title": "Zaaktualizowane zadanie",
            "description": "Zaaktualizowany opis",
            "date_done": "2024-01-06"
        }
        response = self.app.put(f'/tasks/{task_id}', data=json.dumps(updated_task), content_type='application/json', headers=headers)


        # Check if the task was updated in the database
        updated_response = self.app.get(f'/tasks/{task_id}', headers=headers)
        updated_task_data = json.loads(updated_response.data)
        self.assertEqual(updated_task_data['title'], updated_task['title'])
        self.assertEqual(updated_task_data['description'], updated_task['description'])
        self.assertEqual(updated_task_data['date_done'], updated_task['date_done'])

        # Delete the task
        delete_response = self.app.delete(f'/tasks/{task_id}', headers=headers)
        #204 instead of 200, cause Rest API not providing extra message
        self.assertEqual(delete_response.status_code, 204)

        # Verify that the task has been deleted
        verify_deleted_response = self.app.get(f'/tasks/{task_id}', headers=headers)
        self.assertEqual(verify_deleted_response.status_code, 404)


        self.assertEqual(response.status_code, 200)

    def test_delete_task(self):
        # Create a task to be later deleted
        new_task = {
            "title": "Tymczasowe zadanie",
            "description": "Opis zadania",
            "date_done": "2024-01-25"
        }
        headers = self.get_auth_headers('user', '12345')
        response = self.app.post('/tasks', data=json.dumps(new_task), content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 201)

        # Retrieve the task ID from the response JSON
        task_id = json.loads(response.data)['task_id']

        # Delete the task
        response = self.app.delete(f'/tasks/{task_id}', headers=headers)
        #204 instead of 200, cause Rest API not providing extra message
        self.assertEqual(response.status_code, 204)
                
    def test_create_task_with_bad_credentials(self):
        new_task = {
            "title": "Zadanie testowe",
            "description": "Opis zadania",
            "date_done": "2024-01-25"
        }

        headers = self.get_auth_headers('notuser', '55555')

        response = self.app.post('/tasks', data=json.dumps(new_task), content_type='application/json', headers=headers)
        self.assertNotEqual(response.status_code, 201)

    def test_put_task_with_bad_credentials(self):
        # It creates and delete task with correct credentials but tries to update it with bad ones
        
        # Create a new task
        new_task = {
            "title": "Zadanie testowe PUT",
            "description": "Opis zadania PUT",
            "date_done": "2024-01-25"
        }
        headers = self.get_auth_headers('user', '12345')
        response = self.app.post('/tasks', data=json.dumps(new_task), content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 201)

        # Retrieve the task ID from the response JSON
        task_id = json.loads(response.data)['task_id']

        #wring credentials only here
        headers = self.get_auth_headers('notuser', '55555')
        # Update the task
        updated_task = {
            "title": "Zaaktualizowane zadanie",
            "description": "Zaaktualizowany opis",
            "date_done": "2024-01-06"
        }
        response = self.app.put(f'/tasks/{task_id}', data=json.dumps(updated_task), content_type='application/json', headers=headers)


        # Check if the task was updated in the database
        updated_response = self.app.get(f'/tasks/{task_id}', headers=headers)
        updated_task_data = json.loads(updated_response.data)
        self.assertNotEqual(updated_task_data['title'], updated_task['title'])
        self.assertNotEqual(updated_task_data['description'], updated_task['description'])
        self.assertNotEqual(updated_task_data['date_done'], updated_task['date_done'])

        headers = self.get_auth_headers('user', '12345')
        # Delete the task
        delete_response = self.app.delete(f'/tasks/{task_id}', headers=headers)
        #204 instead of 200, cause Rest API not providing extra message
        self.assertEqual(delete_response.status_code, 204)

        # Verify that the task has been deleted
        verify_deleted_response = self.app.get(f'/tasks/{task_id}', headers=headers)
        self.assertEqual(verify_deleted_response.status_code, 404)
        
    def test_delete_task_with_bad_credentials(self):
        # It creates and delete test task with correct credentials
        # but in between it tries to delete it with bad credentials
                
        # Create a task to be later deleted
        new_task = {
            "title": "Tymczasowe zadanie",
            "description": "Opis zadania",
            "date_done": "2024-01-25"
        }
        headers = self.get_auth_headers('user', '12345')
        response = self.app.post('/tasks', data=json.dumps(new_task), content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 201)

        # Retrieve the task ID from the response JSON
        task_id = json.loads(response.data)['task_id']

        # Delete the task with bad credentials
        headers = self.get_auth_headers('notuser', '55555')
        response = self.app.delete(f'/tasks/{task_id}', headers=headers)
        #204 instead of 200, cause Rest API not providing extra message
        self.assertNotEqual(response.status_code, 204)

        # Delete the task
        headers = self.get_auth_headers('user', '12345')
        response = self.app.delete(f'/tasks/{task_id}', headers=headers)
        #204 instead of 200, cause Rest API not providing extra message
        self.assertEqual(response.status_code, 204)
        
if __name__ == '__main__':
    unittest.main()