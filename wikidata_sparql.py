# ORCID API with SPARQL

import time
import os
import string
from datetime import datetime
import requests
from diskcache import Cache
from bs4 import BeautifulSoup
import pandas as pd

import sys
from typing import ClassVar
from SPARQLWrapper import SPARQLWrapper, JSON

def talk_to_sparql(id, id_label):
    endpoint_url = "https://query.wikidata.org/sparql"
    id = id.split("/")[-1]
    if id_label == "VIAF_ID":
        sparql_code = "wdt:P214"
    elif id_label == "LCCN":
        sparql_code = "wdt:P244"

    query = """select ?person ?personLabel ?personDescription ?orcid ?viaf
    WHERE { ?person wdt:P31 wd:Q5. ?person wdt:P496 ?orcid . ?person SPARQL_CODE "ID_VALUE" .
    service wikibase:label { bd:serviceParam wikibase:language "en". }
    }"""

    query = query.replace("SPARQL_CODE", sparql_code)

    query = query.replace("ID_VALUE", id)

    #print(query)

    def get_results(endpoint_url, query):
        user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
        # TODO adjust user agent; see https://w.wiki/CX6
        sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        return sparql.query().convert()

    cache_key = make_cache_key(base = query, params = {})

    with Cache("wikidata_cache") as cache_ref:

        if cache_key in cache_ref:
            results = cache_ref[cache_key]
        else:
            time.sleep(2)
            results = get_results(endpoint_url, query)
            cache_ref[cache_key] = results
    for result in results["results"]["bindings"]:
        if "orcid" in result:
            if "value" in result["orcid"]:
                return result["orcid"]["value"]

def make_cache_key(base, params, private_keys=['key']):
    kvs = []
    alpha_keys = sorted(params.keys())
    for k in alpha_keys:
        if k not in private_keys:
            kvs.append(f'{k}={params[k]}')
    return base + '?' + '&'.join(kvs)

def manage_api_call(row,cache):

    """
    Takes a row (pandas Series) and iterates over the data needed to form URLs.
    If conditions are met, makes the scraping request and adds the resulting data to the row
    """

    orcid_found = False

    for id_label in ["VIAF_ID", "LCCN"]:

        if orcid_found == False:

            id = row[id_label]

            if not pd.isnull(id):
                orcid = talk_to_sparql(id, id_label)
                if not pd.isnull(orcid):
                    row["ORCID_ID"] = orcid
                    orcid_found = True
    return row

def manage_apply():

    """
    Handles opening the input file, opening the cache file, iterating over the input rows, and forming the output file(s)
    """

    spreadsheet = pd.read_csv("author_data_consolidated.csv",dtype=str) # change to "author_data_consolidated.csv"

    # Limit the length of the spreadsheet for testing
    spreadsheet = spreadsheet[:1000]

    new_headers = [

        "VIAF_ID",
        "ORCID_ID",
        "LCCN",
    ]

    spreadsheet = spreadsheet.reindex(columns = new_headers)
    print(spreadsheet)

    with Cache("demo_cache") as cache:

        spreadsheet = spreadsheet.apply(
                lambda row : manage_api_call(row,cache),
                axis=1
            )

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    outdir = "outputs"
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    spreadsheet.to_csv(f"{outdir}/{timestamp}_output.csv",index=False)

    print("Output files created")

if __name__ == '__main__':
    manage_apply()
