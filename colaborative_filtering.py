import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors


def load_data():
    # Read data from a CSV file into a Pandas DataFrame
    df = pd.read_csv("data/streams.csv")

    # Preprocess user and song IDs by adding prefixes to ensure consistent formatting
    df.user_id = df.user_id.apply(lambda x: "user_" + str(x))
    df.song_id = df.song_id.apply(lambda x: "song_" + str(x))

    # Group data by song and user IDs and calculate the count of streams
    df = df.groupby(["song_id", "user_id"]).agg(stream_count=("stream_id", "count"))


    # Create a pivot table to reshape the data for collaborative filtering and convert to unsigned integers
    df = (
        pd.pivot_table(
            data=df, values="stream_count", index="song_id", columns="user_id"
        )
        .fillna(0)
        .astype(np.uint8)
    )
    return df


# Define a function to recommend songs for a given user
def recommend_songs(user, num_recommended_songs, df_copy, df):
    recommended_songs = []
    # Find songs the user has not streamed and calculate predicted ratings
    for song_id in df[df[user] == 0].index.tolist():
        index_df = df.index.tolist().index(song_id)
        predicted_rating = df_copy.iloc[index_df, df_copy.columns.tolist().index(user)]
        recommended_songs.append((song_id, predicted_rating))

    # Sort recommended songs by predicted rating in descending order
    sorted_rm = sorted(recommended_songs, key=lambda x: x[1], reverse=True)

    recommendations = []
    for recommended_songs in sorted_rm[:num_recommended_songs]:
        # Create a list of recommended songs with their predicted ratings
        recommendations.append(
            {
                "song_id": recommended_songs[0],
                "rating": recommended_songs[1],
            }
        )
    return pd.DataFrame(recommendations)


# Define a song recommender function that uses collaborative filtering
def song_recommender(user, num_neighbors, num_recommendation, df):
    # Create a copy of the original DataFrame
    df1 = df.copy()

    # Create a Nearest Neighbors model with cosine similarity
    knn = NearestNeighbors(metric="cosine", algorithm="brute")
    knn.fit(df.values)
    distances, indices = knn.kneighbors(df.values, n_neighbors=num_neighbors)

    # Find the index of the user in the DataFrame
    user_index = df.columns.tolist().index(user)

    # Loop through each song in the DataFrame
    for song_id, _ in list(enumerate(df.index)):
        # Check if the user has not streamed the song (rating is 0)
        if df.iloc[song_id, user_index] == 0:
            # Get similar songs and their distances
            sim_songs = indices[song_id].tolist()
            songs_distances = distances[song_id].tolist()

            # Remove the current song from the list if it's present
            if song_id in sim_songs:
                indices_song_id = sim_songs.index(song_id)
                sim_songs.remove(song_id)
                songs_distances.pop(indices_song_id)
            else:
                # Limit the number of similar songs to the desired number of neighbors
                sim_songs = sim_songs[: num_neighbors - 1]
                songs_distances = songs_distances[: num_neighbors - 1]

            # Calculate song similarities based on distances
            song_similarity = [1 - x for x in songs_distances]
            song_similarity_copy = song_similarity.copy()
            nominator = 0

            # Calculate the predicted rating for the song
            for s in range(0, len(song_similarity)):
                if df.iloc[sim_songs[s], user_index] == 0:
                    if len(song_similarity_copy) == (num_neighbors - 1):
                        # Remove the first element when reaching the limit
                        song_similarity_copy.pop(s)
                    else:
                        # Remove the first element when the list isn't at its limit
                        song_similarity_copy.pop(
                            s - (len(song_similarity) - len(song_similarity_copy))
                        )
                else:
                    nominator = (
                        nominator
                        + song_similarity[s] * df.iloc[sim_songs[s], user_index]
                    )

            if len(song_similarity_copy) > 0:
                if sum(song_similarity_copy) > 0:
                    # Calculate the predicted rating for the song
                    predicted_r = nominator / sum(song_similarity_copy)
                else:
                    # Set predicted rating to 0 if no valid similarities
                    predicted_r = 0
            else:
                # Set predicted rating to 0 if no valid similarities
                predicted_r = 0

            # Update the predicted rating for the song in the copy of the DataFrame
            df1.iloc[song_id, user_index] = predicted_r

    # Generate song recommendations for the user using the updated DataFrame
    recommendations_df = recommend_songs(user, num_recommendation, df_copy=df1, df=df)
    return recommendations_df




def precision_at_n(recommended_items, relevant_items, n):
    relevant_and_recommended = np.intersect1d(
        recommended_items[:n], relevant_items
    )
    precision = len(relevant_and_recommended) / n
    return precision


def dcg_at_n(recommended_items, relevant_items, n):
    relevances = np.isin(recommended_items[:n], relevant_items).astype(int)
    discounts = np.log2(
        np.arange(len(relevances)) + 2
    )  # +2 because the index starts at 1
    dcg = np.sum(relevances / discounts)
    return dcg


def ndcg_at_n(recommended_items, relevant_items, n):
    relevant_items = relevant_items
    actual_dcg = dcg_at_n(recommended_items, relevant_items, n)
    ideal_dcg = dcg_at_n(sorted(relevant_items, reverse=True), relevant_items, n)
    ndcg = actual_dcg / ideal_dcg if ideal_dcg > 0 else 0
    return ndcg


def evaluate_recommendation(user_id, recommendations_df, n):
    songs_df = pd.read_csv("data/songs.csv")
    users_genre_df = pd.read_csv("data/users_favorite_genre.csv")
    users_artists_df = pd.read_csv("data/users_favorite_artist.csv")
    artists_df = pd.read_csv("data/artists.csv")
    users_df = pd.read_csv("data/users.csv")

    user_id = user_id.replace("user_", "")

    # takes the genres that are favorite for our user
    user_favourite_genres = users_genre_df[
        users_genre_df.user_id == int(user_id)
    ].genre_id.values

    # takes the artists that are favorite for our user
    user_favourite_artist = users_artists_df[
        users_artists_df.user_id == int(user_id)
    ].artist_id.values

    # adds artist country column to song_df
    songs_df = pd.merge(
        songs_df, artists_df[["artist_id", "continent"]], on="artist_id", how="left"
    )

    # Adds a binary column favourite_genre to songs_df, marking 1 for songs that belong to the user's favorite_genres and 0 otherwise.
    songs_df["favourite_genre"] = songs_df.genre.isin(user_favourite_genres).astype(int)

    # Adds a binary column favourite_artist to songs_df, marking 1 for songs by the user's favorite_artists and 0 otherwise.
    songs_df["favourite_artist"] = songs_df.artist_id.isin(
        user_favourite_artist
    ).astype(int)

    # adds a binary column common_continent to songs_df, marking 1 if user and artist have same continent
    songs_df["common_continent"] = (
        songs_df.continent
        == users_df[users_df.user_id == int(user_id)]["continent"].iloc[0]
    ).astype(int)

    del songs_df["continent"]

    # assign a weight for each attribute

    point_columns = {
        "favourite_genre": 1,
        "is_premium": 80,
        "number_of_streams": 1,
        "common_continent": 1,
        "is_famous": 1,
        "is_artist_famous": 1,
        "favourite_artist": 2,
        "week_released": 2,
    }
    # calculate the points for each attribute
    for c, multiplier in point_columns.items():
        songs_df[c + "_points"] = multiplier * songs_df[c] / songs_df[c].sum()
    points_columns = [c + "_points" for c in point_columns]

    average = songs_df[points_columns].sum(axis=1).sort_values(ascending=False).mean()
    benchmark = average - 0 * average
    temp = songs_df[points_columns].sum(axis=1).sort_values(ascending=False)
    # find relevance of the songs by summing all points
    relevant_items = (
        temp[temp > benchmark].index
    )

    recommended_items = (
        recommendations_df.song_id.str.replace("song_", "").astype(int).values
    )

    return ndcg_at_n(recommended_items, relevant_items, n), precision_at_n(recommended_items, relevant_items, n)


# Entry point of the program
if __name__ == "__main__":
    # Call the song_recommender function with specific user, neighbor count, and recommendation count
    df = load_data()
    num_recommendation = 40
    num_neighbors = 8
    num_users = 50

    NDCG_array = []
    PrecisionAtN_array = []
    for user_id in df.columns.tolist()[:num_users]:
        recommendations_df = song_recommender(
            user=user_id,
            num_neighbors=num_neighbors,
            num_recommendation=num_recommendation,
            df=df,
        )
        n = 5
        NDCG_value, PrecisionAtN_value = evaluate_recommendation(
            user_id=user_id,
            recommendations_df=recommendations_df,
            n=n,
        )
        NDCG_array.append(NDCG_value)
        PrecisionAtN_array.append(PrecisionAtN_value)

    print("NDCG: ", sum(NDCG_array) / len(NDCG_array))
    print("Precision@N: ", sum(PrecisionAtN_array) / len(PrecisionAtN_array))
