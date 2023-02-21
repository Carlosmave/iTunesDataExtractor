import requests, json, sys, time
from bs4 import BeautifulSoup
from selenium import webdriver

from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from selenium.common.exceptions import WebDriverException
import markdown

mode=""
urls=[]
img_urls=[]
short_descriptions=[]
search_terms=[]
output=[]
apikey="e6fa56aa"
entity=""

session = requests.Session()
retry = Retry(connect=5, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)


def movie_mode():
    print("---------------------------------------------------------------------------------------------------")
    print("Choose source:")
    print("1: iTunes and IMDb")
    print("2: Just IMDb")
    try:
        mode = input("Choose a source: ")
    except KeyboardInterrupt:
        sys.exit()
    if (mode=="1"):
        print("Source chosen: iTunes and IMDb")
        return("1")
    elif (mode=="2"):
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
    if (media_type=="1"):
        print("Media type chosen: Movie")
        return movie_mode()
    elif (media_type=="2"):
        print("Media type chosen: TV Show")
        return("3")
    else:
        print("The chosen number is not in the list")
        return media_mode()



##def search():
##    search_term = input("Enter search term (type 0 when you're done): ")
##    if (search_term != "0" and search_term != ""):
##        search_terms.append(search_term)
##        search()
##    elif (search_term == ""):
##        print("Enter a valid search term")
##        search()
##    else:
##        print(str(len(search_terms)) + " search terms added")








def choose(search_results):
    try:
        choice_number = input("Choose an item number (type 0 to discard the results): ")
    except KeyboardInterrupt:
        sys.exit()
    if(choice_number!="0"):
        try:
            choice=search_results[int(choice_number)-1]
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


def imdb_search(search_term):
    if (search_term!="sourceimdb"):
        print("---------------------------------------------------------------------------------------------------")
        print("Search results on IMDb for: " + search_term)
        imdb_url = 'http://www.omdbapi.com/?apikey=' + apikey + '&s=' + search_term + '&type=movie'
        response = session.get(imdb_url)
        response.raise_for_status()
        response = response.json()
        if response["Response"]=="True":
            i=1
            counter=1
            imdb_search_results=[]
            while(i<5):
                imdb_url = 'http://www.omdbapi.com/?apikey=' + apikey + '&s=' + search_term + '&type=movie&page=' + str(i)
                response = session.get(imdb_url)
                response.raise_for_status()
                response = response.json()
                try:
                    for item in response["Search"]:
                        print(str(counter)+ ": " + item["Title"] + " - " + item["Year"])
                        counter+=1
                        imdb_search_results.append(item)
                except KeyError:
                    break
                    #pass
                i+=1
            imdb_choice=choose(imdb_search_results)
            if (imdb_choice !=None):

                print("Item chosen: " + imdb_choice["Title"]  + " - " + imdb_choice["Year"])
                imdb_id=imdb_choice["imdbID"]

                #imdb_url = 'http://www.omdbapi.com/?apikey=' + apikey + '&i=' + imdb_id + '&type=movie'
                #response = requests.get(imdb_url)
                #response.raise_for_status()
                #response = response.json()
                #short_descriptions.append(response["Plot"])



                plot_url = "https://www.imdb.com/title/" + imdb_id + "/plotsummary?ref_=tt_ov_pl"
                # result=session.get(plot_url)
                # src = result.content
                # soup = BeautifulSoup(src, 'lxml')
                # description_list = soup.find("ul", id="plot-summaries-content")
                # description_list = description_list.find_all("li")
                # short_description = description_list[0].find("p").text.replace("’", "'").replace("“", '"').replace("”", '"').replace("…", "...").replace("  ", " ")
                # short_descriptions.append(short_description)

                
                html=None
                while (html == None):
                    try:
                        # browser = webdriver.Firefox(executable_path = r'C:/Users/carlo/Documents/Programming-Projects/Python Scripts/iTunesMediaExtractor/geckodriver.exe')
                        browser = webdriver.Chrome(service = Service(ChromeDriverManager().install()))
                        browser.get(plot_url)
                        html=browser.page_source
                    except WebDriverException:
                        browser.close()
                        time.sleep(1)

                soup = BeautifulSoup(html, 'lxml')

                try:
                    description_list = soup.find("div", attrs={"data-testid":"sub-section-summaries"}).find("ul")
                    description_list = description_list.find_all("li", attrs={"role":"presentation"})[0]
                    short_description = description_list.text.replace("’", "'").replace("“", '"').replace("”", '"').replace("…", "...").replace("  ", " ")
                except Exception as e:
                    print("Exception:", str(e))
                    short_description = "No Description Available" 
                short_descriptions.append(short_description)               

            else:
                try:
                    search_term = input("Enter search term: ")
                except KeyboardInterrupt:
                    sys.exit()
                #print("---------------------------------------------------------------------------------------------------")
                #print("Search results on IMDb for: " + search_term)
                imdb_search(search_term)




            #print("---------------------------------------------------------------------------------------------------")
        else:
            print("The iTunes movie name couldn't be found on IMDb, please enter the search term again")
            try:
                search_term = input("Enter search term: ")
            except KeyboardInterrupt:
                sys.exit()
            #print("---------------------------------------------------------------------------------------------------")
            #print("Search results on IMDb for: " + search_term)
            imdb_search(search_term)
    else:
        try:
            search_term = input("Enter search term (type 0 when you're done): ")
        except KeyboardInterrupt:
            sys.exit()
        if (search_term != "0" and search_term != ""):
            print("---------------------------------------------------------------------------------------------------")
            print("Search results on IMDb for: " + search_term)
            imdb_url = 'http://www.omdbapi.com/?apikey=' + apikey + '&s=' + search_term + '&type=movie'
            response = session.get(imdb_url)
            response.raise_for_status()
            response = response.json()
            if response["Response"]=="True":
##                print("---------------------------------------------------------------------------------------------------")
##                print("Search results on IMDb for: " + search_term)
                i=1
                counter=1
                imdb_search_results=[]
                while(i<5):
                    imdb_url = 'http://www.omdbapi.com/?apikey=' + apikey + '&s=' + search_term + '&type=movie&page=' + str(i)
                    response = session.get(imdb_url)
                    response.raise_for_status()
                    response = response.json()
                    try:
                        for item in response["Search"]:
                            print(str(counter)+ ": " + item["Title"] + " - " + item["Year"])
                            counter+=1
                            imdb_search_results.append(item)
                    except KeyError:
                        break
                        #pass
                    i+=1
                imdb_choice=choose(imdb_search_results)
                if (imdb_choice !=None):
                    print("Item chosen: " + imdb_choice["Title"]  + " - " + imdb_choice["Year"])
                    imdb_id=imdb_choice["imdbID"]
                    imdb_url = 'http://www.omdbapi.com/?apikey=' + apikey + '&i=' + imdb_id + '&type=movie'
                    urls.append(imdb_url)
            else:
                print("No results match the search term entered")
            imdb_search("sourceimdb")
        elif (search_term == ""):
            print("Enter a valid search term")
            imdb_search("sourceimdb")
        else:
            print(str(len(urls)) + " search terms added")


def choose_country():
    countries={
    "ae": "United Arab Emirates",
    "ag": "Antigua and Barbuda",
    "ai": "Anguilla",
    "al": "Albania",
    "am": "Armenia",
    "ao": "Angola",
    "ar": "Argentina",
    "at": "Austria",
    "au": "Australia",
    "az": "Azerbaijan",
    "bb": "Barbados",
    "be": "Belgium",
    "bf": "Burkina-Faso",
    "bg": "Bulgaria",
    "bh": "Bahrain",
    "bj": "Benin",
    "bm": "Bermuda",
    "bn": "Brunei Darussalam",
    "bo": "Bolivia",
    "br": "Brazil",
    "bs": "Bahamas",
    "bt": "Bhutan",
    "bw": "Botswana",
    "by": "Belarus",
    "bz": "Belize",
    "ca": "Canada",
    "cg": "Democratic Republic of the Congo",
    "ch": "Switzerland",
    "cl": "Chile",
    "cn": "China",
    "co": "Colombia",
    "cr": "Costa Rica",
    "cv": "Cape Verde",
    "cy": "Cyprus",
    "cz": "Czech Republic",
    "de": "Germany",
    "dk": "Denmark",
    "dm": "Dominica",
    "do": "Dominican Republic",
    "dz": "Algeria",
    "ec": "Ecuador",
    "ee": "Estonia",
    "eg": "Egypt",
    "es": "Spain",
    "fi": "Finland",
    "fj": "Fiji",
    "fm": "Federated States of Micronesia",
    "fr": "France",
    "gb": "United Kingdom",
    "gd": "Grenada",
    "gh": "Ghana",
    "gm": "Gambia",
    "gr": "Greece",
    "gt": "Guatemala",
    "gw": "Guinea Bissau",
    "gy": "Guyana",
    "hk": "Hong Kong",
    "hn": "Honduras",
    "hr": "Croatia",
    "hu": "Hungary",
    "id": "Indonesia",
    "ie": "Ireland",
    "il": "Israel",
    "in": "India",
    "is": "Iceland",
    "it": "Italy",
    "jm": "Jamaica",
    "jo": "Jordan",
    "jp": "Japan",
    "ke": "Kenya",
    "kg": "Krygyzstan",
    "kh": "Cambodia",
    "kn": "Saint Kitts and Nevis",
    "kr": "South Korea",
    "kw": "Kuwait",
    "ky": "Cayman Islands",
    "kz": "Kazakhstan",
    "la": "Laos",
    "lb": "Lebanon",
    "lc": "Saint Lucia",
    "lk": "Sri Lanka",
    "lr": "Liberia",
    "lt": "Lithuania",
    "lu": "Luxembourg",
    "lv": "Latvia",
    "md": "Moldova",
    "mg": "Madagascar",
    "mk": "Macedonia",
    "ml": "Mali",
    "mn": "Mongolia",
    "mo": "Macau",
    "mr": "Mauritania",
    "ms": "Montserrat",
    "mt": "Malta",
    "mu": "Mauritius",
    "mw": "Malawi",
    "mx": "Mexico",
    "my": "Malaysia",
    "mz": "Mozambique",
    "na": "Namibia",
    "ne": "Niger",
    "ng": "Nigeria",
    "ni": "Nicaragua",
    "nl": "Netherlands",
    "np": "Nepal",
    "no": "Norway",
    "nz": "New Zealand",
    "om": "Oman",
    "pa": "Panama",
    "pe": "Peru",
    "pg": "Papua New Guinea",
    "ph": "Philippines",
    "pk": "Pakistan",
    "pl": "Poland",
    "pt": "Portugal",
    "pw": "Palau",
    "py": "Paraguay",
    "qa": "Qatar",
    "ro": "Romania",
    "ru": "Russia",
    "sa": "Saudi Arabia",
    "sb": "Soloman Islands",
    "sc": "Seychelles",
    "se": "Sweden",
    "sg": "Singapore",
    "si": "Slovenia",
    "sk": "Slovakia",
    "sl": "Sierra Leone",
    "sn": "Senegal",
    "sr": "Suriname",
    "st": "Sao Tome e Principe",
    "sv": "El Salvador",
    "sz": "Swaziland",
    "tc": "Turks and Caicos Islands",
    "td": "Chad",
    "th": "Thailand",
    "tj": "Tajikistan",
    "tm": "Turkmenistan",
    "tn": "Tunisia",
    "tr": "Turkey",
    "tt": "Republic of Trinidad and Tobago",
    "tw": "Taiwan",
    "tz": "Tanzania",
    "ua": "Ukraine",
    "ug": "Uganda",
    "us": "United States of America",
    "uy": "Uruguay",
    "uz": "Uzbekistan",
    "vc": "Saint Vincent and the Grenadines",
    "ve": "Venezuela",
    "vg": "British Virgin Islands",
    "vn": "Vietnam",
    "ye": "Yemen",
    "za": "South Africa",
    "zw": "Zimbabwe"}
    countries = dict(sorted(countries.items(), key=lambda x: x[1]))
    print("---------------------------------------------------------------------------------------------------")
    print("iTunes countries:")
    keys=list(countries.keys())
    values=list(countries.values())
    iterator=1
    for i in values:
        print (str(iterator) + " - " + i)
        iterator+=1
    #print(countries.values())
    try:
        country = input("Enter iTunes country (leave blank to choose US): ")
    except KeyboardInterrupt:
        sys.exit()
    #print(keys[int(country)-1])
    try:
        country=keys[int(country)-1]
        print("Chosen country: " + country.upper())
        return country
    except IndexError:
        print("The chosen number is not in the list")
        return choose_country()
    except ValueError:
        country="us"
        print("Chosen country: " + country.upper())
        return country



def itunes_search():
    print("---------------------------------------------------------------------------------------------------")
    try:
        search_term = input("Enter search term (type 0 when you're done): ")
    except KeyboardInterrupt:
        sys.exit()
    if (search_term != "0" and search_term != ""):
        country=choose_country()
        movie_url = 'https://itunes.apple.com/search?term=' + search_term + '&country=' + country + '&entity=' + entity
        response = session.get(movie_url)
        response.raise_for_status()
        response = response.json()
        print("---------------------------------------------------------------------------------------------------")
        print("Search results on iTunes (" + country.upper() + ") for: " + search_term)
        if response["results"]:

            if (mode=="1"):
##                print("---------------------------------------------------------------------------------------------------")
##                print("Search results on iTunes for: " + search_term)

                counter=1
                search_results=[]
                for item in response["results"]:
                    try:
                        print(str(counter)+ ": " + item["trackName"] + " - " + item["releaseDate"][:4])
                        counter+=1
                        search_results.append(item)
                    except KeyError:
                        pass

                choice=choose(search_results)
                if (choice !=None):
                    print("Item chosen: " + choice["trackName"]  + " - " + choice["releaseDate"][:4])
                    url=choice["trackViewUrl"]
                    urls.append(url)
                    imgurl=(choice["artworkUrl100"]).replace("100x100bb", "100000x100000-999")
                    img_urls.append(imgurl)
                    #print("---------------------------------------------------------------------------------------------------")
                    #print("Search results on IMDb for: " + choice["trackName"])
                    imdb_search(choice["trackName"])

            elif (mode=="3"):
##                print("---------------------------------------------------------------------------------------------------")
##                print("Search results on iTunes for: " + search_term)

                counter=1
                search_results=[]
                for item in response["results"]:
                    try:
                        print(str(counter)+ ": " + item["collectionName"] + " - " + item["releaseDate"][:4])
                        counter+=1
                        search_results.append(item)
                    except KeyError:
                        pass

                choice=choose(search_results)
                if (choice !=None):
                    print("Item chosen: " + choice["collectionName"]  + " - " + choice["releaseDate"][:4])
                    url=choice["collectionViewUrl"]
                    urls.append(url)
                    imgurl=(choice["artworkUrl100"]).replace("100x100bb", "100000x100000-999")
                    img_urls.append(imgurl)



        else:
            print("No results match the search term entered")
        itunes_search()
    elif (search_term == ""):
        print("Enter a valid search term")
        itunes_search()
    else:
        print(str(len(urls)) + " search terms added")



print("Welcome to the iTunesMediaExtractor")
print("Made by Carlos Martinez")
mode=media_mode()





if (mode=="1"):
    entity="movie"
    itunes_search()


    for url, img_url, short_description in zip(urls, img_urls, short_descriptions):
        #result=requests.get(url)
        #src = result.content
        #soup = BeautifulSoup(src, 'lxml')
        #Se puede ver que la sección information viene de un JavaScript yendo a la sección "Sources" en el buscador, por eso no se puede obtener mediante requests. Para que se ejecute el JavaScript
        #y aparezca la información completa de forma scrapeable, se debe abrir el link en un buscador. Para eso se utilizó Selenium.
        print("---------------------------------------------------------------------------------------------------")
        print("Movie URL: " + url)
        print("Country: " + url.split(".com/")[1][:2].upper())
        print("Getting metadata...")

##        browser = webdriver.Firefox(executable_path = r'C:/Users/carlo/Documents/Programming-Projects/Python Scripts/iTunesMediaExtractor/geckodriver.exe')

        html=None
        while (html == None):
            try:
                # browser = webdriver.Firefox(executable_path = r'C:/Users/carlo/Documents/Programming-Projects/Python Scripts/iTunesMediaExtractor/geckodriver.exe')
                browser = webdriver.Chrome(service = Service(ChromeDriverManager().install()))
                browser.get(url)
                html=browser.page_source
            except WebDriverException:
                browser.close()
                time.sleep(1)

        soup = BeautifulSoup(html, 'lxml')
        title = soup.find("h1", class_="product-header__title movie-header__title")
        time.sleep(3)
        try:
            rating = soup.find("svg")["aria-label"].replace(" ","-")
            # rating = soup.find("li", attrs = {"class": "inline-list__item inline-list__item--margin-inline-end-rating"}).find("svg")["aria-label"].replace(" ","-")
        except TypeError:
            rating = soup.find("span", class_="badge").text
        genre = soup.find("a", class_="link link--no-tint")
        release_date = soup.find("time")
        description = soup.find("p")
        crew = soup.find_all("dd", class_="cast-list__detail")
        movieid = soup.find("meta", attrs={"name":"apple:content_id"})
        cast=[]
        directors=[]
        producers=[]
        screenwriters=[]

        for person in crew:
            data=person.find("a")
            data=data["data-metrics-click"]
            data=json.loads(data)
            data=data["actionDetails"]
            role=data["type"]
            if role == "cast":
                cast.append(person.find("a").text.strip())
            elif role == "director":
                directors.append(person.find("a").text.strip())
            elif role == "producer":
                producers.append(person.find("a").text.strip())
            elif role == "screenwriter":
                screenwriters.append(person.find("a").text.strip())

        try:
            studio = soup.find("dd", class_="information-list__item__definition").text.strip()
        except AttributeError:
            studio = ""
        try:
            cpright = soup.find("dd", class_="information-list__item__definition information-list__item__definition--copyright").text.strip()
        except AttributeError:
            cpright = ""

        ourl="Movie URL: " + url
        ocountry="Country: " + url.split(".com/")[1][:2].upper()
        otitle="Title: " + title.text
        ordate="Release Date: " + release_date["datetime"][:10]
        orating="Rating: " + rating
        ogenre="Genre: " + genre.text
        osdescr="Short Description: " + short_description.replace("’", "'").replace("“", '"').replace("”", '"').replace("…", "...").replace("  ", " ")
        odescr="Long Description: " + description.text.replace("’", "'").replace("“", '"').replace("”", '"').replace("…", "...").replace("  ", " ")
        ocast="Cast: " + ', '.join(cast)
        odirec="Directors: " + ', '.join(directors)
        oprod="Producers: " + ', '.join(producers)
        oscreen="Screenwriters: " + ', '.join(screenwriters)
        ostudio="Studio: " + studio
        ocpright="Copyright: " + cpright
        omovieid="Movie ID: " + movieid["content"]
        spacer="---------------------------------------------------------------------------------------------------"

        output.append(ourl)
        output.append(ocountry)
        output.append(otitle)
        output.append(ordate)
        output.append(orating)
        output.append(ogenre)
        output.append(osdescr)
        output.append(odescr)
        output.append(odirec)
        output.append(oprod)
        output.append(ocast)
        output.append(oscreen)
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
        print(odirec)
        print(oprod)
        print(ocast)
        print(oscreen)
        print(ostudio)
        print(ocpright)
        print(omovieid)

        browser.close()
        print("Metadata extracted")

        print("Image URL: " + img_url)
        print("Downloading image...")
        #r = requests.get(img_url)





        r = session.get(img_url)



        filename= title.text +  ".jpg"

        fcharacters=[':', '*', '?', '"', '<', '>', '|', ' ', "'", "/"]#, '/', '\'
        for fcharacter in fcharacters:
            if fcharacter in filename:
                filename = filename.replace(fcharacter,"")

        filename=filename.lower()
        with open(filename, 'wb') as f:
            f.write(r.content)
        print("Download complete")
        print("Image saved in: " + filename)
        #time.sleep(1)


    with open('metadata.txt', 'w', encoding='utf-8') as f:
        for line in output:
            f.write("%s\n" % line)
    print("Done")


elif (mode=="2"):
    imdb_search("sourceimdb")



    for url in urls:
        print("---------------------------------------------------------------------------------------------------")
        print("Movie URL: " + "https://www.imdb.com/title/" + url.split("&i=")[1].split("&type=")[0] + "/")
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
        #description = response["Plot"]
##        cast =
        directors = response["Director"]
##        producers =
        screenwriters = response["Writer"]
##        studio =
        production_company = response["Production"]
        imdbID = response["imdbID"]
        cast=[]
        release_dates=[]
        #directors=[]
        producers=[]
        distributors=[]
        productions=[]
        ratings=[]




        cast_crew_url = "https://www.imdb.com/title/" + imdbID + "/fullcredits?ref_=tt_cl_sm#cast"
        release_info_url = "https://www.imdb.com/title/" + imdbID + "/releaseinfo?ref_=tt_ov_inf"
        company_credits_url = "https://www.imdb.com/title/" + imdbID + "/companycredits?ref_=tt_dt_co"
        ratings_url = "https://www.imdb.com/title/" + imdbID + "/parentalguide?ref_=tt_stry_pg#certification"
        plot_url = "https://www.imdb.com/title/" + imdbID + "/plotsummary?ref_=tt_ov_pl"



        result=session.get(cast_crew_url)
        src = result.content
        soup = BeautifulSoup(src, 'lxml')
        cast_list = soup.find("table", class_="cast_list")
        cast_list=cast_list.find_all("tr")
        for actor in cast_list:
            try:
                if (actor["class"][0]=="odd" or actor["class"][0]=="even"):
                    cast.append(actor.find_all("td")[1].text.strip())
            except KeyError:
                pass



        header_list = soup.find_all("h4", class_="dataHeaderWithBorder")
        try:
            if ("Produced by" in header_list[3].text):
                producers_list=soup.find_all("table", class_="simpleTable simpleCreditsTable")
                producers_list=producers_list[2].find_all("tr")
                for producer in producers_list:
                    producer=producer.find_all("td")
                    producers.append(producer[0].text.strip() + " - " + producer[2].text.strip())
        except IndexError:
            pass




        html=None
        while (html == None):
            try:
                # browser = webdriver.Firefox(executable_path = r'C:/Users/carlo/Documents/Programming-Projects/Python Scripts/iTunesMediaExtractor/geckodriver.exe')
                browser = webdriver.Chrome(service = Service(ChromeDriverManager().install()))
                browser.get(release_info_url)
                html=browser.page_source
            except WebDriverException:
                browser.close()
                time.sleep(1)

        soup = BeautifulSoup(html, 'lxml')
        # title = soup.find("h1", class_="product-header__title movie-header__title")


        # result=session.get(release_info_url)
        # src = result.content
        # soup = BeautifulSoup(src, 'lxml')
        # print(soup)
        
        # release_list = soup.find("table", class_="ipl-zebra-list ipl-zebra-list--fixed-first release-dates-table-test-only")
        release_list = browser.find_elements("xpath", "//div[@data-testid='sub-section-releases']/ul/li")
        # release_list = soup.find("ul", class_="ipc-metadata-list ipc-metadata-list--dividers-after sc-6b43c14d-0 bZVCaQ ipc-metadata-list--base")
        # release_list = release_list.find_all("tr")
        # release_list = release_list.find_all("li")
        
        for release in release_list:
            #print(release)
            # release=release.find_all("td")
            # release_dates.append(release[0].text.strip() + " - " + release[1].text)
            # release_country=release.find_all("a")[0].text.strip()
            release_country = release.find_element("xpath", "./a").text.strip()
            print("RELEASE COUNTRY:", release_country)
            
            # release_date=release.find_all("div")[0].find_all("label")[0].text.strip()
            release_date = release.find_elements("xpath", "./div")[0].find_elements("xpath", ".//label")[0].text.strip()
            print("RELEASE DATA:", release_date)
            release_dates.append(release_country + " - " + release_date)
            # time.sleep(100000)
            #print(release[0].text.strip() + " - " + release[1].text)




        # print("COMPANY CREDITS URL:", company_credits_url)
        # result=session.get(company_credits_url)
        # src = result.content
        # soup = BeautifulSoup(src, 'lxml')

        html=None
        while (html == None):
            try:
                # browser = webdriver.Firefox(executable_path = r'C:/Users/carlo/Documents/Programming-Projects/Python Scripts/iTunesMediaExtractor/geckodriver.exe')
                browser = webdriver.Chrome(service = Service(ChromeDriverManager().install()))
                browser.get(company_credits_url)
                html=browser.page_source
            except WebDriverException:
                browser.close()
                time.sleep(1)

        soup = BeautifulSoup(html, 'lxml')

        production_header = soup.find("span", id="production")
        if production_header != None:
            production_list = browser.find_elements("xpath", "//div[@data-testid='sub-section-production']/ul/li")
            for production in production_list:
                productions.append(production.text.strip().replace("            "," - "))

        distributors_header = soup.find("span", id="distribution")
        if distributors_header != None:
            distributor_list = browser.find_elements("xpath", "//div[@data-testid='sub-section-distribution']/ul/li")            
            for distributor in distributor_list:
                distributors.append(distributor.text.strip().replace("            "," - "))


        # distributors_header = soup.find("span", id="distribution")
        # if (production_header!=None and distributors_header!=None):
        #     company_list=soup.find_all("ul", class_="simpleList")
        #     production_list=company_list[0]
        #     production_list=production_list.find_all("li")
        #     distributor_list=company_list[1]
        #     distributor_list=distributor_list.find_all("li")
        #     for production in production_list:
        #         productions.append(production.text.strip().replace("            "," - "))
        #     for distributor in distributor_list:
        #         distributors.append(distributor.text.strip().replace("            "," - "))




        result=session.get(ratings_url)
        src = result.content
        soup = BeautifulSoup(src, 'lxml')
        ratings_list = soup.find("tr", id="certifications-list")
        try:
            ratings_list = ratings_list.find_all("li")
            for rating in ratings_list:
                ratings.append(rating.find("a").text)
        except AttributeError:
            pass




        # result=session.get(plot_url)
        # src = result.content
        # soup = BeautifulSoup(src, 'lxml')
        # print("PLOT URL:", plot_url)

        html=None
        while (html == None):
            try:
                # browser = webdriver.Firefox(executable_path = r'C:/Users/carlo/Documents/Programming-Projects/Python Scripts/iTunesMediaExtractor/geckodriver.exe')
                browser = webdriver.Chrome(service = Service(ChromeDriverManager().install()))
                browser.get(plot_url)
                html=browser.page_source
            except WebDriverException:
                browser.close()
                time.sleep(1)

        soup = BeautifulSoup(html, 'lxml')

        # time.sleep(100000)
        # description_list = soup.find("ul", id="plot-summaries-content")
        # print("SOUP:", soup)
        try:
            description_list = soup.find("div", attrs={"data-testid":"sub-section-summaries"}).find("ul")
            description_list = description_list.find_all("li", attrs={"role":"presentation"})[0]
            description = description_list.text.replace("’", "'").replace("“", '"').replace("”", '"').replace("…", "...").replace("  ", " ")
        except Exception as e:
            print("Exception:", str(e))
            description = "No Description Available"

        ourl="Movie URL: " + "https://www.imdb.com/title/" + imdbID + "/"
        otitle = "Title: " + title
        oyear = "Year: " + year
        odate = "Date: " + date
        omainrating = "Rating: " + main_rating
        ogenre = "Genre: " + genre
        odescription = "Description: " + description
        odirectors = "Directors: " + directors
        oproducers = "Producers: "+ ', '.join(producers)
        ocast = "Cast: " + ', '.join(cast)
        oscreenwriters = "Screenwriters: " + screenwriters
        oproductioncmpn = "Production Company: " + production_company
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


    with open('metadata.txt', 'w', encoding='utf-8') as f:
        for line in output:
            f.write("%s\n" % line)
    print("Done")












elif (mode=="3"):
    entity="tvSeason"
    itunes_search()


    for url, img_url in zip(urls, img_urls):
        print("---------------------------------------------------------------------------------------------------")
        print("TV Show URL: " + url)
        country = url.split(".com/")[1][:2].upper()
        print("Country: " + country)
        season_id = url.split("id")[1].split("?")[0]
        print("ID: " + season_id)
        print("Getting metadata...")

        season_url = "https://itunes.apple.com/lookup?id=" + season_id + "&entity=tvEpisode"
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

        


#         #browser = webdriver.Firefox(executable_path = r'C:/Users/carlo/Documents/Programming-Projects/Python Scripts/iTunesMediaExtractor/geckodriver.exe')
#         #browser.get(url)
#         #html=browser.page_source
#         html=None
#         while (html == None):
#             try:
#                 # browser = webdriver.Firefox(executable_path = r'C:/Users/carlo/Documents/Programming-Projects/Python Scripts/iTunesMediaExtractor/geckodriver.exe')
#                 browser = webdriver.Chrome(service = Service(ChromeDriverManager().install()))
#                 browser.get(url)
#                 html=browser.page_source
#             except WebDriverException:
#                 browser.close()
#                 time.sleep(1)




        # soup = BeautifulSoup(html, 'lxml')
        # print(soup)
        # time.sleep(3)
        # stitle = soup.find("h1", class_="product-header__title show-header__title").text
        stitle = season_collection["collectionName"]
        # try:
        #     rating = soup.find("svg")["aria-label"].replace(" ","-")
        # except TypeError:
        #     rating = ""
        # if (rating == ""):
        #     try:
        #         rating = soup.find("span", class_="badge").text
        #     except AttributeError:
        #         rating=""
        try:
            rating = season_collection["contentAdvisoryRating"]
        except KeyError:
            rating = ""

        # genre = soup.find("a", class_="link link--no-tint").text
        genre = season_collection["primaryGenreName"]
        # srelease_date = soup.find("time")["datetime"][:10]
        srelease_date = season_collection["releaseDate"][:10]
        # sdescription = soup.find("p", dir="ltr").text.replace("’", "'").replace("“", '"').replace("”", '"').replace("…", "...").replace("  ", " ")
        sdescription = season_collection["longDescription"]
        sdescription_html = markdown.markdown(sdescription)
        sdescription_soup = BeautifulSoup(sdescription_html, features='html.parser')
        sdescription = sdescription_soup.get_text()
        sdescription = sdescription.replace("’", "'").replace("“", '"').replace("”", '"').replace("…", "...").replace("  ", " ")
        # try:
        #     cpright = soup.find("div", class_="sosumi product-hero__tracks-sosumi").text.strip()
        # except AttributeError:
        #     cpright = ""
        cpright = season_collection["copyright"]
        # seasonid = soup.find("meta", attrs={"name":"apple:content_id"})["content"]
        seasonid = season_collection["collectionId"]


# ##    You can't use a keyword argument called name because the Beautiful Soup search methods already define a name argument.
# ##    You also can't use a Python reserved word like for as a keyword argument.
# ##    Beautiful Soup provides a special argument called attrs which you can use in these situations. attrs is a dictionary that acts just like the keyword arguments.

#         episodes = soup.find_all("li", class_="tracks__track")

#         # print("EPISODES:", episodes)

        ourl="TV Show URL: " + url
        ocountry="Country: " + url.split(".com/")[1][:2].upper()
        ostitle = "Season Title: " + stitle
        osrelease_date = "Season Release Date: " + srelease_date
        orating = "Rating: " + rating
        ogenre = "Genre: " + genre
        osdescription = "Season Description: " + sdescription
        ocpright = "Copyright: " + cpright
        oseasonid = "Season ID: " + str(seasonid)
        spacer="---------------------------------------------------------------------------------------------------"

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



        # for episode in episodes:
        for episode in episodes_list:
            # episode_id=episode.find("a", class_="link tracks__track__link l-row")["data-episode-id"]
            episode_id=episode["trackId"]
            # episode_number=episode.find("li", class_="inline-list__item inline-list__item--margin-inline-start-large tracks__track__eyebrow-item").text.strip()
            episode_number=episode["trackNumber"]


            # try:
            #     episode_title=episode.find("span", class_="we-truncate we-truncate--multi-line ember-view")["aria-label"]
            # except KeyError:
            #     episode_title=episode.find("div", class_="we-clamp ember-view").text
            
            episode_title = episode["trackName"]

            # episode_description=episode.find("p", dir="ltr").text.replace("’", "'").replace("“", '"').replace("”", '"').replace("…", "...").replace("  ", " ")

            episode_description = episode["longDescription"]
            episode_description_html = markdown.markdown(episode_description)
            episode_description_soup = BeautifulSoup(episode_description_html, features='html.parser')
            episode_description = episode_description_soup.get_text()
            episode_description = episode_description.replace("’", "'").replace("“", '"').replace("”", '"').replace("…", "...").replace("  ", " ")

            # episode_release_date=episode.find("time")["datetime"][:10]
            episode_release_date=episode["releaseDate"][:10]
            spacer2="###################################################################################################"
            oepisode_number="Episode Number: " + str(episode_number)
            oepisode_title="Episode Title: " + episode_title
            oepisode_release_date="Episode Release Date: " + episode_release_date
            oepisode_description="Episode Description: " + episode_description
            oepisode_id="Episode ID: " + str(episode_id)

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
        # browser.close()
        print("Metadata extracted")

        print("Image URL: " + img_url)
        print("Downloading image...")
        r = session.get(img_url)
        filename= stitle +  ".jpg"

        fcharacters=[':', '*', '?', '"', '<', '>', '|', ' ', "'", "/"]#, '/', '\'
        for fcharacter in fcharacters:
            if fcharacter in filename:
                filename = filename.replace(fcharacter,"")

        filename=filename.lower()
        with open(filename, 'wb') as f:
            f.write(r.content)
        print("Download complete")
        print("Image saved in: " + filename)


    with open('metadata.txt', 'w', encoding='utf-8') as f:
        for line in output:
            f.write("%s\n" % line)
    print("Done")












    #print (i)
    #for key, value in i.items():
    #    print(str(key) + ": " + str(value))
##    print(i["trackId"])
##    print(i["artistName"])
##    print(i["trackName"])
##    print(i["trackViewUrl"])
##    print(i["artworkUrl100"])
##    print(i["releaseDate"])
##    print(i["country"])
##    print(i["primaryGenreName"])
##    print(i["contentAdvisoryRating"])
##    print(i["longDescription"])
    #print("------------------------------------------------------------------------")
#print(movies_url)
