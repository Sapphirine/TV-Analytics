import os,inspect,sys
import helperFunctions
#from app import app
from flask import Flask,render_template, flash, redirect, request, url_for,g, session
#from forms import SearchForm
from flask.ext.openid import OpenID
import urllib
import requests
from openid.extensions import pape

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
try:
    import addshowclient
except Exception, e:
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    crawlerdir = os.path.join(parentdir,"queue_test")
    sys.path.insert(0,crawlerdir)
    import addshowclient
import json

app = Flask(__name__)
app.config.update(
    DATABASE_URI = 'sqlite:///flask-openid.db',
    SECRET_KEY = 'development key'
)


# setup flask-openid
oid = OpenID(app, safe_roots=[], extension_responses=[pape.Response])

# setup sqlalchemy
engine = create_engine(app.config['DATABASE_URI'])
db_session = scoped_session(sessionmaker(autocommit=True,
                                         autoflush=True,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()
def init_db():
    Base.metadata.create_all(bind=engine)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(60))
    email = Column(String(200))
    openid = Column(String(200))
    series = Column(String(1000))

    def __init__(self, name, email, openid, series):
        self.name = name
        self.email = email
        self.openid = openid
        self.series = series

@app.before_request
def before_request():
    g.user = None
    if 'openid' in session:
        g.user = User.query.filter_by(openid=session['openid']).first()


@app.after_request
def after_request(response):
    db_session.remove()
    return response



@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    """Does the login via OpenID.  Has to call into `oid.try_login`
    to start the OpenID machinery.
    """
    # if we are already logged in, go back to were we came from
    if g.user is not None:
        return redirect(oid.get_next_url())
    if request.method == 'POST':
        openid = "https://www.google.com/accounts/o8/id"
        pape_req = pape.Request([])
        return oid.try_login(openid, ask_for=['email', 'nickname'],
                                     ask_for_optional=['fullname'],
                                     extensions=[pape_req])
    return render_template('login.html', next=oid.get_next_url(),
                           error=oid.fetch_error())


@oid.after_login
def create_or_login(resp):
    """This is called when login with OpenID succeeded and it's not
    necessary to figure out if this is the users's first login or not.
    This function has to redirect otherwise the user will be presented
    with a terrible URL which we certainly don't want.
    """
    session['openid'] = resp.identity_url
    if 'pape' in resp.extensions:
        pape_resp = resp.extensions['pape']
        session['auth_time'] = pape_resp.auth_time
    user = User.query.filter_by(openid=resp.identity_url).first()
    if user is not None:
        flash(u'Successfully signed in')
        g.user = user
        return redirect(oid.get_next_url())
    return redirect(url_for('create_profile', next=oid.get_next_url(),
                            name=resp.fullname or resp.nickname,
                            email=resp.email))


@app.route('/create-profile', methods=['GET', 'POST'])
def create_profile():
    """If this is the user's first login, the create_or_login function
    will redirect here so that the user can set up his profile.
    """
    if g.user is not None or 'openid' not in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        if not name:
            flash(u'Error: you have to provide a name')
        elif '@' not in email:
            flash(u'Error: you have to enter a valid email address')
        else:
            flash(u'Profile successfully created')
            db_session.begin()
            db_session.add(User(name, email, session['openid'], ""))
            db_session.commit()
            return redirect(oid.get_next_url())
    return render_template('create_profile.html', next_url=oid.get_next_url())


@app.route('/profile', methods=['GET', 'POST'])
def edit_profile():
    """Updates a profile"""
    if g.user is None:
        abort(401)
    form = dict(name=g.user.name, email=g.user.email)
    if request.method == 'POST':
        if 'delete' in request.form:
            db_session.begin()
            db_session.delete(g.user)
            db_session.commit()
            session['openid'] = None
            flash(u'Profile deleted')
            return redirect(url_for('index'))
        if 'remove' in request.form:
            li = g.user.series.split(',')
            li.remove(request.form['remove'])
            db_session.begin()
            g.user.series = ','.join(li)
            db_session.commit()
            return redirect(url_for('edit_profile'))
        error_msg = ""
        if request.form['series']:    
            form['series'] = request.form['series']
            flash(u'Profile successfully created')
            s = {'t':form['series'],'plot':'short','r':'json'}
            imdb_api_url = 'http://www.omdbapi.com/?'+ urllib.urlencode(s)
            res = requests.get(imdb_api_url)
            res =  res.json()
            if res["Response"] == "True":
                if res['Title'] in g.user.series.split(','):
                    error_msg = "Series is already in the list"
                    return render_template('edit_profile.html',form=form, error_msg=error_msg )
                db_session.begin()
                g.user.series += ("," if g.user.series else "") + res["Title"]
                db_session.commit()
                addshowclient.addshowclient(str(res["Title"]))
            else:
                error_msg = "Please enter a valid series"
        else:
            error_msg = "Cannot leave series blank"
        return render_template('edit_profile.html',form=form, error_msg=error_msg )
    return render_template('edit_profile.html', form=form)



@app.route('/logout')
def logout():
    session.pop('openid', None)
    flash(u'You have been signed out')
    return redirect('/')



@app.route('/',methods = ['GET', 'POST'])
@app.route('/index',methods = ['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/searchSeries', methods = ['GET', 'POST'])
def searchSeries():
    flash('Series requested is : '+request.args['seriesName'])
    message = request.args['seriesName']
    message =  helperFunctions.processSeriesString(message)

    message[1] = message[1]+".json"
    ESQuery = dict()
    q = dict() 
    q['match'] = {'showName': request.args['seriesName']}
    ESQuery['size'] = 1000 
    ESQuery['query'] = q
    
    showExists =  addshowclient.addshowclient(request.args['seriesName'])
    res = requests.post('http://localhost:9200/tvshows/_search',json.dumps(ESQuery))
    res = res.json()
    
    #if show file exists, then use that file otherwise use scrapy to generate the json and then use that
    if showExists:
        return render_template("generateChart.html",showName = message[1],esdata = str(json.dumps(res)))
    else:
        #add to queue
        #Respond with try again later
        return render_template("generateChart.html",showName = message[1],esdata = str(json.dumps(res)))


@app.route('/recommendation', methods=['GET', 'POST'])
def recommendation():
    """give recommendations"""
    
    ESQuery =  json.loads('{  "query":  {  "range" : {  "airDate" : {  "gte": "now" }   }  }, "size":1000  }')
    res = requests.post('http://localhost:9200/tvshows/_search',json.dumps(ESQuery))
    res = res.json()
    return render_template('recommendation.html', shows=str(json.dumps(res)))



if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0',debug=True)