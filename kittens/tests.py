import pytest
from rest_framework.test import APIClient
from kittens.models import Breed
from kittens.models import Kitten, Breed, Rating
from django.contrib.auth import get_user_model
from rest_framework import status


User = get_user_model()


@pytest.mark.django_db
def test_breed_list():
    Breed.objects.create(name="Siamese")
    Breed.objects.create(name="Persian")

    client = APIClient()
    response = client.get('/api/breedlist')

    assert response.status_code == 200
    assert len(response.data) == 2
    assert response.data[0]['name'] == "Siamese"


@pytest.mark.django_db
def test_kitten_list():
    breed = Breed.objects.create(name="Siamese")
    user = User.objects.create_user(username="testuser", password="password")

    Kitten.objects.create(name="Kitty1", breed=breed, age_in_months=2, owner=user, color="red", description="description")
    Kitten.objects.create(name="Kitty2", breed=breed, age_in_months=3, owner=user, color="red", description="description")

    client = APIClient()
    response = client.get('/api/kittenlist')

    assert response.status_code == 200
    assert len(response.data) == 2
    assert response.data[0]['name'] == "Kitty1"


@pytest.mark.django_db
def test_kitten_by_breed_success():
    breed = Breed.objects.create(name="Siamese")
    user = User.objects.create_user(username="testuser", password="password")
    Kitten.objects.create(name="Kitty1", breed=breed, age_in_months=2, owner=user, color="red", description="description")

    client = APIClient()
    response = client.post('/api/kittenbybreed', data={'breed_id': breed.id}, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['name'] == "Kitty1"


@pytest.mark.django_db
def test_kitten_by_breed_missing_breed_id():
    client = APIClient()
    response = client.post('/api/kittenbybreed', data={}, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "Необходим параметр 'breed_id'"


@pytest.mark.django_db
def test_kitten_by_breed_not_found():
    breed = Breed.objects.create(name="Siamese")

    client = APIClient()
    response = client.post('/api/kittenbybreed', data={'breed_id': breed.id + 1}, format='json')

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["message"] == "Котята не найдены."


@pytest.mark.django_db
def test_kitten_detail_success():
    breed = Breed.objects.create(name="Siamese")
    user = User.objects.create_user(username="testuser", password="password")
    kitten = Kitten.objects.create(name="Kitty1", breed=breed, age_in_months=2, owner=user, color="red", description="description")

    client = APIClient()
    response = client.post('/api/kittendetail', data={'kitten_id': kitten.id}, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['name'] == "Kitty1"
    assert response.data['age_in_months'] == 2
    assert response.data['color'] == "red"


@pytest.mark.django_db
def test_kitten_detail_missing_kitten_id():
    client = APIClient()
    response = client.post('/api/kittendetail', data={}, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "Необходим параметр 'kitten_id'"


@pytest.mark.django_db
def test_kitten_detail_not_found():
    client = APIClient()
    response = client.post('/api/kittendetail', data={'kitten_id': 999}, format='json')

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["message"] == "Котёнок не найден."


@pytest.mark.django_db
def test_create_kitten_success():
    breed = Breed.objects.create(name="Siamese")
    user = User.objects.create_user(username="testuser", password="password")
    client = APIClient()
    client.force_authenticate(user=user)

    kitten_data = {
        "name": "Kitty1",
        "breed": breed.id,
        "age_in_months": 2,
        "color": "red",
        "description": "Cute kitten"
    }

    response = client.post('/api/kittenmanage', data=kitten_data, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['name'] == "Kitty1"
    assert Kitten.objects.count() == 1


@pytest.mark.django_db
def test_create_kitten_failure():
    user = User.objects.create_user(username="testuser", password="password")
    client = APIClient()
    client.force_authenticate(user=user)

    kitten_data = {
        "name": "",
        "age_in_months": 2,
    }

    response = client.post('/api/kittenmanage', data=kitten_data, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'name' in response.data


@pytest.mark.django_db
def test_update_kitten_success():
    breed = Breed.objects.create(name="Siamese")
    user = User.objects.create_user(username="testuser", password="password")
    kitten = Kitten.objects.create(name="Kitty1", breed=breed, age_in_months=2, owner=user, color="red", description="description")

    client = APIClient()
    client.force_authenticate(user=user)

    update_data = {
        "kitten_id": kitten.id,
        "name": "KittyUpdated",
    }

    response = client.put('/api/kittenmanage', data=update_data, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['name'] == "KittyUpdated"


@pytest.mark.django_db
def test_update_kitten_failure_missing_id():
    user = User.objects.create_user(username="testuser", password="password")
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.put('/api/kittenmanage', data={}, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "Необходим параметр 'kitten_id'"


@pytest.mark.django_db
def test_delete_kitten_success():
    breed = Breed.objects.create(name="Siamese")
    user = User.objects.create_user(username="testuser", password="password")
    kitten = Kitten.objects.create(name="Kitty1", breed=breed, age_in_months=2, owner=user, color="red", description="description")

    client = APIClient()
    client.force_authenticate(user=user)

    delete_data = {
        "kitten_id": kitten.id,
    }

    response = client.delete('/api/kittenmanage', data=delete_data, format='json')

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Kitten.objects.count() == 0


@pytest.mark.django_db
def test_delete_kitten_failure_missing_id():
    user = User.objects.create_user(username="testuser", password="password")
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.delete('/api/kittenmanage', data={}, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "Необходим параметр 'kitten_id'"


@pytest.mark.django_db
def test_register_user_success():
    client = APIClient()
    
    registration_data = {
        "username": "newuser",
        "password": "securepassword123"
    }

    response = client.post('/api/register', data=registration_data, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert 'refresh' in response.data
    assert 'access' in response.data

    user = User.objects.get(username="newuser")
    assert user is not None
    assert user.check_password("securepassword123")


@pytest.mark.django_db
def test_register_user_missing_username():
    client = APIClient()
    
    registration_data = {
        "password": "securepassword123"
    }

    response = client.post('/api/register', data=registration_data, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "Необходим параметр 'username'"


@pytest.mark.django_db
def test_register_user_missing_password():
    client = APIClient()
    
    registration_data = {
        "username": "newuser"
    }

    response = client.post('/api/register', data=registration_data, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "Необходим параметр 'password'"


@pytest.mark.django_db
def test_register_user_duplicate_username():
    client = APIClient()
    
    User.objects.create_user(username="existinguser", password="securepassword123")

    registration_data = {
        "username": "existinguser",
        "password": "anotherpassword456"
    }

    response = client.post('/api/register', data=registration_data, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "Пользователь с таким именем уже существует."


@pytest.mark.django_db
def test_register_user_invalid_username():
    client = APIClient()
    
    registration_data = {
        "username": "",
        "password": "securepassword123"
    }

    response = client.post('/api/register', data=registration_data, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "Необходим параметр 'username'"


@pytest.mark.django_db
def test_rate_kitten_success_add():
    client = APIClient()
    
    # Создание тестового пользователя и котенка
    breed = Breed.objects.create(name="Siamese")
    user = User.objects.create_user(username="testuser", password="password")
    kitten = Kitten.objects.create(name="Fluffy", age_in_months=2, owner=user, color="white", breed=breed)

    # Авторизация пользователя
    client.force_authenticate(user=user)

    # Данные для оценки котенка
    rating_data = {
        "kitten_id": kitten.id,
        "rating_value": 5
    }

    # Выполнение POST-запроса для оценки
    response = client.post('/api/ratekitten', data=rating_data, format='json')

    # Проверка успешного добавления оценки
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["message"] == "Оценка успешно добавлена."

    # Проверка, что рейтинг был добавлен в базу данных
    rating = Rating.objects.get(kitten=kitten, user=user)
    assert rating.rating == 5


@pytest.mark.django_db
def test_rate_kitten_success_update():
    client = APIClient()
    
    # Создание тестового пользователя и котенка
    breed = Breed.objects.create(name="Siamese")
    user = User.objects.create_user(username="testuser", password="password")
    kitten = Kitten.objects.create(name="Fluffy", age_in_months=2, owner=user, color="white", breed=breed)

    # Создание первоначальной оценки
    Rating.objects.create(kitten=kitten, user=user, rating=3)

    # Авторизация пользователя
    client.force_authenticate(user=user)

    # Данные для обновления оценки котенка
    rating_data = {
        "kitten_id": kitten.id,
        "rating_value": 4
    }

    # Выполнение POST-запроса для обновления оценки
    response = client.post('/api/ratekitten', data=rating_data, format='json')

    # Проверка успешного обновления оценки
    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "Оценка обновлена."

    # Проверка, что рейтинг был обновлен в базе данных
    rating = Rating.objects.get(kitten=kitten, user=user)
    assert rating.rating == 4


@pytest.mark.django_db
def test_rate_kitten_missing_kitten_id():
    client = APIClient()
    
    # Создание тестового пользователя
    user = User.objects.create_user(username="testuser", password="password")
    client.force_authenticate(user=user)

    # Данные для оценки без указания kitten_id
    rating_data = {
        "rating_value": 5
    }

    # Выполнение POST-запроса для оценки
    response = client.post('/api/ratekitten', data=rating_data, format='json')

    # Проверка ответа на отсутствие kitten_id
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "Необходим параметр 'kitten_id'"


@pytest.mark.django_db
def test_rate_kitten_missing_rating_value():
    client = APIClient()
    
    # Создание тестового пользователя
    user = User.objects.create_user(username="testuser", password="password")
    client.force_authenticate(user=user)

    # Данные для оценки без указания rating_value
    rating_data = {
        "kitten_id": 1  # Используем несуществующий ID
    }

    # Выполнение POST-запроса для оценки
    response = client.post('/api/ratekitten', data=rating_data, format='json')

    # Проверка ответа на отсутствие rating_value
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "Необходим параметр 'rating_value'"


@pytest.mark.django_db
def test_rate_kitten_invalid_rating_value():
    client = APIClient()
    
    # Создание тестового пользователя и котенка
    breed = Breed.objects.create(name="Siamese")
    user = User.objects.create_user(username="testuser", password="password")
    kitten = Kitten.objects.create(name="Fluffy", age_in_months=2, owner=user, color="white", breed=breed)

    # Авторизация пользователя
    client.force_authenticate(user=user)

    # Данные для оценки с недопустимым rating_value
    rating_data = {
        "kitten_id": kitten.id,
        "rating_value": 10  # Недопустимое значение
    }

    # Выполнение POST-запроса для оценки
    response = client.post('/api/ratekitten', data=rating_data, format='json')

    # Проверка ответа на недопустимое значение рейтинга
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "Оценка должна быть в пределах от 1 до 5"


@pytest.mark.django_db
def test_rate_kitten_kitten_not_found():
    client = APIClient()
    
    # Создание тестового пользователя
    user = User.objects.create_user(username="testuser", password="password")
    client.force_authenticate(user=user)

    # Данные для оценки с несуществующим kitten_id
    rating_data = {
        "kitten_id": 9999,  # Не существует в базе данных
        "rating_value": 5
    }

    # Выполнение POST-запроса для оценки
    response = client.post('/api/ratekitten', data=rating_data, format='json')

    # Проверка ответа на отсутствие котенка
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["detail"] == "No Kitten matches the given query."