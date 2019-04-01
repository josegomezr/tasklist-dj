from django.test import TestCase, tag
from .models import Task
from django.contrib.auth.models import User
import json

from django.test.client import RequestFactory

class TasksTestCase(TestCase):

    def _make_user(self, username):
        user = User(username=username)
        user.set_password('123456')
        user.is_active = 1
        user.save()
        return user
    
    def _make_task(self, user, content, done=False, **kwargs):
        return Task.objects.create(
            user=user,
            content=content,
            done=done,
            **kwargs,
        )

    def setUp(self):
        u1 = self._make_user('test1')
        u2 = self._make_user('test2')
        self.task1 = self._make_task(user=u1, content='task A for user 1', id=1)
        self.task2 = self._make_task(user=u1, content='task B for user 1', done=True, id=2)
        
        self.task3 = self._make_task(user=u2, content='task C for user 2', id=3)
    

    def _get_token(self, username):
        payload = {
            'username': username,
            'password': '123456',
            }

        response = self.client.post('/get-token/', 
            data=json.dumps(payload), 
            content_type='application/json'
            )
        return response.json()['token']
    
    def test_list_tasks_guest(self):
        response = self.client.get('/tasks/')
        # it should get 401 Unauthorized
        self.assertEquals(response.status_code, 401)

    def test_list_tasks_auth(self):
        token = self._get_token('test1')
        response = self.client.get('/tasks/', **{
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(token)
        })
        # it should get 200 OK 
        self.assertEquals(response.status_code, 200)

        payload = response.json()['data']

        # it should get 2 objects, the third doesn't belong
        # to this user.
        self.assertEquals(len(payload), 2)
    
    
    def test_get_task_not_belonging(self):
        token = self._get_token('test1')
        response = self.client.get('/tasks/3', **{
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(token)
        })
        # it should get 404 not found
        self.assertEquals(response.status_code, 404)

    def test_delete_task(self):
        token = self._get_token('test1')
        response = self.client.delete('/tasks/1/delete', **{
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(token)
        })
        # it should get 200 OK 
        self.assertEquals(response.status_code, 204)

        self.assertEquals(False, Task.objects.filter(pk=1).exists())
        self.assertEquals(2, len(Task.objects.all()))
    
    def test_delete_task_not_belonging(self):
        token = self._get_token('test2')
        response = self.client.delete('/tasks/1/delete', **{
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(token)
        })
        # it should get 400 Not found
        self.assertEquals(response.status_code, 404)

        self.assertEquals(True, Task.objects.filter(pk=1).exists())
        self.assertEquals(3, len(Task.objects.all()))

    def test_mark_task_done(self):
        token = self._get_token('test1')
        response = self.client.put('/tasks/1/mark/done', **{
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(token)
        })
        # it should get 200 OK 
        self.assertEquals(response.status_code, 204)

        self.task1.refresh_from_db()
        self.assertEquals(True, self.task1.done)

    def test_mark_task_done_missing(self):
        token = self._get_token('test1')
        response = self.client.put('/tasks/99/mark/done', **{
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(token)
        })
        # it should get 200 OK 
        self.assertEquals(response.status_code, 404)
    
    def test_mark_task_undone(self):
        token = self._get_token('test1')
        response = self.client.put('/tasks/1/mark/undone', **{
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(token)
        })
        # it should get 200 OK 
        self.assertEquals(response.status_code, 204)

        self.task1.refresh_from_db()
        self.assertEquals(False, self.task1.done)

    def test_mark_task_undone_missing(self):
        token = self._get_token('test1')
        response = self.client.put('/tasks/99/mark/undone', **{
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(token)
        })
        # it should get 200 OK 
        self.assertEquals(response.status_code, 404)
    
    def test_update_task_get_method(self):
        token = self._get_token('test1')
        response = self.client.get('/tasks/1/update', **{
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(token)
        })
        # it should get 200 OK 
        self.assertEquals(response.status_code, 405)
    
    def test_update_task(self):
        token = self._get_token('test1')
        payload = json.dumps({
            'content': 'A new note!',
        })

        response = self.client.put('/tasks/1/update', payload, **{
            'content_type': 'application/json',
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(token)
        })
        # it should get 200 OK 
        self.assertEquals(response.status_code, 204)

        old_content = self.task1.content
        self.task1.refresh_from_db()
        new_content = self.task1.content

        self.assertNotEquals(old_content, new_content)
        
        
        payload = json.dumps({
            'content': 'A new note! x2',
            'done': True,
        })

        response = self.client.put('/tasks/2/update', payload, **{
            'content_type': 'application/json',
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(token)
        })
        # it should get 200 OK 
        self.assertEquals(response.status_code, 204)

        old_content = self.task2.content
        self.task2.refresh_from_db()
        new_content = self.task2.content

        self.assertNotEquals(old_content, new_content)
        self.assertEquals(True, self.task2.done)
    
    def test_update_task_non_belonging(self):
        token = self._get_token('test1')
        payload = json.dumps({
            'content': 'A new note!',
        })

        response = self.client.put('/tasks/3/update', payload, **{
            'content_type': 'application/json',
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(token)
        })
        # it should get 404
        self.assertEquals(response.status_code, 404)

        old_content = self.task1.content
        self.task1.refresh_from_db()
        new_content = self.task1.content

        self.assertEquals(old_content, new_content)
    
    def test_create_task(self):
        token = self._get_token('test1')
        payload = json.dumps({
            'content': 'A new note!',
        })

        response = self.client.put('/tasks/create', payload, **{
            'content_type': 'application/json',
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(token)
        })
        # it should get 200
        self.assertEquals(response.status_code, 200)

        body = response.json()

        self.assertEquals(body['data']['content'], 'A new note!')

        self.assertEquals(len(Task.objects.all()) , 4)
        
    def test_create_empty_task(self):
        token = self._get_token('test1')
        payload = json.dumps({})

        response = self.client.put('/tasks/create', payload, **{
            'content_type': 'application/json',
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(token)
        })

        self.assertEquals(response.status_code, 400)

        self.assertEquals(len(Task.objects.all()) , 3)
        
    
