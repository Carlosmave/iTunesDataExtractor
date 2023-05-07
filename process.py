from config import countries, session, api_key, chrome_options
import sys, time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup
import markdown

class Process:
    def __init__(self):
        self.browser = webdriver.Chrome(service = Service(ChromeDriverManager().install()), options = chrome_options)
        self.urls = []
        self.img_urls = []
        self.imdb_ids = []
        self.output = []
        self.session = session

    def get_html_page_content(self, url: str):
        html = None
        while (html == None):
            try:
                self.browser.get(url)
                html = self.browser.page_source
            except WebDriverException:
                self.browser.close()
                time.sleep(1)
                self.browser = webdriver.Chrome(service = Service(ChromeDriverManager().install()), options = chrome_options)
        soup = BeautifulSoup(html, 'lxml')
        return soup

    def movie_mode(self):
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
            return self.movie_mode()

    def media_mode(self):
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
            return self.movie_mode()
        elif (media_type == "2"):
            print("Media type chosen: TV Show")
            return("3")
        else:
            print("The chosen number is not in the list")
            return self.media_mode()

    def choose_country(self):
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
            return self.choose_country()
        except ValueError:
            country = "us"
            print("Chosen country: " + country.upper())
            return country

    def choose(self, search_results):
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
                return self.choose(search_results)
            except ValueError:
                print("Please insert a number")
                return self.choose(search_results)
        else:
            print("No number chosen, discarding results")
            return None


    def get_imdb_choice(self, search_term):
        i = 1
        counter = 1
        imdb_search_results = []
        while(i < 5):
            imdb_url = f'http://www.omdbapi.com/?apikey={api_key}&s={search_term}&type=movie&page={str(i)}'
            response = self.session.get(imdb_url)
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
        imdb_choice = self.choose(imdb_search_results)
        return imdb_choice

    def imdb_search(self, search_term):
        if (search_term != "sourceimdb"):
            print("---------------------------------------------------------------------------------------------------")
            print("Search results on IMDb for: " + search_term)
            imdb_url = f'http://www.omdbapi.com/?apikey={api_key}&s={search_term}&type=movie'
            response = self.session.get(imdb_url)
            response.raise_for_status()
            response = response.json()
            if response["Response"] == "True":
                imdb_choice = self.get_imdb_choice(search_term)
                if (imdb_choice != None):
                    print(f'Item chosen: {imdb_choice["Title"]} - {imdb_choice["Year"]}')
                    imdb_id = imdb_choice["imdbID"]
                    self.imdb_ids.append(imdb_id)
                else:
                    try:
                        search_term = input("Enter search term: ")
                    except KeyboardInterrupt:
                        sys.exit()
                    self.imdb_search(search_term)
            else:
                print("The iTunes movie name couldn't be found on IMDb, please enter the search term again")
                try:
                    search_term = input("Enter search term: ")
                except KeyboardInterrupt:
                    sys.exit()
                self.imdb_search(search_term)
        else:
            try:
                search_term = input("Enter search term (type 0 when you're done): ")
            except KeyboardInterrupt:
                sys.exit()
            if (search_term != "0" and search_term != ""):
                print("---------------------------------------------------------------------------------------------------")
                print("Search results on IMDb for: " + search_term)
                imdb_url = f'http://www.omdbapi.com/?apikey={api_key}&s={search_term}&type=movie'
                response = self.session.get(imdb_url)
                response.raise_for_status()
                response = response.json()
                if response["Response"] == "True":
                    imdb_choice = self.get_imdb_choice(search_term)
                    if (imdb_choice != None):
                        print(f'Item chosen: {imdb_choice["Title"]} - {imdb_choice["Year"]}')
                        imdb_id = imdb_choice["imdbID"]
                        imdb_url = f'http://www.omdbapi.com/?apikey={api_key}&i={imdb_id}&type=movie'
                        self.urls.append(imdb_url)
                else:
                    print("No results match the search term entered")
                self.imdb_search("sourceimdb")
            elif (search_term == ""):
                print("Enter a valid search term")
                self.imdb_search("sourceimdb")
            else:
                print(str(len(self.urls)) + " search terms added")


    def itunes_search(self, mode: str, entity: str):
        print("---------------------------------------------------------------------------------------------------")
        try:
            search_term = input("Enter search term (type 0 when you're done): ")
        except KeyboardInterrupt:
            sys.exit()
        if (search_term != "0" and search_term != ""):
            country = self.choose_country()
            movie_url = f'https://itunes.apple.com/search?term={search_term}&country={country}&entity={entity}'
            response = self.session.get(movie_url)
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
                choice = self.choose(search_results)
                if (choice != None):
                    print(f'Item chosen: {choice[item_key]} - {choice["releaseDate"][:4]}')
                    url = choice[f'{item_key.replace("Name", "View")}Url']
                    self.urls.append(url)
                    imgurl = (choice["artworkUrl100"]).replace("100x100bb", "100000x100000-999")
                    self.img_urls.append(imgurl)
                if (mode == "1"):
                    self.imdb_search(choice["trackName"])
            else:
                print("No results match the search term entered")
            self.itunes_search(mode, entity)
        elif (search_term == ""):
            print("Enter a valid search term")
            self.itunes_search(mode, entity)
        else:
            print(str(len(self.urls)) + " search terms added")

    def save_cover(self, title, img_url):
        print(f'Image URL: {img_url}')
        print("Downloading image...")
        r = self.session.get(img_url)
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

    def save_data(self):
        with open('metadata.txt', 'w', encoding='utf-8') as f:
            for line in self.output:
                f.write("%s\n" % line)
        print("Done")

    def get_movie_information(self):
        for url, img_url, imdb_id in zip(self.urls, self.img_urls, self.imdb_ids):
            print("---------------------------------------------------------------------------------------------------")
            print("Movie URL: " + url)
            print("Country: " + url.split(".com/")[1][:2].upper())
            print("Getting metadata...")
            movieid = url.split("/id")[1].split("?")[0]
            season_url = "https://itunes.apple.com/lookup?id=" + movieid + "&entity=movie"
            response = self.session.get(season_url)
            response.raise_for_status()
            response = response.json()
            response = response["results"][0]
            title = response["trackName"]
            rating = response["contentAdvisoryRating"]
            genre = response["primaryGenreName"]
            release_date = response["releaseDate"][:10]
            description = response["longDescription"]
            soup = self.get_html_page_content(url)
            try:
                studio = soup.find_all("section", class_="product-footer__metadata__section")[0].find_all("dd", class_="product-footer__metadata__section__desc typ-caption clr-secondary-text")[0].text.strip()
            except AttributeError:
                studio = ""
            try:
                cpright = soup.find_all("section", class_="product-footer__metadata__section")[0].find("p", class_="product-footer__metadata__section__desc typ-caption clr-secondary-text").text.strip()
            except AttributeError:
                cpright = ""
            imdb_url = f'http://www.omdbapi.com/?apikey={api_key}&i={imdb_id}&type=movie'
            response = self.session.get(imdb_url)
            response.raise_for_status()
            response = response.json()
            short_description = response["Plot"].replace("’", "'").replace("“", '"').replace("”", '"').replace("…", "...").replace("  ", " ")
            directors = response["Director"]
            screenwriters = response["Writer"]
            cast = []
            producers = []
            cast_crew_url = f'https://www.imdb.com/title/{imdb_id}/fullcredits?ref_=tt_cl_sm#cast'
            soup = self.get_html_page_content(cast_crew_url)
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
            odirectors = f'Directors: {directors}'
            oproducers = "Producers: "+ ', '.join(producers)
            ocast = "Cast: " + ', '.join(cast)
            oscreenwriters = f'Screenwriters: {screenwriters}'
            spacer="---------------------------------------------------------------------------------------------------"
            self.output.append(ourl)
            self.output.append(ocountry)
            self.output.append(otitle)
            self.output.append(ordate)
            self.output.append(orating)
            self.output.append(ogenre)
            self.output.append(osdescr)
            self.output.append(odescr)
            self.output.append(ostudio)
            self.output.append(ocpright)
            self.output.append(omovieid)
            self.output.append(odirectors)
            self.output.append(oproducers)
            self.output.append(ocast)
            self.output.append(oscreenwriters)
            self.output.append(spacer)
            print(otitle)
            print(ordate)
            print(orating)
            print(ogenre)
            print(osdescr)
            print(odescr)
            print(ostudio)
            print(ocpright)
            print(omovieid)
            print(odirectors)
            print(oproducers)
            print(ocast)
            print(oscreenwriters)
            # browser.close()
            print("Metadata extracted")
            self.save_cover(title, img_url)
        self.browser.close()
        self.save_data()


    def get_imdb_movie_information(self):
        for url in self.urls:
            print("---------------------------------------------------------------------------------------------------")
            print(f'Movie URL: https://www.imdb.com/title/{url.split("&i=")[1].split("&type=")[0]}/')
            print("Getting metadata...")
            print("OTHER URL:", url)
            response = self.session.get(url)
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
            soup = self.get_html_page_content(cast_crew_url)
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
            soup = self.get_html_page_content(release_info_url)
            release_list = self.browser.find_elements("xpath", "//div[@data-testid='sub-section-releases']/ul/li")
            for release in release_list:
                release_country = release.find_element("xpath", "./a").text.strip()
                release_date = release.find_elements("xpath", "./div")[0].find_elements("xpath", ".//span")[0].text.strip()
                release_dates.append(f'{release_country} - {release_date}')
            soup = self.get_html_page_content(company_credits_url)
            production_header = soup.find("span", id="production")
            if production_header != None:
                production_list = self.browser.find_elements("xpath", "//div[@data-testid='sub-section-production']/ul/li")
                for production in production_list:
                    productions.append(production.text.strip().replace("            "," - "))
            distributors_header = soup.find("span", id = "distribution")
            if distributors_header != None:
                distributor_list = self.browser.find_elements("xpath", "//div[@data-testid='sub-section-distribution']/ul/li")            
                for distributor in distributor_list:
                    distributors.append(distributor.text.strip().replace("            "," - "))
            soup = self.get_html_page_content(ratings_url)
            ratings_list = soup.find("tr", id = "certifications-list")
            try:
                ratings_list = ratings_list.find_all("li")
                for rating in ratings_list:
                    ratings.append(rating.find("a").text)
            except AttributeError:
                pass
            soup = self.get_html_page_content(plot_url)
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
            self.output.append(ourl)
            self.output.append(otitle)
            self.output.append(oyear)
            self.output.append(odate)
            self.output.append(omainrating)
            self.output.append(ogenre)
            self.output.append(odescription)
            self.output.append(odirectors)
            self.output.append(oproducers)
            self.output.append(ocast)
            self.output.append(oscreenwriters)
            self.output.append(oproductioncmpn)
            self.output.append(oreleasedates)
            self.output.append(oproductioncmpns)
            self.output.append(odistributors)
            self.output.append(oratings)
            self.output.append(spacer)
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
        self.browser.close()
        self.save_data()


    def get_tv_show_information(self):
        for url, img_url in zip(self.urls, self.img_urls):
            print("---------------------------------------------------------------------------------------------------")
            print("TV Show URL: " + url)
            country = url.split(".com/")[1][:2].upper()
            print(f'Country: {country}')
            season_id = url.split("/id")[1].split("?")[0]
            print(f'ID: {season_id}')
            print("Getting metadata...")
            season_url = f'https://itunes.apple.com/lookup?id={season_id}&entity=tvEpisode'
            response = self.session.get(season_url)
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
            self.output.append(ourl)
            self.output.append(ocountry)
            self.output.append(ostitle)
            self.output.append(osrelease_date)
            self.output.append(orating)
            self.output.append(ogenre)
            self.output.append(osdescription)
            self.output.append(ocpright)
            self.output.append(oseasonid)
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
                self.output.append(spacer2)
                self.output.append(oepisode_number)
                self.output.append(oepisode_title)
                self.output.append(oepisode_release_date)
                self.output.append(oepisode_description)
                self.output.append(oepisode_id)
                print(spacer2)
                print(oepisode_number)
                print(oepisode_title)
                print(oepisode_release_date)
                print(oepisode_description)
                print(oepisode_id)
            self.output.append(spacer)
            print("Metadata extracted")
            self.save_cover(stitle, img_url)
        self.browser.close()
        self.save_data()
