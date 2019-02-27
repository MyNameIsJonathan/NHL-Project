import NHL_scrape_functions as nhl

if __name__ == '__main__':
    with nhl.nonFlaskCreateEngine() as engine:
        nhl.scrapeToToday(engine)
