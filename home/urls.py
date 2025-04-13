from django.urls import path, include
from .views import index, login, logout, callback, trans_web, download

urlpatterns = [
    path('', index, name='index'),
    path("login", login, name="login"),
    path("logout", logout, name="logout"),
    path("callback", callback, name="callback"),
    path("trans-web", trans_web, name='trans_web'),
    path("download", download, name='download')
]
