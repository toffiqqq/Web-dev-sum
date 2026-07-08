from .models import Movie, Review, Genre

def site_statistics(request):
    return {
        "movie_count": Movie.objects.count(),
        "review_count": Review.objects.count(),
        "genres": Genre.objects.all(),
    }