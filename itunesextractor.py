from process import Process

def main():
    """Main function which calls all other functions."""
    print("Welcome to the iTunesMediaExtractor")
    print("Made by Carlos Martinez")
    process = Process()
    mode = process.media_mode()
    if (mode == "1"):
        entity = "movie"
        process.itunes_search(mode, entity)
        process.get_movie_information()
    elif (mode == "2"):
        process.imdb_search("sourceimdb")
        process.get_imdb_movie_information()
    elif (mode == "3"):
        entity = "tvSeason"
        process.itunes_search(mode, entity)
        process.get_tv_show_information()


if __name__ == "__main__":
    main()