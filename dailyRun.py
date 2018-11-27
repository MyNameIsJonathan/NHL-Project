import NHL_scrape_functions

if __name__ == '__main__':
    NHL_scrape_functions.scrapeToToday()


a = NHL_scrape_functions.openLatestMyDF()
b = NHL_scrape_functions.openLatestLastTime()
c = NHL_scrape_functions.openLatestGamesSince()