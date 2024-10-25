import pytest
from main import application


@pytest.fixture
def client():
    application.testing = True
    application.config['WTF_CSRF_ENABLED'] = False
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

def test_profile_redirects_when_not_logged_in(client):
    response = client.get('/profile')
    assert response.status_code == 302

def test_blog_redirects_when_not_logged_in(client):
    response = client.get('/blog')
    assert response.status_code == 302

def test_404_page(client):
    response = client.get('/nonexistent-page-that-does-not-exist')
    assert response.status_code == 404

def test_create_post_redirects_when_not_logged_in(client):
    response = client.get('/create-post')
    assert response.status_code == 302

def test_registration_post(client):
    response = client.post('/registration', data={
        'name': 'Test',
        'last_name': 'User',
        'login': 'testuser_unique_123',
        'password': 'testpassword',
    })
    assert response.status_code in (200, 302)
