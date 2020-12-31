from flask import Flask, render_template, request, Blueprint, flash, g, redirect, session, url_for
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
app = Flask(__name__)
# from db import connection as conn,cursor
# import db
from psycopg2 import connect
import os
# cursor, conn = db.connection(app)


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
def create_similarity():
    data = pd.read_csv('main_data.csv')
    # creating a count matrix
    cv = CountVectorizer()
    count_matrix = cv.fit_transform(data['comb'])
    # creating a similarity score matrix
    similarity = cosine_similarity(count_matrix)
    return data,similarity

def rcmd(m):
    # global similarity, data
    m = m.lower()
    try:
        data.head()
        similarity.shape
    except:
        data, similarity = create_similarity()
    if m not in data['movie_title'].unique():
        return('Sorry! The movie you requested is not in our database. Please check the spelling or try with some other movies')
    else:
        i = data.loc[data['movie_title']==m].index[0]
        lst = list(enumerate(similarity[i]))
        lst = sorted(lst, key = lambda x:x[1] ,reverse=True)
        lst = lst[1:11] # excluding first item since it is the requested movie itself
        l = []
        for i in range(len(lst)):
            a = lst[i][0]
            l.append(data['movie_title'][a])
        return l

# converting list of string to list (eg. "["abc","def"]" to ["abc","def"])
def convert_to_list(my_list):
    my_list = my_list.split('","')
    my_list[0] = my_list[0].replace('["','')
    my_list[-1] = my_list[-1].replace('"]','')
    return my_list



# @app.route("/")
@app.route("/movierecommender",methods=["GET","POST"])
def movierecommender():
    suggestions = get_suggestions()
    return render_template('movie_recommender_home.html', suggestions=suggestions)


def get_suggestions():
    data = pd.read_csv('main_data.csv')
    return list(data['movie_title'].str.capitalize())




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
    release_date = request.form['release_date']
    runtime = request.form['runtime']
    status = request.form['status']
    rec_movies = request.form['rec_movies']
    rec_posters = request.form['rec_posters']

    # get movie suggestions for auto complete
    suggestions = get_suggestions()

    # call the convert_to_list function for every string that needs to be converted to list
    rec_movies = convert_to_list(rec_movies)
    rec_posters = convert_to_list(rec_posters)
    cast_names = convert_to_list(cast_names)
    cast_chars = convert_to_list(cast_chars)
    cast_profiles = convert_to_list(cast_profiles)
    cast_bdays = convert_to_list(cast_bdays)
    cast_bios = convert_to_list(cast_bios)
    cast_places = convert_to_list(cast_places)

    # convert string to list (eg. "[1,2,3]" to [1,2,3])
    cast_ids = cast_ids.split(',')
    cast_ids[0] = cast_ids[0].replace("[", "")
    cast_ids[-1] = cast_ids[-1].replace("]", "")

    # rendering the string to python string
    for i in range(len(cast_bios)):
        cast_bios[i] = cast_bios[i].replace(r'\n', '\n').replace(r'\"', '\"')

    # combining multiple lists as a dictionary which can be passed to the html file so that it can be processed easily and the order of information will be preserved
    movie_cards = {rec_posters[i]: rec_movies[i] for i in range(len(rec_posters))}

    casts = {cast_names[i]: [cast_ids[i], cast_chars[i], cast_profiles[i]] for i in range(len(cast_profiles))}

    cast_details = {cast_names[i]: [cast_ids[i], cast_profiles[i], cast_bdays[i], cast_places[i], cast_bios[i]] for i in
                    range(len(cast_places))}

    # web scraping to get user reviews from IMDB site
    sauce = urllib.request.urlopen('https://www.imdb.com/title/{}/reviews?ref_=tt_ov_rt'.format(imdb_id)).read()
    soup = bs.BeautifulSoup(sauce, 'html.parser')
    soup_result = soup.find_all("div", {"class": "text show-more__control"})

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

    # combining reviews and comments into a dictionary
    movie_reviews = {reviews_list[i]: reviews_status[i] for i in range(len(reviews_list))}

    # passing all the data to the html file
    return render_template('recommend.html', title=title, poster=poster, overview=overview, vote_average=vote_average,
                           vote_count=vote_count, release_date=release_date, runtime=runtime, status=status,
                           genres=genres,
                           movie_cards=movie_cards, reviews=movie_reviews, casts=casts, cast_details=cast_details)







# ==========================================================================================================


@app.route("/")
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        if 'user_id' in session:
            app.logger.debug(session['user_id'])
            return redirect(url_for('movierecommender'))
        return render_template('login.html')
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        error = None
        # password = generate_password_hash(password)
        print(password)
        email = request.form['email']
        print(email)
        cursor.execute('''SELECT * FROM ACCOUNTS WHERE EMAIL = '%s';''' % (email))
        user = cursor.fetchone()
        print(user)
        app.logger.debug(user)
        # print(user[2])
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user[2], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user[0]
            suggestions = get_suggestions()
            return render_template('movie_recommender_home.html',suggestions=suggestions,username=user[1])
        flash(error)
        return render_template('login.html', title='Login')

@app.route('/register', methods=('GET', 'POST'))
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


if __name__ == '__main__':

    app.debug = config.Config.DEBUG
    app.config['SECRET_KEY'] = config.Config.SECRET_KEY
    app.run(port=config.Config.PORT,debug=True)


# <a href="{{ url_for('login') }}"><i class="fas fa-home"></i>Login</a>-->
# <!--				<a href="{{ url_for('register') }}"><i class="fas fa-home"></i>Register</a>-->
# <!--				<a href="{{ url_for('profile') }}"><i class="fas fa-home"></i>rofile</a>-->
