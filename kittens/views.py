from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from kittens import models
from kittens import serializers
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken


class BreedListAPIView(APIView):
    """
    Получение списка пород

    Методы:

    GET
    Возвращает список пород.

    Пример запроса:
    ```
    GET /api/breedlist
    ```

    **Пример ответа:**
    ```
    [
        {
            "id": 1,
            "name": "Порода1"
        },
        {
            "id": 2,
            "name": "Порода2"
        },
        {
            "id": 3,
            "name": "Порода3"
        }
    ]
    ```
    Где:
        id - id породы
        name - название породы
    """
    def get(self, request: WSGIRequest):
        breeds = models.Breed.objects.all()
        serializer = serializers.BreedSerializer(breeds, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class KittenListAPIView(APIView):
    """
    Получение списка всех котят

    Методы

    ### GET
    Создает новый ресурс.

    
    Пример запроса:
    ```
    GET /api/kittenlist
    ```

    **Пример ответа:**
    ```
    [
        {
            "id": 1,
            "name": "Кот1",
            "breed": 1,
            "owner": 1
        },
        {
            "id": 2,
            "name": "Кот2",
            "breed": 2,
            "owner": 1
        }
    ]
    ```

    Где:
        id - id котенка
        name - имя котенка
        breed - id породы
        owner - id владельца
    """
    def get(self, request):
        kittens = models.Kitten.objects.all()
        serializer = serializers.KittenSerializer(kittens, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class KittenByBreedListAPIView(APIView):
    """
    Получение списка котят определенной породы по фильтру

    Методы

    POST

    Параметры:
    - `breed_id` (int): id породы

    Пример запроса:
    ```
    POST /api/kittenbybreed
    {
        "breed_id": "1"
    }
    ```

    Пример ответа:
    ```
    [
        {
            "id": 1,
            "name": "Кот1",
            "breed": 1,
            "owner": 1
        },
        {
            "id": 4,
            "name": "Кот5",
            "breed": 1,
            "owner": 1
        }
    ]
    ```
    Где:
        id - id котенка
        name - имя котенка
        breed - id породы
        owner - id владельца
    """
    def post(self, request):
        breed_id = request.data.get('breed_id')
        if not breed_id:
            return Response({"error": "Необходим параметр 'breed_id'"}, status=status.HTTP_400_BAD_REQUEST)

        kittens = models.Kitten.objects.filter(breed_id=breed_id)

        if not kittens.exists():
            return Response({"message": "Котята не найдены."}, status=status.HTTP_404_NOT_FOUND)

        serializer = serializers.KittenSerializer(kittens, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class KittenDetailAPIView(APIView):
    """
    Получение подробной информации о котенке.

    Методы

    POST

    Параметры:
    - `kitten_id` (int): id котенка

    Пример запроса:
    ```
    POST /api/kittendetail
    {
        "kitten_id": 1
    }
    ```

    Пример ответа:
    ```
    {
        "id": 1,
        "name": "Кот1",
        "color": "Черный",
        "age_in_months": 10,
        "description": "Черный кот",
        "breed": 1,
        "owner": 1
    }
    ```
    Где:
        id - id котенка
        name - имя котенка
        color - цвет котенка
        age_in_months - возраст в мес.
        description - описание котенка
        breed - id породы
        owner - id владельца
    """
    def post(self, request):
        kitten_id = request.data.get('kitten_id')
        if not kitten_id:
            return Response({"error": "Необходим параметр 'kitten_id'"}, status=status.HTTP_400_BAD_REQUEST)
        
        kitten = models.Kitten.objects.filter(id=kitten_id)
        if not kitten.exists():
            return Response({"message": "Котёнок не найден."}, status=status.HTTP_404_NOT_FOUND)

        serializer = serializers.DetailedKittenSerializer(kitten.first())
        return Response(serializer.data, status=status.HTTP_200_OK)


class KittenManageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Создание нового котенка

        Методы

        POST
        Создает нового котенка.

        **Заголовки:**
        - `Authorization` (string, обязательный): JWT токен в формате `Bearer <токен>`.

        Параметры:
        - `name` (str): Имя котенка
        - `color` (str): Цвет котенка.
        - `age_in_months` (str): Возраст котенка в мес.
        - `description` (str): Описание котенка.
        - `breed` (int): id породы.

        Пример запроса:
        ```
        POST /api/kittenmanage
        {
            "name": "Супер-кот",
            "color": "Белый",
            "age_in_months": 12,
            "description": "Красивый белый кот",
            "breed": 1
        }
        ```

        Пример ответа:
        ```
        {
            "id": 12,
            "name": "Супер-кот",
            "color": "Белый",
            "age_in_months": 12,
            "description": "Красивый белый кот",
            "breed": 1,
            "owner": 2
        }
        ```
        """
        serializer = serializers.DetailedKittenSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """
        Изменение информации о котенке

        Методы

        PUT
        Изменение информации о котенке

        **Заголовки:**
        - `Authorization` (string, обязательный): JWT токен в формате `Bearer <токен>`.

        Параметры:
        - `kitten_id` (int): id котенка
        - `name` (str): Имя котенка (Опционально)
        - `color` (str): Цвет котенка. (Опционально)
        - `age_in_months` (str): Возраст котенка в мес. (Опционально)
        - `description` (str): Описание котенка. (Опционально)
        - `breed` (int): id породы. (Опционально)
        
        Пример запроса:
        ```
        PUT /api/kittenmanage
        {
            "kitten_id": 12,
            "name": "Супер-кот",
            "color": "Белый",
            "age_in_months": 12,
            "description": "Красивый белый кот",
            "breed": 1
        }
        ```

        Пример ответа:
        ```
        {
            "id": 12,
            "name": "Супер-кот",
            "color": "Белый",
            "age_in_months": 12,
            "description": "Красивый белый кот",
            "breed": 1,
            "owner": 2
        }
        ```
        """
        kitten_id = request.data.get('kitten_id')
        if not kitten_id:
            return Response({"error": "Необходим параметр 'kitten_id'"}, status=status.HTTP_400_BAD_REQUEST)
        
        kitten = get_object_or_404(models.Kitten, id=kitten_id, owner=request.user)
        serializer = serializers.DetailedKittenSerializer(kitten, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """
        Изменение информации о котенке

        Методы
        
        DELETE
        Изменение информации о котенке

        **Заголовки:**
        - `Authorization` (string, обязательный): JWT токен в формате `Bearer <токен>`.

        Параметры:
        - `kitten_id` (int): id котенка

        Пример запроса:
        ```
        DELETE /api/kittenmanage
        {
            "kitten_id": 12,
        }
        ```

        Пример ответа:
        ```
        {
            "message": "Котёнок успешно удален."
        }
        ```
        """
        kitten_id = request.data.get('kitten_id')
        if not kitten_id:
            return Response({"error": "Необходим параметр 'kitten_id'"}, status=status.HTTP_400_BAD_REQUEST)
        
        kitten = get_object_or_404(models.Kitten, id=kitten_id, owner=request.user)
        kitten.delete()
        return Response({"message": "Котёнок успешно удален."}, status=status.HTTP_204_NO_CONTENT)
    

User = get_user_model()

class RegisterAPIView(APIView):
    """
    Регистрация нового пользователя.

    Данный API позволяет пользователям регистрироваться в системе, предоставляя имя пользователя и пароль.

    ## Методы

    ### POST
    Регистрирует нового пользователя.

    **Параметры:**
    - `username` (str, обязательный): Имя пользователя. Должно быть уникальным и не пустым.
    - `password` (str, обязательный): Пароль пользователя. Должен содержать хотя бы один символ.

    **Возвращает:**
    - **201 Created**: Успешно зарегистрированный пользователь с токенами доступа.
    - **400 Bad Request**: 
        - Если отсутствует параметр `username`:
            ```json
            {
                "error": "Необходим параметр 'username'"
            }
            ```
        - Если отсутствует параметр `password`:
            ```json
            {
                "error": "Необходим параметр 'password'"
            }
            ```
        - Если пользователь с таким именем уже существует:
            ```json
            {
                "error": "Пользователь с таким именем уже существует."
            }
            ```

    **Пример запроса:**
    ```
    POST /api/register
    {
        "username": "new_user",
        "password": "securepassword123"
    }
    ```

    **Пример успешного ответа:**
    ```
    {
        "refresh": "refresh_token_value",
        "access": "access_token_value"
    }
    ```

    **Примечания:**
    - Пароль перед сохранением будет хешироваться для обеспечения безопасности.
    - Пользовательский токен доступа и токен обновления будут возвращены в ответе при успешной регистрации.
    """
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username:
            return Response({"error": "Необходим параметр 'username'"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not password:
            return Response({"error": "Необходим параметр 'password'"}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(username=username).exists():
            return Response({"error": "Пользователь с таким именем уже существует."}, status=status.HTTP_400_BAD_REQUEST)

        user = User(
            username=username,
            password=make_password(password),
        )
        user.save()

        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
    

class RateKittenAPIView(APIView):
    """
    Оценка котёнка.

    Данный API позволяет авторизованным пользователям оценивать котят по шкале от 1 до 5.

    ## Методы

    ### POST
    Добавляет или обновляет оценку для указанного котёнка.
    
    **Заголовки:**
        - `Authorization` (string, обязательный): JWT токен в формате `Bearer <токен>`.

    **Параметры:**
    - `kitten_id` (int, обязательный): Идентификатор котёнка, который необходимо оценить.
    - `rating_value` (int, обязательный): Оценка котёнка, должна находиться в пределах от 1 до 5.

    **Возвращает:**
    - **201 Created**: Успешно добавленная оценка.
    - **200 OK**: Успешно обновлённая оценка.
    - **400 Bad Request**: 
        - Если отсутствует параметр `kitten_id`:
            ```json
            {
                "error": "Необходим параметр 'kitten_id'"
            }
            ```
        - Если отсутствует параметр `rating_value`:
            ```json
            {
                "error": "Необходим параметр 'rating_value'"
            }
            ```
        - Если оценка находится вне допустимого диапазона:
            ```json
            {
                "error": "Оценка должна быть в пределах от 1 до 5"
            }
            ```
    - **404 Not Found**: Если котёнок с указанным идентификатором не найден.

    **Пример запроса:**
    ```
    POST /api/ratekitten
    {
        "kitten_id": 1,
        "rating_value": 5
    }
    ```

    **Пример успешного ответа (добавление новой оценки):**
    ```
    {
        "message": "Оценка успешно добавлена."
    }
    ```

    **Пример успешного ответа (обновление существующей оценки):**
    ```
    {
        "message": "Оценка обновлена."
    }
    ```

    **Примечания:**
    - Доступ к этому API возможен только для авторизованных пользователей.
    - Пользователи могут оценивать одного котёнка только один раз. Если оценка уже существует, она будет обновлена.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        kitten_id = request.data.get('kitten_id')
        rating_value = request.data.get('rating_value')

        if not kitten_id:
            return Response({"error": "Необходим параметр 'kitten_id'"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not rating_value:
            return Response({"error": "Необходим параметр 'rating_value'"}, status=status.HTTP_400_BAD_REQUEST)

        if not (1 <= rating_value <= 5):
            return Response({"error": "Оценка должна быть в пределах от 1 до 5"}, status=status.HTTP_400_BAD_REQUEST)

        kitten = get_object_or_404(models.Kitten, id=kitten_id)

        existing_rating = models.Rating.objects.filter(kitten=kitten, user=request.user).first()

        if existing_rating:
            existing_rating.rating = rating_value
            existing_rating.save()
            return Response({"message": "Оценка обновлена."}, status=status.HTTP_200_OK)

        models.Rating.objects.create(kitten=kitten, user=request.user, rating=rating_value)

        return Response({"message": "Оценка успешно добавлена."}, status=status.HTTP_201_CREATED)
