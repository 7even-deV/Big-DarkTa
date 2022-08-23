'''Import necessary libraries'''

# Standard libraries
import json
import os
from datetime import datetime
from time import time
import csv
# 3rd-party libraries
import enlighten
# Custom functions
from packages.common import requestAndParse
from packages.page import extract_maximums, extract_listings
from packages.listing import extract_listing


# Loads user defined parameters
def load_configs(path, country):
    with open(path) as config_file:
        configurations = json.load(config_file)

    base_url = configurations['base_url_' + country]
    target_num = int(configurations["target_num"])
    return base_url, target_num


# Appends list of tuples in specified output csv file
# a tuple is written as a single row in csv file
def fileWriter(listOfTuples, output_fileName):
    with open(output_fileName, 'a', newline='') as out:
        csv_out = csv.writer(out)
        for row_tuple in listOfTuples:
            try:
                csv_out.writerow(row_tuple)
                # Can also do csv_out.writerows(data) instead of the for loop
            except Exception as e:
                print(f"[WARN] In fileWriter: {e}")


# Updates url according to the page_index desired
def updateUrl(prev_url, page_index):
    if page_index == 1:
        prev_substring = ".htm"
        new_substring = "_IP" + str(page_index) + ".htm"
    else:
        prev_substring = "_IP" + str(page_index - 1) + ".htm"
        new_substring = "_IP" + str(page_index) + ".htm"

    new_url = prev_url.replace(prev_substring, new_substring)
    return new_url


def main(data, country):
    base_url, target_num = load_configs(path="assets/scrapper/glassdoor/data/" + data, country=country)

    # Initialize output directory and file
    if not os.path.exists('assets/scrapper/glassdoor/output'):
        os.makedirs('assets/scrapper/glassdoor/output')
    now = datetime.now()  # Current date and time
    output_fileName = "./assets/scrapper/glassdoor/output/glassdoor_" + \
        now.strftime("%d_%m_%Y") + ".csv"
    csv_header = [("companyName", "company_starRating", "company_offeredRole",
                    "company_roleLocation", "listing_jobDesc", "requested_url")]
    fileWriter(listOfTuples=csv_header, output_fileName=output_fileName)

    maxJobs, maxPages = extract_maximums(base_url)
    # print("[INFO] Maximum number of jobs in range: {}, number of pages in range: {}".format(maxJobs, maxPages))
    if (target_num >= maxJobs):
        print("[ERROR] Target number larger than maximum number of jobs. Exiting program...\n")
        os._exit(0)

    # Initialize enlighten_manager
    enlighten_manager = enlighten.get_manager()
    progress_outer = enlighten_manager.counter(
        total=target_num, desc="Total progress", unit="listings", color="green", leave=False)

    # Initialize variables
    page_index = 1
    total_listingCount = 0

    # Initialize prev_url as base_url
    prev_url = base_url

    while total_listingCount <= target_num:
        # Clean up buffer
        list_returnedTuple = []

        new_url = updateUrl(prev_url, page_index)
        page_soup, _ = requestAndParse(new_url)
        listings_set, jobCount = extract_listings(page_soup)
        progress_inner = enlighten_manager.counter(total=len(
            listings_set), desc="Listings scraped from page", unit="listings", color="blue", leave=False)

        print(f"\n[INFO] Processing page index {page_index}: {new_url}")
        print(f"[INFO] Found {jobCount} links in page index {page_index}")

        for listing_url in listings_set:
            # To implement cache here
            returned_tuple = extract_listing(listing_url)
            list_returnedTuple.append(returned_tuple)
            # print(returned_tuple)
            progress_inner.update()

        progress_inner.close()

        fileWriter(listOfTuples=list_returnedTuple,
                    output_fileName=output_fileName)

        # Done with page, moving onto next page
        total_listingCount = total_listingCount + jobCount
        print(f"[INFO] Finished processing page index {page_index}; Total number of jobs processed: {total_listingCount}")
        page_index = page_index + 1
        prev_url = new_url
        progress_outer.update(jobCount)

    progress_outer.close()


def run():
    country_list = [
        "spain",
        "india",
        "singapore"
    ]

    file_list = os.listdir("assets/scrapper/glassdoor/data/")
    for data in file_list:
        for country in country_list:
            main(data, country)


if __name__ == '__main__':
    run()
