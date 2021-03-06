from flask import Flask, render_template, request, Blueprint, flash, g, redirect, session, url_for
from pipenv.vendor.urllib3.exceptions import HTTPError
from werkzeug.security import generate_password_hash, check_password_hash
import db
from flask import Flask, render_template, request, redirect, url_for, session, flash,g,session,Blueprint
from datetime import datetime
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd
import bs4 as bs
import urllib.request
import pickle
from datetime import date

app = Flask(__name__)
app.secret_key = "iamkey345"
app.config['SECRET_KEY'] = "1a2b3c4d"

# from db import connection as conn,cursor
# import db
from psycopg2 import connect
import os
# cursor, conn = db.connection(app)

dictt = {}

conn = connect(user="ytxlxwlysehdbe",
                          password="f48ba2aec3b7f09a41bc2d0b4d48644c202b01d7fd9499a54833c0be9282bf8d",
                          host="ec2-75-101-232-85.compute-1.amazonaws.com",
                          port="5432",
                          database="ddlj5rrgii4pdl"
                          )
cursor = conn.cursor()


filename = 'nlp_model.pkl'
clf = pickle.load(open(filename, 'rb'))
vectorizer = pickle.load(open('tranform.pkl', 'rb'))

def convert_to_list(my_list):
    my_list = my_list.split('","')
    my_list[0] = my_list[0].replace('["','')
    my_list[-1] = my_list[-1].replace('"]','')
    return my_list

# convert list of numbers to list (eg. "[1,2,3]" to [1,2,3])
def convert_to_list_num(my_list):
    my_list = my_list.split(',')
    my_list[0] = my_list[0].replace("[","")
    my_list[-1] = my_list[-1].replace("]","")
    return my_list

def get_suggestions():
    data = pd.read_csv('main_data.csv')
    return list(data['movie_title'].str.capitalize())



def create_similarity():
    data = pd.read_csv('main_data.csv')
    # creating a count matrix
    cv = CountVectorizer()
    count_matrix = cv.fit_transform(data['comb'])
    # creating a similarity score matrix
    similarity = cosine_similarity(count_matrix)
    return data,similarity




# def rcmd(m):
#     m = m.lower()
#     try:
#         data.head()
#         similarity.shape
#     except:
#         data, similarity = create_similarity()
#     if m not in data['movie_title'].unique():
#         return('Sorry! The movie you requested is not in our database. Please check the spelling or try with some other movies')
#     else:
#         i = data.loc[data['movie_title']==m].index[0]
#         lst = list(enumerate(similarity[i]))
#         lst = sorted(lst, key = lambda x:x[1] ,reverse=True)
#         lst = lst[1:11] # excluding first item since it is the requested movie itself
#         l = []
#         for i in range(len(lst)):
#             a = lst[i][0]
#             l.append(data['movie_title'][a])
#         return l

def rcmd(m):
    # global similarity, data
    m = m.lower()
    try:
        data.head()
        similarity.shape
    except:
        data, similarity = create_similarity()
    if m not in data['movie_title']:
        return('Sorry! The movie you requested is not in our database. Please check the spelling or try with some other movies')
        # return 1
    elif m  in data['movie_title']:
        i = data.loc[data['movie_title']==m].index[0]
        lst = list(enumerate(similarity[i]))
        lst = sorted(lst, key = lambda x:x[1] ,reverse=True)
        lst = lst[1:11] # excluding first item since it is the requested movie itself
        l = []
        for i in range(len(lst)):
            a = lst[i][0]
            l.append(data['movie_title'][a])
    else:
        return ('Sorry! The movie you requested is not in our database. Please check the spelling or try with some other movies')
    return l



@app.route("/similarity", methods=["POST"])
def similarity():
    movie = request.form['name']
    rc = rcmd(movie)
    if type(rc) == type('string'):
        return rc
    else:
        m_str = "---".join(rc)
        return m_str


@app.route("/recommend", methods=["POST"])
def recommend():
    # getting data from AJAX request
    title = request.form['title']
    cast_ids = request.form['cast_ids']
    cast_names = request.form['cast_names']
    cast_chars = request.form['cast_chars']
    cast_bdays = request.form['cast_bdays']
    cast_bios = request.form['cast_bios']
    cast_places = request.form['cast_places']
    cast_profiles = request.form['cast_profiles']
    imdb_id = request.form['imdb_id']
    poster = request.form['poster']
    genres = request.form['genres']
    overview = request.form['overview']
    vote_average = request.form['rating']
    vote_count = request.form['vote_count']
    rel_date = request.form['rel_date']
    release_date = request.form['release_date']
    runtime = request.form['runtime']
    status = request.form['status']
    rec_movies = request.form['rec_movies']
    rec_posters = request.form['rec_posters']
    rec_movies_org = request.form['rec_movies_org']
    rec_year = request.form['rec_year']
    rec_vote = request.form['rec_vote']

    # get movie suggestions for auto complete
    suggestions = get_suggestions()

    # call the convert_to_list function for every string that needs to be converted to list
    rec_movies_org = convert_to_list(rec_movies_org)
    rec_movies = convert_to_list(rec_movies)
    rec_posters = convert_to_list(rec_posters)
    cast_names = convert_to_list(cast_names)
    cast_chars = convert_to_list(cast_chars)
    cast_profiles = convert_to_list(cast_profiles)
    cast_bdays = convert_to_list(cast_bdays)
    cast_bios = convert_to_list(cast_bios)
    cast_places = convert_to_list(cast_places)

    # convert string to list (eg. "[1,2,3]" to [1,2,3])
    cast_ids = convert_to_list_num(cast_ids)
    rec_vote = convert_to_list_num(rec_vote)
    rec_year = convert_to_list_num(rec_year)

    # rendering the string to python string
    for i in range(len(cast_bios)):
        cast_bios[i] = cast_bios[i].replace(r'\n', '\n').replace(r'\"', '\"')

    for i in range(len(cast_chars)):
        cast_chars[i] = cast_chars[i].replace(r'\n', '\n').replace(r'\"', '\"')

        # combining multiple lists as a dictionary which can be passed to the html file so that it can be processed easily and the order of information will be preserved
    movie_cards = {rec_posters[i]: [rec_movies[i], rec_movies_org[i], rec_vote[i], rec_year[i]] for i in
                   range(len(rec_posters))}

    casts = {cast_names[i]: [cast_ids[i], cast_chars[i], cast_profiles[i]] for i in range(len(cast_profiles))}

    cast_details = {cast_names[i]: [cast_ids[i], cast_profiles[i], cast_bdays[i], cast_places[i], cast_bios[i]] for i in
                    range(len(cast_places))}

    # web scraping to get user reviews from IMDB site
    try:
        sauce = urllib.request.urlopen('https://www.imdb.com/title/{}/reviews?ref_=tt_ov_rt'.format(imdb_id)).read()
        soup = bs.BeautifulSoup(sauce, 'html.parser')
        soup_result = soup.find_all("div", {"class": "text show-more__control"})
    except  HTTPError as e:
        return 'Sorry! The movie you requested is not in our database. Please check the spelling or try with some other movies'

    reviews_list = []  # list of reviews
    reviews_status = []  # list of comments (good or bad)
    for reviews in soup_result:
        if reviews.string:
            reviews_list.append(reviews.string)
            # passing the review to our model
            movie_review_list = np.array([reviews.string])
            movie_vector = vectorizer.transform(movie_review_list)
            pred = clf.predict(movie_vector)
            reviews_status.append('Good' if pred else 'Bad')

    # getting current date
    movie_rel_date = ""
    curr_date = ""
    if (rel_date):
        today = str(date.today())
        curr_date = datetime.strptime(today, '%Y-%m-%d')
        movie_rel_date = datetime.strptime(rel_date, '%Y-%m-%d')

    # combining reviews and comments into a dictionary
    movie_reviews = {reviews_list[i]: reviews_status[i] for i in range(len(reviews_list))}

    # passing all the data to the html file
    return render_template('recommend.html', title=title, poster=poster, overview=overview, vote_average=vote_average,
                           vote_count=vote_count, release_date=release_date, movie_rel_date=movie_rel_date,
                           curr_date=curr_date, runtime=runtime, status=status, genres=genres, movie_cards=movie_cards,
                           reviews=movie_reviews, casts=casts, cast_details=cast_details)


# ==========================================================================================================


@app.route("/",methods=['POST','GET'])
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        if 'user_id' in session:
            app.logger.debug(session['user_id'])
            return redirect(url_for('movierecommender'))
        return render_template('login.html')
    if request.method == 'POST':
        useremailname = request.form['emailorusername']
        password = request.form['password']
        error = None
        # password = generate_password_hash(password)
        print(password)
        # email = request.form['email']
        # print(email)
        cursor.execute('''SELECT * FROM ACCOUNTS WHERE EMAIL = '%s' or USERNAME = '%s';''' % (useremailname,useremailname))
        user = cursor.fetchone()

        print(user)
        app.logger.debug(user)
        # print(user[2])
        # dictt['username'] = str(user[1])
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user[2], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user[0]
            session['username'] = user[1]
            dictt['username'] = user[1]
            suggestions = get_suggestions()
            # usernam = user[1]
            # return render_template('movie_recommender_home.html',suggestions=suggestions,username=dictt['username'])
            return redirect(url_for('movierecommender'))
        flash(error)
        return render_template('login.html', title='Login')

@app.route("/forgot-password",methods=['POST','GET'])
def forgot_password():
    if request.method == 'POST':
        username = request.form['name']
        email = request.form['email']
        password = request.form['password']
        cursor.execute('''SELECT * FROM ACCOUNTS WHERE EMAIL='%s' and USERNAME='%s';''' % (email,username))
        isaccountexists = cursor.fetchone()
        if  isaccountexists :
            password = generate_password_hash(password)
            cursor.execute('''UPDATE ACCOUNTS SET PASSWORD = '%s' where USERNAME = '%s';''' % (password, username))
            conn.commit()
            flash("Password has been set successfully! Login Now!")
            # flash('Registration successfull!, login now!')
            return redirect(url_for('login'))
        else:
            flash("Account does not exists")
    return render_template('forgot_password.html')



# @app.route("/backtohome")
# def backtohome():
#     suggestions = get_suggestions()
#     return render_template('movie_recommender_home.html', suggestions=suggestions, username=session['username'])


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        if 'user_id' in session:
            app.logger.debug(session['user_id'])
            return redirect(url_for('home'))
        return render_template('register.html', title='Register')
    if request.method == 'POST':
        username = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm']
        error = None
        if password != confirm:
            error = 'password and confirm password does not match'
        else:
            cursor.execute('''SELECT * FROM ACCOUNTS WHERE EMAIL='%s';'''% (email))
            user = cursor.fetchone()
            app.logger.debug(user)
            if user:
                error = 'Sorry, email already exist!'

        if error is None:
            password = generate_password_hash(password)
            now = datetime.now()
            date_time = now.strftime("%m-%d-%Y, %H:%M:%S")

            cursor.execute('''INSERT INTO ACCOUNTS(USERNAME,PASSWORD,EMAIL,CREATED_ON) VALUES ( '%s', '%s', '%s','%s') RETURNING USER_ID;''' % (username, password, email, str(now)))
            # user = cursor.fetchone()
            conn.commit()
            print(cursor.lastrowid)
            if not cursor.lastrowid:
                flash('Registration successfull!, login now!')
                return redirect(url_for('login'))
            else:
                flash('Something went wrong, try again!')
                return render_template('register.html', title='Register')
        flash(error)
        return render_template('register.html', title='Register')

# @app.route('/')
# def index():
#     # if request.method == 'GET':
#     #     if 'user_id' in session:
#     #         return redirect(url_for('home'))
#     return redirect(url_for('login'))


# @app.route('/home')
# def home():
#     if request.method == 'GET':
#         if 'user_id' not in session:
#             return redirect(url_for('login'))
#     cursor.execute('SELECT * FROM ACCOUNTS WHERE user_id=%d' % (session['user_id']))
#     user = cursor.fetchone()
#     name = user[1]
#     return render_template('home.html', title=name, name=name)


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have successfully logged out.')
    return redirect('/login')

@app.route("/movierecommender")
def movierecommender():
    suggestions = get_suggestions()
    # return render_template('movie_recommender_home.html', suggestions=suggestions,username=us)

    return render_template('movie_recommender_home.html', suggestions=suggestions)


if __name__ == '__main__':

    app.debug = True
    app.config['SECRET_KEY'] = "1a2b3c4d"
    app.run(debug=True)


# <a href="{{ url_for('login') }}"><i class="fas fa-home"></i>Login</a>-->
# <!--				<a href="{{ url_for('register') }}"><i class="fas fa-home"></i>Register</a>-->
# <!--				<a href="{{ url_for('profile') }}"><i class="fas fa-home"></i>rofile</a>-->
