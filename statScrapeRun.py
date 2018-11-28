import NHL_scrape_functions

# source /Users/jonathanolson/Projects/Environments/nhl_flask/bin/activate

if __name__ == '__main__':
    NHL_scrape_functions.scrapeToToday()


a = NHL_scrape_functions.openLatestMyDF()
b = NHL_scrape_functions.openLatestLastTime()
c = NHL_scrape_functions.openLatestGamesSince()

a[a['G'] == a['G'].max()].sort_values('PTS', ascending=False)