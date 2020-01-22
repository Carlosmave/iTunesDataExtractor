import requests, json
from bs4 import BeautifulSoup
from selenium import webdriver

urls=[]
imgurls=[]


input_var = input("Enter something: ")
#print ("you entered " + input_var)
#input_var = input_var.strip()
#input_var = input_var.replace(" ", "+")
#movies_url = 'https://itunes.apple.com/search?term=harry+potter&limit=25'
#movies_url = 'https://itunes.apple.com/search?term=harry+potter&entity=movie'
movies_url = 'https://itunes.apple.com/search?term=' + input_var + '&country=us&entity=movie'
response = requests.get(movies_url)
response.raise_for_status()
data10 = response.json()

contador=1
resultados=[]
for i in data10["results"]:
    print(str(contador)+ ": " + i["trackName"])
    contador+=1
    resultados.append(i)

input_var2 = input("Choose number: ")
print(resultados[int(input_var2)-1]["trackName"])
urls.append(resultados[int(input_var2)-1]["trackViewUrl"])
imgurl=(resultados[int(input_var2)-1]["artworkUrl100"]).replace("100x100bb", "100000x100000-999")
imgurls.append(imgurl)
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





for url, imgurl in zip(urls, imgurls):
    #result=requests.get(url)
    #src = result.content
    #soup = BeautifulSoup(src, 'lxml')

    #Se puede ver que la sección information viene de un JavaScript yendo a la sección "Sources" en el buscador, por eso no se puede obtener mediante requests. Para que se ejecute el JavaScript
    #y aparezca la información completa de forma scrapeable, se debe abrir el link en un buscador. Para eso se utilizó Selenium.
    
    browser = webdriver.Firefox(executable_path = r'C:/Users/carlo/Documents/Programming-Projects/Python Scripts/iTunesMediaExtractor/geckodriver.exe')
    browser.get(url)
    html=browser.page_source
    
    


    soup = BeautifulSoup(html, 'lxml')
    title = soup.find("h1", class_="product-header__title movie-header__title")
    rating = soup.find("svg")
    genre = soup.find("a", class_="link link--no-tint")
    releasedate = soup.find("time")
    description = soup.find("p")
    crew = soup.find_all("dd", class_="cast-list__detail")
    cast=[]
    directors=[]
    producers=[]
    screenwriters=[]

    for person in crew: 
        test2=person.find("a")
        test2=test2["data-metrics-click"]
        test2=json.loads(test2)
        test2=test2["actionDetails"]
        role=test2["type"]
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
    
    print("Title: " + title.text)
    print("Release Date: " + releasedate["datetime"])
    print("Rating: " + rating["aria-label"])
    print("Genre: " + genre.text)
    print("Description: " + description.text)
    print("Cast: " + ', '.join(cast))
    print("Directors: " + ', '.join(directors))
    print("Producers: " + ', '.join(producers))
    print("Screenwriters: " + ', '.join(screenwriters))

    print("Studio: " + studio)
    print("Copyright: " + cpright)

    browser.close()
    
    
    r = requests.get(imgurl)
    print(url)
    print(imgurl)
    filename= title.text +  ".jpg"

    pcharacters=[':', '*', '?', '"', '<', '>', '|', ' ']#, '/', '\'
    for pcharacter in pcharacters:
        if pcharacter in filename:
            filename = filename.replace(pcharacter,"")
                                                                  
    filename=filename.lower()
    print(filename)
    with open(filename, 'wb') as f:
        f.write(r.content)
    
    
    


