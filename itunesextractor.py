import requests, json
from bs4 import BeautifulSoup
from selenium import webdriver

urls=["https://itunes.apple.com/us/movie/devil/id396826065", "https://itunes.apple.com/us/movie/dinosaur/id296353403"]
for url in urls:
    #result=requests.get(url)
    #src = result.content
    #soup = BeautifulSoup(src, 'lxml')

    #Se puede ver que la sección information viene de un JavaScript yendo a la sección "Sources" en el buscador, por eso no se puede obtener mediante requests. Para que se ejecute el JavaScript
    #y aparezca la información completa de forma scrapeable, se debe abrir el link en un buscador. Para eso se utilizó Selenium.
    
    browser = webdriver.Firefox(executable_path = r'C:/Users/carlo/Documents/Programming-Projects/Python Scripts/iTunesExtractor/geckodriver.exe')
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

    studio = soup.find("dd", class_="information-list__item__definition")
    cpright = soup.find("dd", class_="information-list__item__definition information-list__item__definition--copyright")
    
    print("Title: " + title.text)
    print("Release Date: " + releasedate["datetime"])
    print("Rating: " + rating["aria-label"])
    print("Genre: " + genre.text)
    print("Description: " + description.text)
    print("Cast: " + ', '.join(cast))
    print("Directors: " + ', '.join(directors))
    print("Producers: " + ', '.join(producers))
    print("Screenwriters: " + ', '.join(screenwriters))

    print("Studio: " + studio.text.strip())
    print("Copyright: " + cpright.text.strip())

    browser.close()


input_var = input("Enter something: ")
print ("you entered " + input_var)
    
    


