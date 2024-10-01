from django.urls import path, include
from kittens import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('register', view=views.RegisterAPIView.as_view(), name='register'),
    path('token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token_refresh', TokenRefreshView.as_view(), name='token_refresh'),

    path('breedlist', view=views.BreedListAPIView.as_view(), name='breedlist'),
    path('kittenlist', view=views.KittenListAPIView.as_view(), name='kittenlist'),
    path('kittenbybreed', view=views.KittenByBreedListAPIView.as_view(), name='kittenbybreed'),
    path('kittendetail', view=views.KittenDetailAPIView.as_view(), name='kittendetail'),
    path('kittenmanage', view=views.KittenManageAPIView.as_view(), name='kittenmanage'),
    path('ratekitten', view=views.RateKittenAPIView.as_view(), name='ratekitten'),
]