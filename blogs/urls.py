from django.urls import path
from .views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

urlpatterns = [

    path('register/',UserResgistration.as_view(),name = "registration"),
    path('login/',UserLogin.as_view(),name='login'),
    path('refresh/', TokenRefreshView.as_view(),name='token_refresh'),
    path('logout/',UserLogout.as_view(),name='logout'),
    path("create/blog",PostBlog.as_view(),name="blogs"),
    path("like/<int:pk>",BlogLikes.as_view(),name="blogs_likes"),
    path("answer/blog/<int:pk>",BlogAnswer.as_view(),name="blogs_answer"),
    
   
    


]