import game_by_game_scrape
import schedule
import time

def job():
    print('It works')

# schedule.every().day.at("18:35").do(job)

schedule.every().day.at("18:37").do(game_by_game_scrape.scrapeYesterday)

while True:
    schedule.run_pending()
    time.sleep(60)