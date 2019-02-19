import NHL_scrape_functions as nhl

if __name__ == '__main__':
    engine = nhl.nonFlaskCreateEngine()
    # backupsEngine = nhl.createEngine(database='backups')
    nhl.scrapeToToday(engine)
