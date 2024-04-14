from django.urls import path
from .views import *

urlpatterns = [
    path('insertAnimals', InsertAnimalsAPI.as_view()),
    path('uploadImage', UploadImageAPI.as_view()),
    path('getImage', GetImageAPI.as_view()),
    path('uploadVideo', UploadVideoAPI.as_view()),
    path('getVideo', GetVideoAPI.as_view()),
    path('uploadArticle', UploadArticleAPI.as_view()),
    path('getArticle', GetArticleAPI.as_view()),
    path('register', RegisterViewAPI.as_view()),
    path('login', LoginViewAPI.as_view()),
    path('isAuth', isAuthAPI.as_view()),
    path('logout', LogoutView.as_view()),
    path('search', SearchAPI.as_view()),
    # path('insertTag', InsertTag.as_view())
]
