from flask import render_template, request, Blueprint
from flaskblog.models import Post
import pandas as pd


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
    a = pd.read_pickle('/Users/jonathanolson/Documents/GitHub/NHL-Project/dailyMyDF/dailyMyDF_2018-11-25.pickle')
    a = a.sort_values('G', ascending=False)
    my_results = {}
    my_results['Top Scorer'] = a.iloc[0].name
    my_results['Second Top Scorer'] = a.iloc[1].name
    my_results['Third Top Scorer'] = a.iloc[2].name
    my_results['Fourth Top Scorer'] = a.iloc[3].name
    my_results['Fifth Top Scorer'] = a.iloc[4].name
    return render_template('nhl_stats.html', title = 'NHL Stats', my_results=my_results)

@main.route("/announcements")
def announcements():
    return render_template('announcements.html', title = 'Announcements')