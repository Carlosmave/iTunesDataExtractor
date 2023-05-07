from config import countries, session, urls, img_urls, api_key, short_descriptions, output
import sys, time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup
import markdown

def movie_mode():
    print("---------------------------------------------------------------------------------------------------")
    print("Choose source:")
    print("1: iTunes and IMDb")
    print("2: Just IMDb")
    try:
        mode = input("Choose a source: ")
    except KeyboardInterrupt:
        sys.exit()
    if (mode == "1"):
        print("Source chosen: iTunes and IMDb")
        return("1")
    elif (mode == "2"):
        print("Source chosen: Just IMDb")
        return("2")
    else:
        print("The chosen number is not in the list")
        return movie_mode()

def media_mode():
    print("---------------------------------------------------------------------------------------------------")
    print("Choose media type:")
    print("1: Movie")
    print("2: TV Show")
    try:
        media_type = input("Choose a media type: ")
    except KeyboardInterrupt:
        sys.exit()
    if (media_type == "1"):
        print("Media type chosen: Movie")
        return movie_mode()
    elif (media_type == "2"):
        print("Media type chosen: TV Show")
        return("3")
    else:
        print("The chosen number is not in the list")
        return media_mode()

def choose_country():
    print("---------------------------------------------------------------------------------------------------")
    print("iTunes countries:")
    sorted_countries = dict(sorted(countries.items(), key=lambda x: x[1]))
    keys = list(sorted_countries.keys())
    values = list(sorted_countries.values())
    iterator = 1
    for i in values:
        print (str(iterator) + " - " + i)
        iterator += 1
    try:
        country = input("Enter iTunes country (leave blank to choose US): ")
    except KeyboardInterrupt:
        sys.exit()
    try:
        country = keys[int(country)-1]
        print("Chosen country: " + country.upper())
        return country
    except IndexError:
        print("The chosen number is not in the list")
        return choose_country()
    except ValueError:
        country = "us"
        print("Chosen country: " + country.upper())
        return country

def choose(search_results):
    try:
        choice_number = input("Choose an item number (type 0 to discard the results): ")
    except KeyboardInterrupt:
        sys.exit()
    if(choice_number != "0"):
        try:
            choice = search_results[int(choice_number)-1]
            return choice
        except IndexError:
            print("The chosen number is not in the list")
            return choose(search_results)
        except ValueError:
            print("Please insert a number")
            return choose(search_results)
    else:
        print("No number chosen, discarding results")
        return None


def get_imdb_choice(search_term):
    i = 1
    counter = 1
    imdb_search_results = []
    while(i < 5):
        imdb_url = f'http://www.omdbapi.com/?apikey={api_key}&s={search_term}&type=movie&page={str(i)}'
        response = session.get(imdb_url)
        response.raise_for_status()
        response = response.json()
        try:
            for item in response["Search"]:
                print(f'{str(counter)}: {item["Title"]} - {item["Year"]}')
                counter += 1
                imdb_search_results.append(item)
        except KeyError:
            break
        i += 1
    imdb_choice = choose(imdb_search_results)
    return imdb_choice

def imdb_search(search_term):
    if (search_term != "sourceimdb"):
        print("---------------------------------------------------------------------------------------------------")
        print("Search results on IMDb for: " + search_term)
        imdb_url = f'http://www.omdbapi.com/?apikey={api_key}&s={search_term}&type=movie'
        response = session.get(imdb_url)
        response.raise_for_status()
        response = response.json()
        if response["Response"] == "True":
            imdb_choice = get_imdb_choice(search_term)
            if (imdb_choice != None):
                print(f'Item chosen: {imdb_choice["Title"]} - {imdb_choice["Year"]}')
                imdb_id = imdb_choice["imdbID"]
                imdb_url = f'http://www.omdbapi.com/?apikey={api_key}&i={imdb_id}&type=movie'
                response = session.get(imdb_url)
                response.raise_for_status()
                response = response.json()
                short_description = response["Plot"].replace("’", "'").replace("“", '"').replace("”", '"').replace("…", "...").replace("  ", " ")            
                short_descriptions.append(short_description)   
            else:
                try:
                    search_term = input("Enter search term: ")
                except KeyboardInterrupt:
                    sys.exit()
                imdb_search(search_term)
        else:
            print("The iTunes movie name couldn't be found on IMDb, please enter the search term again")
            try:
                search_term = input("Enter search term: ")
            except KeyboardInterrupt:
                sys.exit()
            imdb_search(search_term)
    else:
        try:
            search_term = input("Enter search term (type 0 when you're done): ")
        except KeyboardInterrupt:
            sys.exit()
        if (search_term != "0" and search_term != ""):
            print("---------------------------------------------------------------------------------------------------")
            print("Search results on IMDb for: " + search_term)
            imdb_url = f'http://www.omdbapi.com/?apikey={api_key}&s={search_term}&type=movie'
            response = session.get(imdb_url)
            response.raise_for_status()
            response = response.json()
            if response["Response"] == "True":
                imdb_choice = get_imdb_choice(search_term)
                if (imdb_choice != None):
                    print(f'Item chosen: {imdb_choice["Title"]} - {imdb_choice["Year"]}')
                    imdb_id = imdb_choice["imdbID"]
                    imdb_url = f'http://www.omdbapi.com/?apikey={api_key}&i={imdb_id}&type=movie'
                    urls.append(imdb_url)
            else:
                print("No results match the search term entered")
            imdb_search("sourceimdb")
        elif (search_term == ""):
            print("Enter a valid search term")
            imdb_search("sourceimdb")
        else:
            print(str(len(urls)) + " search terms added")


def itunes_search(mode: str, entity: str):
    print("---------------------------------------------------------------------------------------------------")
    try:
        search_term = input("Enter search term (type 0 when you're done): ")
    except KeyboardInterrupt:
        sys.exit()
    if (search_term != "0" and search_term != ""):
        country = choose_country()
        movie_url = f'https://itunes.apple.com/search?term={search_term}&country={country}&entity={entity}'
        response = session.get(movie_url)
        response.raise_for_status()
        response = response.json()
        print("---------------------------------------------------------------------------------------------------")
        print("Search results on iTunes (" + country.upper() + ") for: " + search_term)
        if response["results"]:
            item_key = "trackName" if mode == "1" else "collectionName"
            counter = 1
            search_results=[]
            for item in response["results"]:
                try:
                    print(f'{str(counter)}: {item[item_key]} - {item["releaseDate"][:4]}')
                    counter += 1
                    search_results.append(item)
                except KeyError:
                    pass
            choice = choose(search_results)
            if (choice != None):
                print(f'Item chosen: {choice[item_key]} - {choice["releaseDate"][:4]}')
                url = choice[f'{item_key.replace("Name", "View")}Url']
                urls.append(url)
                imgurl = (choice["artworkUrl100"]).replace("100x100bb", "100000x100000-999")
                img_urls.append(imgurl)
            if (mode == "1"):
                imdb_search(choice["trackName"])
        else:
            print("No results match the search term entered")
        itunes_search(mode, entity)
    elif (search_term == ""):
        print("Enter a valid search term")
        itunes_search(mode, entity)
    else:
        print(str(len(urls)) + " search terms added")

def save_cover(title, img_url):
    print(f'Image URL: {img_url}')
    print("Downloading image...")
    r = session.get(img_url)
    filename = title +  ".jpg"
    fcharacters = [':', '*', '?', '"', '<', '>', '|', ' ', "'", "/"]
    for fcharacter in fcharacters:
        if fcharacter in filename:
            filename = filename.replace(fcharacter,"")
    filename = filename.lower()
    with open(filename, 'wb') as f:
        f.write(r.content)
    print("Download complete")
    print("Image saved in: " + filename)

def save_data(output):
    with open('metadata.txt', 'w', encoding='utf-8') as f:
        for line in output:
            f.write("%s\n" % line)
    print("Done")

def get_movie_information():
    for url, img_url, short_description in zip(urls, img_urls, short_descriptions):
        print("---------------------------------------------------------------------------------------------------")
        print("Movie URL: " + url)
        print("Country: " + url.split(".com/")[1][:2].upper())
        print("Getting metadata...")
        movieid = url.split("/id")[1].split("?")[0]
        season_url = "https://itunes.apple.com/lookup?id=" + movieid + "&entity=movie"
        response = requests.get(season_url)
        response.raise_for_status()
        response = response.json()
        response = response["results"][0]
        html = None
        while (html == None):
            try:
                browser = webdriver.Chrome(service = Service(ChromeDriverManager().install()))
                browser.get(url)
                html = browser.page_source
            except WebDriverException:
                browser.close()
                time.sleep(1)
        soup = BeautifulSoup(html, 'lxml')
        title = response["trackName"]
        time.sleep(3)
        rating = response["contentAdvisoryRating"]
        genre = response["primaryGenreName"]
        release_date = response["releaseDate"][:10]
        description = response["longDescription"]
        try:
            studio = soup.find_all("section", class_="product-footer__metadata__section")[0].find_all("dd", class_="product-footer__metadata__section__desc typ-caption clr-secondary-text")[0].text.strip()
        except AttributeError:
            studio = ""
        try:
            cpright = soup.find_all("section", class_="product-footer__metadata__section")[0].find("p", class_="product-footer__metadata__section__desc typ-caption clr-secondary-text").text.strip()
        except AttributeError:
            cpright = ""
        ourl = f'Movie URL: {url}'
        ocountry = f'Country: {url.split(".com/")[1][:2].upper()})'
        otitle = f'Title: {title}'
        ordate = f'Release Date: {release_date}'
        orating = f'Rating: {rating}'
        ogenre = f'Genre: {genre}'
        osdescr = "Short Description: " + short_description.replace("’", "'").replace("“", '"').replace("”", '"').replace("…", "...").replace("  ", " ")
        odescr = "Long Description: " + description.replace("’", "'").replace("“", '"').replace("”", '"').replace("…", "...").replace("  ", " ")
        ostudio = f'Studio: {studio}'
        ocpright = f'Copyright: {cpright}'
        omovieid = f'Movie ID: {movieid}'
        spacer="---------------------------------------------------------------------------------------------------"
        output.append(ourl)
        output.append(ocountry)
        output.append(otitle)
        output.append(ordate)
        output.append(orating)
        output.append(ogenre)
        output.append(osdescr)
        output.append(odescr)
        output.append(ostudio)
        output.append(ocpright)
        output.append(omovieid)
        output.append(spacer)
        print(otitle)
        print(ordate)
        print(orating)
        print(ogenre)
        print(osdescr)
        print(odescr)
        print(ostudio)
        print(ocpright)
        print(omovieid)
        browser.close()
        print("Metadata extracted")
        save_cover(title, img_url)
    save_data(output)


def get_imdb_movie_information():
    for url in urls:
        print("---------------------------------------------------------------------------------------------------")
        print(f'Movie URL: https://www.imdb.com/title/{url.split("&i=")[1].split("&type=")[0]}/')
        print("Getting metadata...")
        print("OTHER URL:", url)
        response = session.get(url)
        response.raise_for_status()
        response = response.json()
        title = response["Title"]
        year = response["Year"]
        date = response["Released"]
        main_rating = response["Rated"]
        genre = response["Genre"]
        description = response["Plot"].replace("’", "'").replace("“", '"').replace("”", '"').replace("…", "...").replace("  ", " ")
        directors = response["Director"]
        screenwriters = response["Writer"]
        production_company = response["Production"]
        imdbID = response["imdbID"]
        cast = []
        release_dates = []
        producers = []
        distributors = []
        productions = []
        ratings = []
        cast_crew_url = f'https://www.imdb.com/title/{imdbID}/fullcredits?ref_=tt_cl_sm#cast'
        release_info_url = f'https://www.imdb.com/title/{imdbID}/releaseinfo?ref_=tt_ov_inf'
        company_credits_url = f'https://www.imdb.com/title/{imdbID}/companycredits?ref_=tt_dt_co'
        ratings_url = f'https://www.imdb.com/title/{imdbID}/parentalguide?ref_=tt_stry_pg#certification'
        plot_url = f'https://www.imdb.com/title/{imdbID}/plotsummary?ref_=tt_ov_pl'
        result = session.get(cast_crew_url)
        src = result.content
        soup = BeautifulSoup(src, 'lxml')
        cast_list = soup.find("table", class_="cast_list")
        cast_list = cast_list.find_all("tr")
        for actor in cast_list:
            try:
                if (actor["class"][0] == "odd" or actor["class"][0] == "even"):
                    cast.append(actor.find_all("td")[1].text.strip())
            except KeyError:
                pass
        header_list = soup.find_all("h4", class_="dataHeaderWithBorder")
        try:
            if ("Produced by" in header_list[3].text):
                producers_list = soup.find_all("table", class_="simpleTable simpleCreditsTable")
                producers_list = producers_list[2].find_all("tr")
                for producer in producers_list:
                    producer = producer.find_all("td")
                    producers.append(f'{producer[0].text.strip()} - {producer[2].text.strip()}')
        except IndexError:
            pass
        html = None
        while (html == None):
            try:
                browser = webdriver.Chrome(service = Service(ChromeDriverManager().install()))
                browser.get(release_info_url)
                html = browser.page_source
            except WebDriverException:
                browser.close()
                time.sleep(1)
        soup = BeautifulSoup(html, 'lxml')
        release_list = browser.find_elements("xpath", "//div[@data-testid='sub-section-releases']/ul/li")
        for release in release_list:
            release_country = release.find_element("xpath", "./a").text.strip()
            print("RELEASE COUNTRY:", release_country)
            release_date = release.find_elements("xpath", "./div")[0].find_elements("xpath", ".//span")[0].text.strip()
            print("RELEASE DATA:", release_date)
            release_dates.append(f'{release_country} - {release_date}')
        html = None
        while (html == None):
            try:
                browser = webdriver.Chrome(service = Service(ChromeDriverManager().install()))
                browser.get(company_credits_url)
                html = browser.page_source
            except WebDriverException:
                browser.close()
                time.sleep(1)
        soup = BeautifulSoup(html, 'lxml')
        production_header = soup.find("span", id="production")
        if production_header != None:
            production_list = browser.find_elements("xpath", "//div[@data-testid='sub-section-production']/ul/li")
            for production in production_list:
                productions.append(production.text.strip().replace("            "," - "))
        distributors_header = soup.find("span", id = "distribution")
        if distributors_header != None:
            distributor_list = browser.find_elements("xpath", "//div[@data-testid='sub-section-distribution']/ul/li")            
            for distributor in distributor_list:
                distributors.append(distributor.text.strip().replace("            "," - "))
        result = session.get(ratings_url)
        src = result.content
        soup = BeautifulSoup(src, 'lxml')
        ratings_list = soup.find("tr", id = "certifications-list")
        try:
            ratings_list = ratings_list.find_all("li")
            for rating in ratings_list:
                ratings.append(rating.find("a").text)
        except AttributeError:
            pass
        html = None
        while (html == None):
            try:
                browser = webdriver.Chrome(service = Service(ChromeDriverManager().install()))
                browser.get(plot_url)
                html = browser.page_source
            except WebDriverException:
                browser.close()
                time.sleep(1)
        soup = BeautifulSoup(html, 'lxml')
        ourl = f'Movie URL: https://www.imdb.com/title/{imdbID}/'
        otitle = f'Title: {title}'
        oyear = f'Year: {year}'
        odate = f'Date: {date}'
        omainrating = f'Rating: {main_rating}'
        ogenre = f'Genre: {genre}'
        odescription = f'Description: {description}'
        odirectors = f'Directors: {directors}'
        oproducers = "Producers: "+ ', '.join(producers)
        ocast = "Cast: " + ', '.join(cast)
        oscreenwriters = f'Screenwriters: {screenwriters}'
        oproductioncmpn = f'Production Company: {production_company}'
        oreleasedates = "Release Dates: \n" + '\n'.join(sorted(release_dates))
        oproductioncmpns = "Production Companies: \n" + '\n'.join(productions)
        odistributors = "Distributors: \n" + '\n'.join(distributors)
        oratings = "Ratings: \n" + '\n'.join(ratings)
        spacer="---------------------------------------------------------------------------------------------------"
        output.append(ourl)
        output.append(otitle)
        output.append(oyear)
        output.append(odate)
        output.append(omainrating)
        output.append(ogenre)
        output.append(odescription)
        output.append(odirectors)
        output.append(oproducers)
        output.append(ocast)
        output.append(oscreenwriters)
        output.append(oproductioncmpn)
        output.append(oreleasedates)
        output.append(oproductioncmpns)
        output.append(odistributors)
        output.append(oratings)
        output.append(spacer)
        print(otitle)
        print(oyear)
        print(odate)
        print(omainrating)
        print(ogenre)
        print(odescription)
        print(odirectors)
        print(oproducers)
        print(ocast)
        print(oscreenwriters)
        print(oproductioncmpn)
        print(oreleasedates)
        print(oproductioncmpns)
        print(odistributors)
        print(oratings)
    save_data(output)


def get_tv_show_information():
    for url, img_url in zip(urls, img_urls):
        print("---------------------------------------------------------------------------------------------------")
        print("TV Show URL: " + url)
        country = url.split(".com/")[1][:2].upper()
        print(f'Country: {country}')
        season_id = url.split("/id")[1].split("?")[0]
        print(f'ID: {season_id}')
        print("Getting metadata...")
        season_url = f'https://itunes.apple.com/lookup?id={season_id}&entity=tvEpisode'
        response = requests.get(season_url)
        response.raise_for_status()
        response = response.json()
        response = response["results"]
        episodes_list = []
        season_collection = None
        for track in response:
            if track["wrapperType"] == "track":
                episodes_list.append(track)
            else:
                season_collection = track
        stitle = season_collection["collectionName"]
        try:
            rating = season_collection["contentAdvisoryRating"]
        except KeyError:
            rating = ""
        genre = season_collection["primaryGenreName"]
        srelease_date = season_collection["releaseDate"][:10]
        sdescription = season_collection["longDescription"]
        sdescription_html = markdown.markdown(sdescription)
        sdescription_soup = BeautifulSoup(sdescription_html, features='html.parser')
        sdescription = sdescription_soup.get_text()
        sdescription = sdescription.replace("’", "'").replace("“", '"').replace("”", '"').replace("…", "...").replace("  ", " ")
        cpright = season_collection["copyright"]
        seasonid = season_collection["collectionId"]
        ourl = f'TV Show URL: {url}'
        ocountry = f'Country: {url.split(".com/")[1][:2].upper()}'
        ostitle = f'Season Title: {stitle}'
        osrelease_date = f'Season Release Date: {srelease_date}'
        orating = f'Rating: {rating}'
        ogenre = f'Genre: {genre}'
        osdescription = f'Season Description: {sdescription}'
        ocpright = f'Copyright: {cpright}'
        oseasonid = f'Season ID: {str(seasonid)}'
        spacer = "---------------------------------------------------------------------------------------------------"
        output.append(ourl)
        output.append(ocountry)
        output.append(ostitle)
        output.append(osrelease_date)
        output.append(orating)
        output.append(ogenre)
        output.append(osdescription)
        output.append(ocpright)
        output.append(oseasonid)
        print(ostitle)
        print(osrelease_date)
        print(orating)
        print(ogenre)
        print(osdescription)
        print(ocpright)
        print(oseasonid)
        for episode in episodes_list:
            episode_id = episode["trackId"]
            episode_number = episode["trackNumber"]
            episode_title = episode["trackName"]
            episode_description = episode["longDescription"]
            episode_description_html = markdown.markdown(episode_description)
            episode_description_soup = BeautifulSoup(episode_description_html, features='html.parser')
            episode_description = episode_description_soup.get_text()
            episode_description = episode_description.replace("’", "'").replace("“", '"').replace("”", '"').replace("…", "...").replace("  ", " ")
            episode_release_date = episode["releaseDate"][:10]
            spacer2 = "###################################################################################################"
            oepisode_number = f'Episode Number: {str(episode_number)}'
            oepisode_title = f'Episode Title: {episode_title}'
            oepisode_release_date = f'Episode Release Date: {episode_release_date}'
            oepisode_description = f'Episode Description: {episode_description}'
            oepisode_id = f'Episode ID: {str(episode_id)}'
            output.append(spacer2)
            output.append(oepisode_number)
            output.append(oepisode_title)
            output.append(oepisode_release_date)
            output.append(oepisode_description)
            output.append(oepisode_id)
            print(spacer2)
            print(oepisode_number)
            print(oepisode_title)
            print(oepisode_release_date)
            print(oepisode_description)
            print(oepisode_id)
        output.append(spacer)
        print("Metadata extracted")
        save_cover(stitle, img_url)
    save_data(output)
