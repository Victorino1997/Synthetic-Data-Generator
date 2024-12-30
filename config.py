import yaml


class Config:
    def __init__(self, config_file_path):
        self.config = self.load_config(config_file_path)

        self.users_rate = self.config["users_rate"]
        self.artists_rate = self.config["artists_rate"]
        self.WEEKS_NUM = self.config["WEEKS_NUM"]
        self.frequencies_genre = self.config["frequencies_genre"]
        self.frequencies_continent = self.config["frequencies_continent"]

        self.p_favorite = self.config["p_favorite"]
        self.p_favorite_playlist = self.config["p_favorite_playlist"]
        self.p_random_songs_stream = self.config["p_random_songs_stream"]
        self.avg_songs_unsub = self.config["avg_songs_unsub"]
        self.avg_songs_sub = self.config["avg_songs_sub"]
        self.p_fav_art_sng_gnr_cnt = self.config["p_fav_art_sng_gnr_cnt"]
        self.p_fav_art_sng_gnr = self.config["p_fav_art_sng_gnr"]
        self.p_fav_gnr = self.config["p_fav_gnr"]
        self.p_other = self.config["p_other"]
        self.min_streams_to_favorites = self.config["min_streams_to_favorites"]
        self.min_streams_to_famous_song = self.config["min_streams_to_famous_song"]
        self.min_streams_to_famous_artist = self.config["min_streams_to_famous_artist"]
        self.p_is_song_premium = self.config["p_is_song_premium"]
        self.P_is_artist_famous = self.config["P_is_artist_famous"]
        self.p_is_user_subscribed = self.config["p_is_user_subscribed"]

    def load_config(self, config_file_path):
        with open(config_file_path, "r") as fh:
            return yaml.load(fh, Loader=yaml.FullLoader)
