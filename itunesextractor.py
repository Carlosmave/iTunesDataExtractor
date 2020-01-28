import requests, json, sys
from bs4 import BeautifulSoup
from selenium import webdriver

mode=""
urls=[]
img_urls=[]
short_descriptions=[]
search_terms=[]
output=[]
apikey="e6fa56aa"

def movie_mode():
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
        choice_number = input("Choose an item number: ")
    except KeyboardInterrupt:
        sys.exit()
    try:
        choice=search_results[int(choice_number)-1]
        return choice
    except IndexError:
        print("The chosen number is not in the list")
        return choose(search_results)
    except ValueError:
        print("Please insert a number")
        return choose(search_results)


def imdb_search(search_term):
    if (search_term!="sourceimdb"):
        imdb_url = 'http://www.omdbapi.com/?apikey=' + apikey + '&s=' + search_term + '&type=movie'
        response = requests.get(imdb_url)
        response.raise_for_status()
        response = response.json()
        if response["Response"]=="True":
            i=1
            counter=1
            imdb_search_results=[]
            while(i<5):
                imdb_url = 'http://www.omdbapi.com/?apikey=' + apikey + '&s=' + search_term + '&type=movie&page=' + str(i)
                response = requests.get(imdb_url)
                response.raise_for_status()
                response = response.json()
                try:
                    for item in response["Search"]:
                        print(str(counter)+ ": " + item["Title"] + " - " + item["Year"])
                        counter+=1
                        imdb_search_results.append(item)
                except KeyError:
                    pass
                i+=1
            imdb_choice=choose(imdb_search_results)
            print("Item chosen: " + imdb_choice["Title"]  + " - " + imdb_choice["Year"])
            imdb_id=imdb_choice["imdbID"]
            imdb_url = 'http://www.omdbapi.com/?apikey=' + apikey + '&i=' + imdb_id + '&type=movie'
            response = requests.get(imdb_url)
            response.raise_for_status()
            response = response.json()
            short_descriptions.append(response["Plot"])
            print("---------------------------------------------------------------------------------------------------")
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
            imdb_url = 'http://www.omdbapi.com/?apikey=' + apikey + '&s=' + search_term + '&type=movie'
            response = requests.get(imdb_url)
            response.raise_for_status()
            response = response.json()
            if response["Response"]=="True":
                print("---------------------------------------------------------------------------------------------------")
                print("Search results on IMDb for: " + search_term)
                i=1
                counter=1
                imdb_search_results=[]
                while(i<5):
                    imdb_url = 'http://www.omdbapi.com/?apikey=' + apikey + '&s=' + search_term + '&type=movie&page=' + str(i)
                    response = requests.get(imdb_url)
                    response.raise_for_status()
                    response = response.json()
                    try:
                        for item in response["Search"]:
                            print(str(counter)+ ": " + item["Title"] + " - " + item["Year"])
                            counter+=1
                            imdb_search_results.append(item)
                    except KeyError:
                        pass
                    i+=1
                imdb_choice=choose(imdb_search_results)
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


def itunes_search():
    try:
        search_term = input("Enter search term (type 0 when you're done): ")
    except KeyboardInterrupt:
        sys.exit()
    if (search_term != "0" and search_term != ""):
        movie_url = 'https://itunes.apple.com/search?term=' + search_term + '&country=us&entity=movie'
        response = requests.get(movie_url)
        response.raise_for_status()
        response = response.json()
        if response["results"]:
            print("---------------------------------------------------------------------------------------------------")
            print("Search results on iTunes for: " + search_term)

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
            print("Item chosen: " + choice["trackName"]  + " - " + choice["releaseDate"][:4])
            url=choice["trackViewUrl"]
            urls.append(url)
            imgurl=(choice["artworkUrl100"]).replace("100x100bb", "100000x100000-999")
            img_urls.append(imgurl)
            
            if (mode=="1"):
                print("---------------------------------------------------------------------------------------------------")
                print("Search results on IMDb for: " + search_term)
                imdb_search(choice["trackName"])
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
    itunes_search()


    for url, img_url, short_description in zip(urls, img_urls, short_descriptions):
        #result=requests.get(url)
        #src = result.content
        #soup = BeautifulSoup(src, 'lxml')
        #Se puede ver que la sección information viene de un JavaScript yendo a la sección "Sources" en el buscador, por eso no se puede obtener mediante requests. Para que se ejecute el JavaScript
        #y aparezca la información completa de forma scrapeable, se debe abrir el link en un buscador. Para eso se utilizó Selenium.
        print("---------------------------------------------------------------------------------------------------")
        print("Item: " + url)
        print("Getting metadata...")
            
        browser = webdriver.Firefox(executable_path = r'C:/Users/carlo/Documents/Programming-Projects/Python Scripts/iTunesMediaExtractor/geckodriver.exe')
        browser.get(url)
        html=browser.page_source
            
            


        soup = BeautifulSoup(html, 'lxml')
        title = soup.find("h1", class_="product-header__title movie-header__title")
        rating = soup.find("svg")
        genre = soup.find("a", class_="link link--no-tint")
        release_date = soup.find("time")
        description = soup.find("p")
        crew = soup.find_all("dd", class_="cast-list__detail")
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


        otitle="Title: " + title.text
        ordate="Release Date: " + release_date["datetime"][:10]
        orating="Rating: " + rating["aria-label"].replace(" ","-")
        ogenre="Genre: " + genre.text
        osdescr="Short Description: " + short_description.replace("’", "'").replace("“", '"').replace("”", '"')
        odescr="Long Description: " + description.text.replace("’", "'").replace("“", '"').replace("”", '"')
        ocast="Cast: " + ', '.join(cast)
        odirec="Directors: " + ', '.join(directors)
        oprod="Producers: " + ', '.join(producers)
        oscreen="Screenwriters: " + ', '.join(screenwriters)
        ostudio="Studio: " + studio
        ocpright="Copyright: " + cpright
        spacer="---------------------------------------------------------------------------------------------------"

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

        browser.close()
        print("Metadata extracted")

        print("Image: " + img_url)
        print("Downloading image...")    
        r = requests.get(img_url)
        filename= title.text +  ".jpg"

        fcharacters=[':', '*', '?', '"', '<', '>', '|', ' ']#, '/', '\'
        for fcharacter in fcharacters:
            if fcharacter in filename:
                filename = filename.replace(fcharacter,"")
                                                                          
        filename=filename.lower()
        with open(filename, 'wb') as f:
            f.write(r.content)
        print("Download complete")
        print("Image saved in: " + filename)
        
        
    with open('metadata.txt', 'w') as f:
        for line in output:
            f.write("%s\n" % line)
    print("Done")


elif (mode=="2"):
    imdb_search("sourceimdb")



    for url in urls:
        print("---------------------------------------------------------------------------------------------------")
        print("Item: " + url)
        print("Getting metadata...")
        response = requests.get(url)
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


        
        result=requests.get(cast_crew_url)
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
        



        result=requests.get(release_info_url)
        src = result.content
        soup = BeautifulSoup(src, 'lxml')
        release_list = soup.find("table", class_="ipl-zebra-list ipl-zebra-list--fixed-first release-dates-table-test-only")
        release_list = release_list.find_all("tr")
        for release in release_list:
            #print(release)
            release=release.find_all("td")
            release_dates.append(release[0].text.strip() + " - " + release[1].text)
            #print(release[0].text.strip() + " - " + release[1].text)

        



        result=requests.get(company_credits_url)
        src = result.content
        soup = BeautifulSoup(src, 'lxml')
        production_header = soup.find("h4", id="production")
        distributors_header = soup.find("h4", id="distributors")
        if (production_header!=None and distributors_header!=None):
            company_list=soup.find_all("ul", class_="simpleList")
            production_list=company_list[0]
            production_list=production_list.find_all("li")
            distributor_list=company_list[1]
            distributor_list=distributor_list.find_all("li")
            for production in production_list:
                productions.append(production.text.strip().replace("            "," - "))
            for distributor in distributor_list:
                distributors.append(distributor.text.strip().replace("            "," - "))


        

        result=requests.get(ratings_url)
        src = result.content
        soup = BeautifulSoup(src, 'lxml')
        ratings_list = soup.find("tr", id="certifications-list")
        try:
            ratings_list = ratings_list.find_all("li")
            for rating in ratings_list:
                ratings.append(rating.find("a").text)
        except AttributeError:
            pass

        


        result=requests.get(plot_url)
        src = result.content
        soup = BeautifulSoup(src, 'lxml')
        description_list = soup.find("ul", id="plot-summaries-content")
        description_list = description_list.find_all("li")
        description = description_list[0].find("p").text.replace("’", "'").replace("“", '"').replace("”", '"')



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
        

    with open('metadata.txt', 'w') as f:
        for line in output:
            f.write("%s\n" % line)
    print("Done")
        










    
elif (mode=="3"):
    print("ddd")




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
