import random

import numpy as np
from faker import Faker

from utils import _rand_bool

fake = Faker()


class User:
    def __init__(
        self,
        user_id,
        week_no,
        probabilities_continent_df,
        probabilities_genre_df,
        artist_list,
        song_list,
        p_is_user_subscribed
    ):
        self.user_id = user_id
        self.user_name = fake.name()
        self.age = int(((np.random.lognormal(mean=1, sigma=0.1, size=1)) * 20 - 25)[0])
        self.continent = np.random.choice(
            a=probabilities_continent_df.index.to_list(),
            p=probabilities_continent_df.user.to_list(),
        )
        self.favorite_genres = []
        self.favorite_artists = []
        self.favorite_songs = []
        self.streams = {}
        self.is_subscribed = _rand_bool(p_is_user_subscribed)
        self.week = week_no

        self._add_favorite_genres(probabilities_genre_df)
        self._add_favorite_artists(artist_list)
        self._add_favorite_songs(song_list)

    def _add_favorite_genres(self, probabilities_genre_df):
        for _ in range(int(np.random.choice([0, 1, 2, 3], p=[0.2, 0.4, 0.3, 0.1]))):
            self.favorite_genres.append(
                np.random.choice(
                    a=probabilities_genre_df.index.to_list(),
                    p=probabilities_genre_df.user.to_list(),
                )
            )
        self.favorite_genres = list(dict.fromkeys(self.favorite_genres))

    def _add_favorite_artists(self, artist_list):
        to_add = False
        for _ in range(random.randrange(5)):
            for _ in range(20):
                chosen_artist = random.choice(artist_list)
                if (
                    chosen_artist.continent == self.continent
                    and chosen_artist.genre in self.favorite_genres
                    and chosen_artist.is_famous
                    and random.uniform(0, 1) < 0.7
                ):
                    to_add = True
                    break
                elif (
                    chosen_artist.continent == self.continent
                    and chosen_artist.genre in self.favorite_genres
                    and random.uniform(0, 1) < 0.4
                ):
                    to_add = True
                    break
                elif (
                    chosen_artist.genre in self.favorite_genres
                    and chosen_artist.is_famous
                    and random.uniform(0, 1) < 0.4
                ):
                    to_add = True
                    break
                elif random.uniform(0, 1) < 0.05:
                    to_add = True
                    break

            if to_add:
                self.favorite_artists.append(chosen_artist.artist_id)
            to_add = False

        self.favorite_artists = list(dict.fromkeys(self.favorite_artists))

    def _add_favorite_songs(self, song_list):
        for artist_id in self.favorite_artists:
            favorite_artist_songs = [
                song for song in song_list if song.artist_id == artist_id
            ]

            for song in favorite_artist_songs:
                if random.uniform(0, 1) < 0.7 and self.is_subscribed:
                    self.favorite_songs.append(song.song_id)

                if (
                    random.uniform(0, 1) < 0.7
                    and not self.is_subscribed
                    and song.is_premium
                ):
                    self.favorite_songs.append(song.song_id)

        for _ in range(15):
            if song_list:
                random_song = random.choice(song_list)
                if random.uniform(0, 1) < 0.1:
                    self.favorite_songs.append(random_song.song_id)

        self.favorite_songs = list(dict.fromkeys(self.favorite_songs))
