# Using Web Scraping to Enrich Metadata

Watch the [3-minute YouTube video from the Library Publishing Forum, May 13, 2021](https://youtu.be/rRhX2R1f_Wc).

## Context and rationale
At the University of Michigan Library we manage [ACLS Humanities E-Book](https://www.fulcrum.org/heb), a collection of over 5,000 foundational books in the humanities mostly published by North American university presses, with whom we partner to license the collection. We are enriching the metadata as part of our current Mellon grant. Some of the data we want, like book descriptions, is missing, but we know it's public elsewhere on the internet, including on many university press websites.

We could copy and paste it manually, asking one of our student employees to visit 5,000 individual web pages and copy the text over into a spreadsheet or a document.

But there is a more elegant solution, web scraping. You can think of web scraping like automated copy-pasting. You use a programming language like Python or a data cleaning application like OpenRefine to go onto the internet, without opening your browser, lift text from web pages you name, and save it all in one file on your computer.

How did we decide this method was best for our project? We worked through these questions:
1. Is web scraping technically feasible? You need to have someone on your project with some programming or data curation expertise. If you don't have this yourself, try teaming up with a metadata librarian, a digital scholarship librarian, or someone in information technology. Also, the website you want to collect data from matters--some websites aren't structured in the right way, and some websites have ways of blocking web scraping scripts.
2. Is web scraping ethical in this case? If the data is sensitive or the creator community is vulnerable, you might need to get research ethics approval, and if the data is copyrighted, you'd need to contact the copyright holder.
3. Does web scraping provide efficiency at scale? If you only have a few records, your time is better spent doing the work manually than getting the automated process up and running.

In our case, we found web scraping was just the right sauce for getting book descriptions. We have the right combination of skills on our team, the websites are often structured the right way, the data is not sensitive, the university presses and authors who wrote the descriptions are our partners in this collection, and with over 5,000 books, we have the scale to make automation worthwhile.

Like a lot of people, I'm skeptical of technical methods proposed as magical solutions with no negative side effects. I want to avoid framing web scraping as "technoheroic", to use a [term from Catherine D'Ignazio](https://data-feminism.mitpress.mit.edu/pub/frfa9szd/release/4#d6dbccilps). It sure felt magical to see the book descriptions stacking up quickly in our spreadsheet, but really, we just avoided repeating the hidden labor that all those editorial assistants and marketing assistants put in to publishing those descriptions on their websites in the first place. Scraping did not solve everything, it just freed us up from this one tedious task so that we could focus on some of the more artful to-dos on our list.

## Running the script

1. Make sure you have Python 3 installed. This script was written with Python 3.7.8.
2. Clone this repository or download the files, and navigate into the directory with Terminal or Git Bash.
3. Install the libraries used by the script using [`pip`](https://pip.pypa.io/en/stable/). They are listed as imports at the top of the file, and you can also create a virtual environment with something like [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/) and run `pip install -r requirements.txt` to install them all at once.
4. Modify `metadata.xlsx` to list the elements that you will use to build the URLs. In this demo, ISBNs are all we need, since the webpages are found at URLs built with 13-digit ISBNs like https://www.ucpress.edu/book/9780520270183. The script currently expects ISBNs in any of three input columns???`ebook`, `hardcover`, and `paper`???but this can be changed by editing the opening line of the `for` loop in the `manage_scraping` function. Depending on the URL structure of the sites you want to scrape, you may need to prepare multiple elements. (You can also add other columns to `metadata.xlsx` or rearrange them without affecting the script, but you will also have to specify the desired output columns in the `new_headers` list if you want to keep them.)
5. Edit the `manage_scraping` function so that it 1) correctly forms the URLs based on your input data and 2) pinpoints the data point(s) you want from each webpage. You may want to read about [`requests`](https://docs.python-requests.org/en/master/) and you will definitely need to read up on [`BeautifulSoup`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/).
6. Edit the output parameters in the `manage_apply` function as desired. If you output to Excel, you will need to add your scraped data points to the `new_headers` list. See [`pandas DataFrame`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html) reference. If you want to output to Word, edit the rows that build the `new_document` object using syntax from [`python-docx`](https://python-docx.readthedocs.io/en/latest/). Note that output to Word is generally only useful if you are sure of the automated workflow to be used to re-ingest that content into your target system, without losing the data structure???we have used Word styles interpreted by `python-docx` for this.
7. Run the script with `python scraping_demo.py` or the appropriate command for your installation or environment.
