from .models import Movie, Review

def site_statistics(request):
    return {
        "movie_count": Movie.objects.count(),
        "review_count": Review.objects.count(),
    }