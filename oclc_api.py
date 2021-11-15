# OCLC API

import time
import os
import string
from datetime import datetime

# You will probably need to install these with pip
import requests
from diskcache import Cache
from bs4 import BeautifulSoup
import pandas as pd
from scraping_demo import Fox

def manage_api_call(row,cache,fox):

    """
    Takes a row (pandas Series) and iterates over the data needed to form URLs. If conditions are met, makes the scraping request and adds the resulting data to the row
    """

    isbn_record_found = False

    for isbn_format in ["HC_ISBN","PBK_ISBN","EBook_ISBN"]:

        if isbn_record_found == False:

            isbn = row[isbn_format]

            if not pd.isnull(isbn):

                # This is for the website and will return HTML - we do not want to use this
                # url = "http://classify.oclc.org/classify2/ClassifyDemo?search-standnum-txt=9781621064657"

                # This is for the API and will return XML
                url = "http://classify.oclc.org/classify2/Classify"

                parameters = {
                    "isbn" : isbn,
                    "summary" : "true",
                }

                fox.update(base = url, params = parameters)
                # print(fox.cache_key)
                fox.make_request(sleep=3)

                resp = cache[fox.cache_key]
                if resp.status_code != 200:
                    print("Nothing found at", resp.url)
                    print(resp.status_code)
                else:
                    print("Webpage found at", resp.url)
                    soup = BeautifulSoup(resp.text,"html.parser")


                    oclc_response_code = soup.classify.response["code"]

                    if oclc_response_code == "0":
                        work = soup.classify.work
                        print_holdings = int(work["holdings"])
                        electronic_holdings = int(work["eholdings"])
                        total_holdings = print_holdings + electronic_holdings

                    elif oclc_response_code == "4":
                        # E.g. http://classify.oclc.org/classify2/Classify?isbn=9781566395861&summary=true
                        work = soup.classify.works.work
                        total_holdings = int(work["holdings"])

                    owi = work["owi"]

                    row["OCLC Work Identifier"] = owi
                    row["Holdings Count"] = total_holdings

    return row

def manage_apply():

    """
    Handles opening the input file, opening the cache file, iterating over the input rows, and forming the output file(s)
    """

    spreadsheet = pd.read_csv("acq_long_list.csv",dtype=str)

    # Limit the length of the spreadsheet for testing
    spreadsheet = spreadsheet[91:96]

    new_headers = [
        "Title",
        "Subtitle",
        "HC_ISBN",
        "PBK_ISBN",
        "EBook_ISBN",
        "OCLC Work Identifier",
        "Holdings Count",
    ]

    spreadsheet = spreadsheet.reindex(columns = new_headers)

    with Cache("demo_cache") as cache:
        user_agent = ""
        fox = Fox()
        fox.update(
            headers = {'User-Agent':user_agent},
            cache_ref = cache,
            accept_codes=[200]
        )

        spreadsheet = spreadsheet.apply(
                lambda row : manage_api_call(row,cache,fox),
                axis=1
            )

    print(spreadsheet)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    outdir = "outputs"
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    spreadsheet.to_csv(f"{outdir}/{timestamp}_output.csv",index=False)

    # new_document.save(f"{outdir}/{timestamp}_output.docx")
    print("Output files created")

if __name__ == '__main__':
    manage_apply()
