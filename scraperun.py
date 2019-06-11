import NHL_scrape_functions as nhl

if __name__ == '__main__':
    engine = nhl.non_flask_create_engine()
    nhl.scrapeToToday(engine)
