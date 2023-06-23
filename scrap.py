"""
1. define the urls
2. get the cookies
2. get the countries
3. loop over them and save their leaders in a dictionary
4. return the dictionary
"""
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
        leader_text = r.text
        soup = BeautifulSoup(leader_text,"html.parser")
        paragraphs = soup.find_all('p')
        for x in paragraphs:
            if str(x).startswith('<p><b>'):
                first_paragraph = str(x)   # can remove and put str(x below as parameter)
                first_paragraph = re.sub("[\n]","",first_paragraph)
                first_paragraph = re.sub("<.*?>","",first_paragraph)
                break
    else:
        r = session.get(root_url + cookie_url)
        cookies = r.cookies
        r = session.get(wikipedia_url, cookies=cookies)
        leader_text = r.text
        soup = BeautifulSoup(leader_text,"html.parser")
        paragraphs = soup.find_all('p')
        for x in paragraphs:
            if str(x).startswith('<p><b>'):
                first_paragraph = str(x)
                first_paragraph = re.sub("[\n]","",first_paragraph)
                first_paragraph = re.sub("<.*?>","",first_paragraph)
                break
    return first_paragraph

def get_leaders():
    """
    Function that gets list of countries, loops over them and saves their leades in a dictionary. 
    """
    s = requests.Session()
    leaders_per_country = {}
    r = s.get(root_url + cookie_url)
    cookies = r.cookies
    r = s.get(root_url + countries_url, cookies=cookies)
    countries = r.json()
    for x in (countries):
        r = s.get(root_url + leaders_url + "?country=" + x, cookies=cookies)
        if r.status_code == 200:
            result = r.json()
            leaders_per_country[x] = result
        else:
            r = s.get(root_url + cookie_url)
            cookies = r.cookies
            r = s.get(root_url + leaders_url + "?country=" + x, cookies=cookies)
            result = r.json()
            leaders_per_country[x] = result
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

leaders = get_leaders()
save(leaders)