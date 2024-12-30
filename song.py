class Song:
    def __init__(
        self,
        song_id,
        artist_id,
        genre,
        is_artist_famous,
        is_premium,
        is_famous,
        week_released,
        number_of_streams,
    ):
        self.song_id = song_id
        self.artist_id = artist_id
        self.genre = genre
        self.is_artist_famous = is_artist_famous
        self.is_premium = is_premium
        self.is_famous = is_famous
        self.week_released = week_released
        self.number_of_streams = number_of_streams
