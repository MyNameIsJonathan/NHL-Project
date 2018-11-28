from flask import render_template, request, Blueprint
from flaskblog.models import Post
import pandas as pd
import NHL_scrape_functions

main = Blueprint('main', __name__)


#These functions 'create' pages within your site. 
# This one creates the 'home' page, while the one 
# below creates the NHL Stats page
@main.route("/")  #Having two @app. here means that this page is rendered when either website.com/ or website.com/home are visited
@main.route("/home")
def home():
    page = request.args.get('page', default=1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', posts=posts)

@main.route("/nhl_stats")
def nhl_stats():
    myDF = NHL_scrape_functions.openLatestMyDF().sort_values('G', ascending=False)
    lastTimeDF = NHL_scrape_functions.openLatestLastTime()
    gamesSinceDF = NHL_scrape_functions.openLatestGamesSince()

    #Create a dictionary to store important pieces of info, to be displayed on NHL_stats page
    importantStats = {}

    #Get top goal scorers -- if tied, get top point scorer.
    importantStats['Top Scorer'] = myDF.sort_values(['G', 'PTS'], ascending=False).iloc[0].name
    importantStats['Second Top Scorer'] = myDF.sort_values(['G', 'PTS'], ascending=False).iloc[1].name
    importantStats['Third Top Scorer'] = myDF.sort_values(['G', 'PTS'], ascending=False).iloc[2].name
    importantStats['Fourth Top Scorer'] = myDF.sort_values(['G', 'PTS'], ascending=False).iloc[3].name
    importantStats['Fifth Top Scorer'] = myDF.sort_values(['G', 'PTS'], ascending=False).iloc[4].name

    return render_template('nhl_stats.html', title = 'NHL Stats', importantStats=importantStats)

@main.route("/announcements")
def announcements():
    return render_template('announcements.html', title = 'Announcements')