import NHL_scrape_functions as nhl

if __name__ == '__main__':
    engine = nhl.createEngine()
    backupsEngine = nhl.createEngine(database='backups')
    nhl.scrapeToToday(engine)