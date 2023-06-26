from bs4 import BeautifulSoup
import requests
import re
import json
root_url = "https://country-leaders.onrender.com"
countries_url = "/countries"
cookie_url  =  "/cookie"
leaders_url = "/leaders"

def get_first_paragraph(wikipedia_url, session):
    """
    Function that gets first paragraph from the wikipedia article from provided wikipedia_url and clears the paragraph with RegEx.
    """
    first_paragraph = ""
    r = session.get(wikipedia_url)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text,"html.parser")
        paragraphs = soup.find_all('p')
        for x in paragraphs:
            if str(x).startswith('<p><b>'):
                first_paragraph = re.sub("[\n]","",str(x))
                first_paragraph = re.sub("<.*?>","",str(x))
                break
    else:
        r = session.get(root_url + cookie_url)
        r = session.get(wikipedia_url, cookies=r.cookies)
        soup = BeautifulSoup(r.text,"html.parser")
        paragraphs = soup.find_all('p')
        for x in paragraphs:
            if str(x).startswith('<p><b>'):
                first_paragraph = re.sub("[\n]","",str(x))
                first_paragraph = re.sub("<.*?>","",str(x))
                break
    return first_paragraph

def get_leaders():
    """
    Function that gets list of countries, loops over them and saves their leades in a dictionary. 
    """
    s = requests.Session()
    leaders_per_country = {}
    r = s.get(root_url + cookie_url)
    r = s.get(root_url + countries_url, cookies=r.cookies)
    countries = r.json()
    for x in (countries):
        r = s.get(root_url + leaders_url + "?country=" + x)
        if r.status_code == 200:
            leaders_per_country[x] = r.json()
        else:
            r = s.get(root_url + cookie_url)
            r = s.get(root_url + leaders_url + "?country=" + x, cookies=r.cookies)
            leaders_per_country[x] = r.json()
    for x in leaders_per_country:
        for i,y in enumerate(leaders_per_country[x]):
            wikipedia_url = leaders_per_country[x][i]['wikipedia_url']
            leaders_per_country[x][i]['first_par'] = get_first_paragraph(wikipedia_url,s)
    return(leaders_per_country)

def save(leaders_per_country):
    """
    Function to save results as json output file.
    """
    json_object = json.dumps(leaders_per_country, ensure_ascii=False, indent = 4)
    with open("./output.txt","w") as outputfile:
        outputfile.write(json_object)

save(get_leaders())