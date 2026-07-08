from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Avg, FloatField
from django.db.models.functions import Coalesce
from .models import Movie, Genre, Review
from .serializers import GenreSerializer, MovieSerializer, RegisterSerializer, LoginSerializer, ReviewCreateSerializer
from .forms import MovieForm, RegisterForm, ReviewForm

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "username": user.username,},status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_review(request):
    serializer = ReviewCreateSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        review = serializer.save()
        return Response({"message": "Review created", "id": review.id,}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MovieListAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        movies = Movie.objects.all()
        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = MovieSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class MovieDetailAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(Movie, pk=pk)

    def get(self, request, pk):
        movie = self.get_object(pk)
        serializer = MovieSerializer(movie)
        return Response(serializer.data)

    def put(self, request, pk):
        movie = self.get_object(pk)

        serializer = MovieSerializer(movie, data=request.data)

        if serializer.is_valid():
            serializer.save(user=movie.user)
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        movie = self.get_object(pk)
        movie.delete()

        return Response({"message": "Movie deleted"}, status=status.HTTP_204_NO_CONTENT)

@api_view(["POST"])
@permission_classes([AllowAny])
def login_api(request):
    serializer = LoginSerializer(data=request.data)

    if serializer.is_valid():
        user = authenticate(username=serializer.validated_data["username"], password=serializer.validated_data["password"])

        if user is None:
            return Response({"error": "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)

        token, created = Token.objects.get_or_create(user=user)

        return Response({"token": token.key, "username": user.username})

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_api(request):
    request.user.auth_token.delete()
    return Response({"message": "Successfully logged out"})

class GenreListAPIView(APIView):

    def get(self, request):
        genres = Genre.objects.all()
        serializer = GenreSerializer(genres, many=True)
        return Response(serializer.data)

def home(request):
    movies = Movie.objects.annotate(avg_rating=Coalesce(Avg("reviews__rating"), 0.0, output_field=FloatField(),))
    genre_id = request.GET.get("genre")
    if genre_id:
        movies = movies.filter(genre_id=genre_id)
    rating = request.GET.get("rating")
    if rating:
        movies = movies.filter(avg_rating__gte=float(rating))
    genres = Genre.objects.all()
    return render(request, "movies/home.html", {"movies": movies, "genres": genres, "ratings": range(9, -1, -1), "selected_genre": genre_id, "selected_rating": rating})

def movie_detail(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    avg_rating = movie.reviews.aggregate(Avg('rating'))['rating__avg'] 
    return render(request, 'movies/movie_detail.html', {'movie': movie, 'avg_rating': avg_rating})

@login_required
def add_movie(request):
    if request.method == 'POST':
        form = MovieForm(request.POST, request.FILES)
        if form.is_valid():
            movie = form.save(commit=False)
            movie.user = request.user
            movie.save()
            return redirect('home')
    else:
        form = MovieForm()
    return render(request, 'movies/movie_form.html', {'form': form})

def register_page(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})
    
def login_page(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def logout_page(request):
    print("Logout view called")
    logout(request)
    return redirect('home')

@login_required
def add_review(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.movie = movie
            review.user = request.user
            review.save()
            return redirect('movie-detail-page', pk=movie.pk)
    else:
        form = ReviewForm()
    return render(request, 'movies/review_form.html', {'form': form, 'movie': movie})

@login_required
def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk, user=request.user)
    if request.method == 'POST':
        movie_id = review.movie.id
        review.delete()
        return redirect('movie-detail-page', pk=movie_id)

@login_required
def edit_review(request, pk):
    review = get_object_or_404(Review, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('movie-detail-page', pk=review.movie.id)
    else:
        form = ReviewForm(instance=review)
    return render(request, 'movies/review_form.html', {'form': form, 'movie': review.movie,})
