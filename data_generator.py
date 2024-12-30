import random
from pathlib import Path

import faker
import numpy as np
import pandas as pd

from artist import Artist
from config import Config
from song import Song
from stream import Stream
from user import User
from utils import _rand_bool

DATA_PATH = Path("data")
DATA_PATH.mkdir(exist_ok=True)


class SyntheticStreamingDataGenerator:
    def __init__(self, config_file_path):
        super().__init__()
        self.config = Config(config_file_path)
        self.fake = faker.Faker()
        self.user_list = []
        self.artist_list = []
        self.song_list = []
        self.stream_list = []
        self.user_fav_genre = []
        self.user_fav_artist = []
        self.user_fav_song = []

        self.config.users_number = self.config.users_rate
        self.config.artists_number = self.config.artists_rate
        self.config.WEEKS_NUM = self.config.WEEKS_NUM

        frequencies_genre_df = pd.DataFrame(self.config.frequencies_genre).T
        self.probabilities_genre_df = frequencies_genre_df / frequencies_genre_df.sum()
        frequencies_continent_df = pd.DataFrame(self.config.frequencies_continent).T
        self.probabilities_continent_df = (
                frequencies_continent_df / frequencies_continent_df.sum()
        )

    def run(self):
        for week_no in range(self.config.WEEKS_NUM):
            self.create_artists(week_no)
            self.generate_songs(week_no)
            self.create_users(week_no)
            self.generate_streams(week_no)

        self.generate_additional_tables()
        users_df = pd.DataFrame([vars(u) for u in self.user_list])
        users_df.drop(
            columns=[
                "favorite_genres",
                "favorite_artists",
                "favorite_songs",
                "streams",
            ],
            inplace=True,
        )
        artist_df = pd.DataFrame([vars(a) for a in self.artist_list])
        song_df = pd.DataFrame([vars(s) for s in self.song_list])
        stream_df = pd.DataFrame([vars(s) for s in self.stream_list])
        users_df.to_csv(DATA_PATH / "users.csv", index=False)
        artist_df.to_csv(DATA_PATH / "artists.csv", index=False)
        song_df.to_csv(DATA_PATH / "songs.csv", index=False)
        stream_df.to_csv(DATA_PATH / "streams.csv", index=False)

    def create_users(self, week_no):

        num_users_to_add = self.count_amount(self.config.users_number, week_no)

        for _ in range(num_users_to_add):
            user = User(
                user_id=len(self.user_list),
                week_no=week_no,
                probabilities_continent_df=self.probabilities_continent_df,
                probabilities_genre_df=self.probabilities_genre_df,
                artist_list=self.artist_list,
                song_list=self.song_list,
                p_is_user_subscribed=self.config.p_is_user_subscribed
            )
            self.user_list.append(user)

    def create_artists(self, week_no):
        num_artists_to_add = self.count_amount(self.config.artists_number, week_no)

        for i in range(num_artists_to_add):
            artist = Artist(
                artist_id=len(self.artist_list),
                continent=np.random.choice(
                    a=self.probabilities_continent_df.index.to_list(),
                    p=self.probabilities_continent_df.artist.to_list(),
                ),
                genre=np.random.choice(
                    a=self.probabilities_genre_df.index.to_list(),
                    p=self.probabilities_genre_df.artist.to_list(),
                ),
                is_famous=_rand_bool(0.1),
                number_of_streams=0,
                week_no_created=week_no,
            )
            self.artist_list.append(artist)

    def generate_songs(self, week_no):
        assert (
            self.artist_list
        ), "artist_list is empty"  # It checks whether the list is empty
        for artist in self.artist_list:
            # Artist is generating songs every few weeks,
            if _rand_bool(0.25):
                song = Song(
                    song_id=len(self.song_list),
                    artist_id=artist.artist_id,
                    genre=artist.genre,
                    is_artist_famous=artist.is_famous,
                    is_premium=_rand_bool(self.config.p_is_song_premium),
                    is_famous=_rand_bool(self.config.P_is_artist_famous) if artist.is_famous else _rand_bool(0.1),
                    week_released=week_no,
                    number_of_streams=0,
                )
                self.song_list.append(song)

    def generate_streams(self, week_no):
        assert (
            self.user_list
        ), "user_list is empty"  # It checks whether the list is empty
        premium_songs = [
            song for song in self.song_list if song.is_premium
        ]  # create a list of premium songs

        for user_i in range(len(self.user_list)):
            # count number of songs users goes through (not necessarily listen)
            list_songs = self.song_list
            n_songs = len(self.song_list)

            if (
                    self.user_list[user_i].is_subscribed
                    and len(self.song_list) > self.config.avg_songs_sub
            ):
                n_songs = random.randrange(
                    self.config.avg_songs_sub - int(0.5 * self.config.avg_songs_sub),
                    self.config.avg_songs_sub + int(0.5 * self.config.avg_songs_sub),
                )

            elif (
                    not self.user_list[user_i].is_subscribed
                    and len(premium_songs) < self.config.avg_songs_unsub
            ):
                list_songs = premium_songs
                n_songs = len(premium_songs)

            elif (
                    not self.user_list[user_i].is_subscribed
                    and len(premium_songs) > self.config.avg_songs_unsub
            ):
                list_songs = premium_songs
                n_songs = random.randrange(
                    self.config.avg_songs_unsub
                    - int(0.5 * self.config.avg_songs_unsub),
                    self.config.avg_songs_unsub
                    + int(0.5 * self.config.avg_songs_unsub),
                )

            # Random songs outside user's favorites
            if (
                    random.uniform(0, 1) < self.config.p_random_songs_stream and list_songs
            ):  # check if user will access the random songs
                for _ in range(int(n_songs)):  # go through songs
                    random_song = random.choice(list_songs)  # choose random song

                    # if singer is famous, song is famous, same genre, same continent
                    if (
                            (self.artist_list[random_song.artist_id].is_famous)
                            and (random_song.is_famous)
                            and (
                            random_song.genre in self.user_list[user_i].favorite_genres
                    )
                            and (
                            self.artist_list[random_song.artist_id].continent
                            == self.user_list[user_i].continent
                    )
                            and random.uniform(0, 1) < self.config.p_fav_art_sng_gnr_cnt
                    ):
                        user = self.add_stream(
                            self.user_list[user_i], random_song.song_id, week_no
                        )
                        self.user_list[user_i] = user

                    # if singer is famous, song is famous, same genre
                    elif (
                            self.artist_list[random_song.artist_id].is_famous
                            and random_song.is_famous
                            and (
                                    random_song.genre in self.user_list[user_i].favorite_genres
                            )
                            and random.uniform(0, 1) < self.config.p_fav_art_sng_gnr
                    ):
                        user = self.add_stream(
                            self.user_list[user_i], random_song.song_id, week_no
                        )
                        self.user_list[user_i] = user

                    # if  same genre
                    elif (
                            random_song.genre in self.user_list[user_i].favorite_genres
                    ) and random.uniform(0, 1) < self.config.p_fav_gnr:
                        user = self.add_stream(
                            self.user_list[user_i], random_song.song_id, week_no
                        )
                        self.user_list[user_i] = user

                    elif random.uniform(0, 1) < self.config.p_other:
                        user = self.add_stream(
                            self.user_list[user_i], random_song.song_id, week_no
                        )
                        self.user_list[user_i] = user

            if (
                    random.uniform(0, 1) < self.config.p_favorite_playlist
                    and self.user_list[user_i].favorite_songs
            ):  # check if user will access favorite_songs
                list_songs = self.user_list[user_i].favorite_songs
                if len(list_songs) > 1:
                    n_songs = random.randrange(
                        len(list_songs) - int(0.5 * len(list_songs)),
                        len(list_songs) + int(0.5 * len(list_songs)),
                    )
                else:
                    n_songs = len(list_songs)

                for _ in range(int(n_songs)):
                    if random.uniform(0, 1) < self.config.p_favorite:
                        user = self.add_stream(
                            self.user_list[user_i], random.choice(list_songs), week_no
                        )
                        self.user_list[user_i] = user

    def add_stream(self, user, i, week_no):
        stream = Stream(
            stream_id=len(self.stream_list),
            user_id=user.user_id,
            song_id=i,
            week_no=week_no,
        )
        # tracking how many times user listened to particular song and checking if users should add song to favorites
        if i in user.streams:
            user.streams[i] += 1
        else:
            user.streams[i] = 1

        if user.streams[i] > self.config.min_streams_to_favorites:
            user.favorite_songs.append(i)
            user.favorite_songs = list(
                dict.fromkeys(user.favorite_songs)
            )

        # tracking number of streams for each song and checking if to add to favorites
        self.song_list[i].number_of_streams += 1

        if self.song_list[i].number_of_streams > self.config.min_streams_to_famous_song:
            self.song_list[i].is_famous = True

        # tracking number of streams for each artist and checking if to make famous
        self.artist_list[self.song_list[i].artist_id].number_of_streams += 1

        if (
                self.artist_list[self.song_list[i].artist_id].number_of_streams
                > self.config.min_streams_to_famous_artist
        ):
            self.artist_list[self.song_list[i].artist_id].is_famous = True

        self.stream_list.append(stream)
        return user

    def generate_additional_tables(self):
        # generate users_favorite_genres table
        for user in self.user_list:
            for genre in user.favorite_genres:
                row = {"user_id": user.user_id, "genre_id": genre}
                self.user_fav_genre.append(row)

        users_fav_genre_df = pd.DataFrame(self.user_fav_genre)
        users_fav_genre_df.to_csv(DATA_PATH / "users_favorite_genre.csv", index=False)

        # generate users_favorite_artist table
        for user in self.user_list:
            for artist in user.favorite_artists:
                row = {"user_id": user.user_id, "artist_id": artist}
                self.user_fav_artist.append(row)

        users_fav_artist_df = pd.DataFrame(self.user_fav_artist)
        users_fav_artist_df.to_csv(DATA_PATH / "users_favorite_artist.csv", index=False)

        # generate users_favorite_song table
        for user in self.user_list:
            for song in user.favorite_songs:
                row = {"user_id": user.user_id, "song_id": song}
                self.user_fav_song.append(row)

        users_fav_song_df = pd.DataFrame(self.user_fav_song)
        users_fav_song_df.to_csv(DATA_PATH / "users_favorite_song.csv", index=False)

    def count_amount(self, number, week_no):

        return round(
            (11.17315 + 0.3660266 * week_no + 0.009279995 * week_no ** 2)
            * (number / 5976.23302825))

if __name__ == "__main__":
    generator = SyntheticStreamingDataGenerator(config_file_path="config_music.yaml")
    generator.run()
