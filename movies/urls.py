from .views import register, create_review, MovieListAPIView, MovieDetailAPIView, GenreListAPIView, login_api, logout_api, home, movie_detail, add_movie, register_page, login_page, logout_page, add_review, delete_review, edit_review, profile
from django.urls import path

urlpatterns = [
    path('', home, name='home'),
    path('movies/<int:pk>/', movie_detail, name='movie-detail-page'),
    path('movies/add/', add_movie, name='movie-add'),
    path('movies/<int:pk>/review/', add_review, name='add-review'),
    path('register/', register_page, name='register-page'),
    path('login/', login_page, name='login-page'),
    path('logout/', logout_page, name='logout-page'),
    path('reviews/<int:pk>/delete/', delete_review, name='delete-review'),
    path('reviews/<int:pk>/edit/', edit_review, name='edit-review'),
    path("profile/", profile, name="profile"),

    path('api/register/', register, name='register'),
    path('api/login/', login_api, name='login'),
    path('api/logout/', logout_api, name='logout'),
    path('api/movies/', MovieListAPIView.as_view(), name='movie-list'),
    path('api/movies/<int:pk>/', MovieDetailAPIView.as_view(), name='movie-detail'),
    path('api/genres/', GenreListAPIView.as_view(), name='genre-list'),
    path('api/reviews/', create_review, name='create-review'),
]