import requests, json
from bs4 import BeautifulSoup
from selenium import webdriver

urls=[]
img_urls=[]
search_terms=[]
output=[]
def search():
    search_term = input("Enter search term (type 0 when you're done): ")
    if (search_term != "0"):
        search_terms.append(search_term)
        search()
    else:
        print(str(len(search_terms)) + " search terms added")
        
print("Welcome to the iTunesMediaExtractor")
print("Made by Carlos Martinez")
search()



for search_term in search_terms:
    print("---------------------------------------------------------------------------------------------------")
    print("Search results for: " + search_term)
    movie_url = 'https://itunes.apple.com/search?term=' + search_term + '&country=us&entity=movie'
    response = requests.get(movie_url)
    response.raise_for_status()
    response = response.json()

    counter=1
    search_results=[]
    for item in response["results"]:
        try:
            print(str(counter)+ ": " + item["trackName"])
            counter+=1
            search_results.append(item)
        except KeyError:
            pass

    choice_number = input("Choose an item number: ")
    print("Item chosen: " + search_results[int(choice_number)-1]["trackName"])
    url=search_results[int(choice_number)-1]["trackViewUrl"]
    urls.append(url)
    imgurl=(search_results[int(choice_number)-1]["artworkUrl100"]).replace("100x100bb", "100000x100000-999")
    img_urls.append(imgurl)






for url, img_url in zip(urls, img_urls):
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
    ordate="Release Date: " + release_date["datetime"]
    orating="Rating: " + rating["aria-label"]
    ogenre="Genre: " + genre.text
    odescr="Description: " + description.text.replace("’", "'").replace("“", '"').replace("”", '"')
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
    output.append(odescr)
    output.append(ocast)
    output.append(odirec)
    output.append(oprod)
    output.append(oscreen)
    output.append(ostudio)
    output.append(ocpright)
    output.append(spacer)

        
    print("Title: " + title.text)
    print("Release Date: " + release_date["datetime"])
    print("Rating: " + rating["aria-label"])
    print("Genre: " + genre.text)
    print("Description: " + description.text.replace("’", "'").replace("“", '"').replace("”", '"'))
    print("Cast: " + ', '.join(cast))
    print("Directors: " + ', '.join(directors))
    print("Producers: " + ', '.join(producers))
    print("Screenwriters: " + ', '.join(screenwriters))
    print("Studio: " + studio)
    print("Copyright: " + cpright)

    browser.close()
    print("Metadata extracted")

    print("Image: " + img_url)
    print("Downloading image...")    
    r = requests.get(img_url)
    #print(url)
    #print(img_url)
    filename= title.text +  ".jpg"

    fcharacters=[':', '*', '?', '"', '<', '>', '|', ' ']#, '/', '\'
    for fcharacter in fcharacters:
        if fcharacter in filename:
            filename = filename.replace(fcharacter,"")
                                                                      
    filename=filename.lower()
    #print(filename)
    
    with open(filename, 'wb') as f:
        f.write(r.content)
    print("Download complete")
    
    
with open('metadata.txt', 'w') as f:
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
