from django.urls import path, re_path
from .views import index

urlpatterns = [
    # path("", index),
    # path("signin", index),
    # path("signup", index),
    # path("explore", index),
    # path("contribute", index),
    # path("explore/<str:id>", index),
    # path("about", index),
    # path("contact", index),

    # path("profile/<str:id>", index),
    # path("edit/<str:id>", index),
    re_path(r'.*', index)
]
