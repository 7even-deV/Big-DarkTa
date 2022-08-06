from bs4 import BeautifulSoup
from random import random
from time import sleep
import requests
import csv
import re


def generate_url(country_code, country):
    url = f"https://{country_code}.indeed.com/jobs?q=data%20scientist&l={country}"
    return url


def save_record_to_csv(record, filepath, create_new_file=False):
    """Save an individual record to file; set `new_file` flag to `True` to generate new file"""
    header = ["job_title", "company", "location", "job_summary",
                "post_date", "more_info", "salary", "job_url"]
    if create_new_file:
        with open(filepath, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(header)
    else:
        with open(filepath, mode='a+', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(record)


def collect_job_cards_from_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    cards = soup.find_all('div', 'job_seen_beacon')

    return cards, soup


def sleep_for_random_interval():
    seconds = random() * 10
    sleep(seconds)


def request_jobs_from_indeed(url):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                'AppleWebKit/537.11 (KHTML, like Gecko) '
                'Chrome/23.0.1271.64 Safari/537.11',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                'Accept-Encoding': 'none',
                'Accept-Language': 'en-US,en;q=0.8',
                'Connection': 'keep-alive'}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        return None


def find_next_page(country_code, country, index):
    try:
        base_url = f"https://{country_code}.indeed.com"
        pattern_url = f"/jobs?q=data+scientist&l={country}&start={index}0"

        new_url = base_url + pattern_url

        return new_url

    except AttributeError as e:
        return print(e)


def extract_job_card_data(card):
    atag = card.h2.a
    try:
        job_title = card.find("h2", "jobTitle").text.strip()
    except AttributeError:
        job_title = ''
    try:
        company = card.find('span', 'companyName').text.strip()
    except AttributeError:
        company = ''
    try:
        location = card.find('div', 'companyLocation').text.strip()
    except AttributeError:
        location = ''
    try:
        job_summary = card.find('div', 'job-snippet').text.strip()
    except AttributeError:
        job_summary = ''
    try:
        post_date = card.find('span', 'date').text.strip()
    except AttributeError:
        post_date = ''

    try:
        more_info = card.find('div', "attribute_snippet").text.strip()
    except AttributeError:
        more_info = ''
    try:
        salary = card.find('div', 'salary-snippet-container').text.strip()
    except AttributeError:
        salary = ''

    job_url = 'https://www.indeed.com' + atag.get('href')
    return job_title, company, location, job_summary, post_date, more_info, salary, job_url


def main(country_code, country, filepath, total_jobs):
    unique_jobs = set()  # Track job urls to avoid collecting duplicate records
    pages = total_jobs // 15 if total_jobs >= 15 else 1
    print(f"\n>> Starting to scrape indeed {total_jobs} jobs in {pages} pages of {country}.\n")

    country_name = country
    if country == "España":
        country = "Espa%C3%B1a"
    else: country = country.replace(" ", "%20")

    url = generate_url(country_code, country)
    save_record_to_csv(None, filepath, create_new_file=True)
    i = 1

    while True:
        if i > pages:
            break
        print(f"Scrapping page {i} from {url}.")
        html = request_jobs_from_indeed(url)
        if not html:
            break
        cards, soup = collect_job_cards_from_page(html)
        for card in cards:
            record = extract_job_card_data(card)
            if not record[-1] in unique_jobs:
                save_record_to_csv(record, filepath)
                unique_jobs.add(record[-1])
        sleep_for_random_interval()
        url = find_next_page(country_code, country, i)
        print(f"Finished collecting {len(unique_jobs):,d}/{total_jobs} job postings from page {i}/{pages} of {country_name}.\n")
        i += 1

    print(f"<< The compilation of {country_name} with {len(unique_jobs):,d} job postings was created in {filepath}.")

def run(data_dict):
    for i in range(len(data_dict)):

        country_code = list(data_dict.keys())[i]
        country = list(data_dict.values())[i][0]
        total_jobs = list(data_dict.values())[i][1]

        country_name = country.replace(" ", "-")
        filepath = f"./assets/scrapper/output/output_{country_name}.csv"

        main(country_code, country, filepath, total_jobs)

    print("\n<<< The scrapper has completely finished. >>>")


if __name__ == '__main__':
    # Job search settings
    data_dict = {
        # "ar": ["Argentina", 118],
        # "au": ["Australia", 394],
        # "at": ["Austria", 130],
        # "bh": ["Bahrain", 0],
        # "in": ["India", 3628],
        # "id": ["Indonesia", 227],
        # "il": ["Israel", 519],
        # "pt": ["Portugal", 424],
        # "qa": ["Qatar", 5],
        # "ro": ["Romania", 103],
        # "sa": ["Saudi Arabia", 30],

        # "be": ["Belgium", 558],
        # "br": ["Brazil", 294],
        # "ca": ["Canada", 1387],
        # "cl": ["Chile", 101],
        # "it": ["Italy", 461],
        # "jp": ["Japan", 125],
        # "kw": ["Kuwait", 47],
        # "lu": ["Luxembourg", 182],
        # "sg": ["Singapore", 1067],
        # "za": ["South Africa", 267],
        # "kr": ["South Korea", 184],
        # "es": ["Spain", 932],

        # "cn": ["China", 630],
        # "co": ["Colombia", 120],
        # "cr": ["Costa Rica", 45],
        # "cz": ["Czech Republic", 82],
        # "my": ["Malaysia", 355],
        # "mx": ["Mexico", 256],
        # "ma": ["Morocco", 93],
        # "nl": ["Netherlands", 1477],
        # "se": ["Sweden", 234],
        # "ch": ["Switzerland", 425],
        # "tw": ["Taiwan", 119],
        # "th": ["Thailand", 130],

        # "dk": ["Denmark", 206],
        # "ec": ["Ecuador", 26],
        # "eg": ["Egypt", 36],
        # "fi": ["Finland", 54],
        # "nz": ["New Zealand", 143],
        # "ng": ["Nigeria", 55],
        # "no": ["Norway", 106],
        # "om": ["Oman", 13],
        # "tr": ["Turkey", 32],
        # "ua": ["Ukraine", 56],
        # "ae": ["United Arab Emirates", 141],
        # "uk": ["United Kingdom", 2256],

        # "fr": ["France", 1878],
        # "de": ["Germany", 1946],
        # "gr": ["Greece", 60],
        # "hk": ["Hong Kong", 276],
        # "pk": ["Pakistan", 48],
        # "pa": ["Panama", 16],
        # "pe": ["Peru", 38],
        # "ph": ["Philippines", 312],
        # "es": ["United States", 24309],
        # "uy": ["Uruguay", 25],
        # "ve": ["Venezuela", 12],
        # "vn": ["Vietnam", 105],
    }

    run(data_dict)
