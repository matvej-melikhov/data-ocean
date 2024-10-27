import pytest
import uuid


@pytest.fixture(scope='session')
def app():
    import main  # регистрирует routes, admin_views, models
    from app import application, db
    application.config['TESTING'] = True
    application.config['WTF_CSRF_ENABLED'] = False
    application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with application.app_context():
        db.create_all()
    return application


@pytest.fixture
def client(app):
    with app.test_client() as c:
        yield c


def test_home_page(client):
    assert client.get('/').status_code == 200

def test_registration_page(client):
    assert client.get('/registration').status_code == 200

def test_login_page(client):
    assert client.get('/login').status_code == 200

def test_profile_redirects_when_not_logged_in(client):
    assert client.get('/profile').status_code == 302

def test_blog_redirects_when_not_logged_in(client):
    assert client.get('/blog').status_code == 302

def test_404_page(client):
    assert client.get('/nonexistent-page-xyz-123').status_code == 404

def test_create_post_redirects_when_not_logged_in(client):
    assert client.get('/create-post').status_code == 302

def test_registration_post(client):
    login = f'testuser_{uuid.uuid4().hex[:8]}'
    r = client.post('/registration', data={
        'name': 'Test', 'last_name': 'User',
        'login': login, 'password': 'testpassword',
    })
    assert r.status_code in (200, 302)
