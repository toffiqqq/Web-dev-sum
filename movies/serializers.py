from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Movie, Genre, Review, Profile

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'
        read_only_fields = ['user']

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.username", read_only=True)
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ['user', 'created_at']

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        return User.objects.create_user(username=validated_data['username'], password=validated_data['password'])

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class ReviewCreateSerializer(serializers.Serializer):
    movie_id = serializers.IntegerField()
    text = serializers.CharField()
    rating = serializers.IntegerField(min_value=0, max_value=10)

    def validate_movie_id(self, value):
        if not Movie.objects.filter(id=value).exists():
            raise serializers.ValidationError("Movie not found")
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        movie = Movie.objects.get(id=validated_data['movie_id'])
        return Review.objects.create(movie=movie, user=request.user, text=validated_data['text'], rating=validated_data['rating'])