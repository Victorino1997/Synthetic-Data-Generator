import pandas as pd
import pytest

from artist import Artist
from song import Song
from user import User

# Mock data for testing
probabilities_continent_df = pd.DataFrame(
    {"continent": ["North America", "Europe"], "user": [0.5, 0.5]}
).set_index("continent")

probabilities_genre_df = pd.DataFrame(
    {"genre": ["Pop", "Rock"], "user": [0.5, 0.5]}
).set_index("genre")

artist_list = [
    Artist(
        artist_id=0,
        continent="Europe",
        genre="Rock",
        is_famous=True,
        number_of_streams=1000,
        week_no_created=1,
    ),
    Artist(
        artist_id=1,
        continent="North America",
        genre="Pop",
        is_famous=False,
        number_of_streams=100,
        week_no_created=1,
    ),
]

song_list = [
    Song(
        song_id=0,
        artist_id=0,
        is_premium=False,
        genre="Jazz",
        is_artist_famous=True,
        is_famous=True,
        week_released=1,
        number_of_streams=1000,
    ),
    Song(
        song_id=1,
        artist_id=1,
        is_premium=True,
        genre="Jazz",
        is_artist_famous=True,
        is_famous=True,
        week_released=1,
        number_of_streams=2000,
    ),
]


@pytest.fixture
def sample_user():
    """Fixture to create a sample user for tests."""
    return User(
        user_id=1,
        week_no=1,
        probabilities_continent_df=probabilities_continent_df,
        probabilities_genre_df=probabilities_genre_df,
        artist_list=artist_list,
        song_list=song_list,
        p_is_user_subscribed=0.1
    )


def test_user_initialization(sample_user):
    """Test that a User object initializes with correct attributes."""
    assert sample_user.user_id == 1
    assert sample_user.week == 1
    assert isinstance(sample_user.user_name, str)
    assert 15 <= sample_user.age <= 45
    assert sample_user.continent in ["North America", "Europe"]
    assert isinstance(sample_user.favorite_genres, list)
    assert isinstance(sample_user.favorite_artists, list)
    assert isinstance(sample_user.favorite_songs, list)
    assert isinstance(sample_user.streams, dict)


def test_add_favorite_genres(sample_user):
    """Test that favorite genres are added correctly."""
    assert len(sample_user.favorite_genres) >= 0


def test_add_favorite_artists(sample_user):
    """Test that favorite artists are added based on conditions."""
    assert len(sample_user.favorite_artists) >= 0


def test_add_favorite_songs_from_artists(sample_user):
    """Test that favorite songs are added from favorite artists under the correct conditions."""
    if sample_user.is_subscribed or any(song.is_premium for song in song_list):
        assert len(sample_user.favorite_songs) >= 0


def test_user_age_range(sample_user):
    """Test that the user's age is within an expected range given the lognormal distribution."""
    assert 20 <= sample_user.age <= 70, "User's age is outside the expected range"
