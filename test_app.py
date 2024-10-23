import pytest
from main import application
from app.models import User, Post

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

def test_registrate(client):
    # Подготовка данных для теста
    data = {
        'name': 'John',
        'last_name': 'Doe',
        'login': 'johndoe',
        'password': 'securepassword'
    }

    # Отправка POST-запроса на регистрацию
    response = client.post('/registration', data=data)

    # Проверка редиректа после успешной регистрации
    assert response.status_code == 302  # Ожидаем редирект
    assert response.location.endswith('/blog')  # Проверяем, что редирект ведет на правильный маршрут

    # Проверяем, что пользователь был добавлен в БД
    user = User.query.filter_by(login='johndoe').first()
    assert user is not None  # Убедимся, что пользователь существует в БД
    assert user.name == 'John'  # Проверяем имя пользователя
    assert user.last_name == 'Doe'  # Проверяем фамилию пользователя