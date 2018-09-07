META_DATA = {
    "genre" : 44,
    "character" : 100,
    "time" : 10,
    "studio" : 10,
    "staff" : 50,
    "user" : 6,
    "topic" : 50,
    "full_feature_size" : 485
}

user_genres_column = list(map(lambda x: 'u_genre_'+str(x),range(META_DATA["genre"])))
user_characters_column = list(map(lambda x: 'u_character_'+str(x),range(META_DATA["character"])))
user_staffs_column = list(map(lambda x: 'u_staff_'+str(x),range(META_DATA["staff"])))
user_studios_column = list(map(lambda x: 'u_studio_'+str(x),range(META_DATA["studio"])))
user_times_column = list(map(lambda x: 'u_time_'+str(x),range(META_DATA["time"])))
user_column = list(map(lambda x: 'u_'+str(x),range(META_DATA["user"])))

anime_genres_column = list(map(lambda x: 'a_genre_'+str(x),range(META_DATA["genre"])))
anime_characters_column = list(map(lambda x: 'a_character_'+str(x),range(META_DATA["character"])))
anime_staffs_column = list(map(lambda x: 'a_staff_'+str(x),range(META_DATA["staff"])))
anime_studios_column = list(map(lambda x: 'a_studio_'+str(x),range(META_DATA["studio"])))
anime_times_column = list(map(lambda x: 'a_time_'+str(x),range(META_DATA["time"])))
animes_topic_column = list(map(lambda x: 'a_topic_'+str(x),range(META_DATA["topic"])))

column = user_genres_column + user_characters_column + user_staffs_column + user_studios_column + user_times_column + user_column + anime_genres_column + anime_characters_column + anime_staffs_column + anime_studios_column + anime_times_column + animes_topic_column