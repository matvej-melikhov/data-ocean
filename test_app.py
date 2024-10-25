import pytest
from main import application

@pytest.fixture
def client():
    application.testing = True
    with application.test_client() as client:
        yield client

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200

def test_registration_page(client):
    response = client.get('/registration')
    assert response.status_code == 200

def test_login_page(client):
    response = client.get('/login')
    assert response.status_code == 200

def test_profile_page(client):
    response = client.get('/')
    assert response.status_code == 200

def test_404_page(client):
    response = client.get('/some_query')
    assert response.status_code == 404

def test_create_post(client):
    response = client.post('/create-post', json={
        'title':'Test title',
        'tags': [],
        'description': 'Some description',
        'content': 'Post content'
    })
    assert response.status_code == 201

def test_registarate(client):
    response = client.post('/create-post', json={
        'name': 'test name',
        'last_name': 'test last name',
        'login': 'test login',
        'password': 'test password'
    })
    assert response.status_code == 201