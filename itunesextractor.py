from functions import media_mode, itunes_search, get_movie_information, imdb_search, get_imdb_movie_information, get_tv_show_information
mode = ""
search_terms = []
entity = ""
print("Welcome to the iTunesMediaExtractor")
print("Made by Carlos Martinez")
mode = media_mode()
if (mode == "1"):
    entity = "movie"
    itunes_search(mode, entity)
    get_movie_information()
elif (mode == "2"):
    imdb_search("sourceimdb")
    get_imdb_movie_information()
elif (mode == "3"):
    entity="tvSeason"
    itunes_search(mode, entity)
    get_tv_show_information()



