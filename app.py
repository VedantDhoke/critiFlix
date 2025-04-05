from flask import Flask, render_template, redirect, url_for, request, session, flash
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = 'testsecretkey'

client = MongoClient("mongodb+srv://shiven:shiven123@shivencluster.blo4awt.mongodb.net/?retryWrites=true&w=majority&appName=ShivenCluster")
db = client["CritiFlix"]
users_col = db["users"]
movies_col = db["movies"]
reviews_col = db["reviews"]

@app.route('/')
def index():
    movies = list(movies_col.find())
    return render_template('index.html', movies=movies)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        user = users_col.find_one({'username': uname, 'password': pwd})
        if user:
            session['username'] = uname
            # flash('Logged in successfully!')
            return redirect(url_for('index'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users_col.insert_one({
            'username': request.form['username'],
            'password': request.form['password'],
            'email': request.form['email']
        })
        flash('Registered successfully!')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    # flash('Logged out.')
    return redirect(url_for('index'))

@app.route('/add_movie', methods=['GET', 'POST'])
def add_movie():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        movies_col.insert_one({
            'title': request.form['title'],
            'genre': request.form['genre'],
            'year': request.form['year'],
            'description': request.form['description'],
            'poster_url': request.form['poster_url']
        })
        return redirect(url_for('index'))
    return render_template('add_movie.html')

@app.route('/edit_movie/<id>', methods=['GET', 'POST'])
def edit_movie(id):
    movie = movies_col.find_one({'_id': ObjectId(id)})
    if not movie:
        return "Movie not found", 404
    if request.method == 'POST':
        movies_col.update_one({'_id': ObjectId(id)}, {
            '$set': {
                'title': request.form['title'],
                'genre': request.form['genre'],
                'year': request.form['year'],
                'description': request.form['description'],
                'poster_url': request.form['poster_url']
            }
        })
        return redirect(url_for('index'))
    return render_template('edit_movie.html', movie=movie)

@app.route('/delete_movie/<id>')
def delete_movie(id):
    movies_col.delete_one({'_id': ObjectId(id)})
    return redirect(url_for('index'))

@app.route('/movie/<id>')
def movie_detail(id):
    movie = movies_col.find_one({'_id': ObjectId(id)})
    movie_reviews = list(reviews_col.find({'movie_id': ObjectId(id)}))
    return render_template('movie_detail.html', movie=movie, reviews=movie_reviews)

@app.route('/add_review/<id>', methods=['POST'])
def add_review(id):
    if 'username' not in session:
        return redirect(url_for('login'))
    content = request.form['content']
    reviews_col.insert_one({
        'movie_id': ObjectId(id),
        'username': session['username'],
        'content': content
    })
    return redirect(url_for('movie_detail', id=id))

@app.route('/edit_review/<review_id>', methods=['GET', 'POST'])
def edit_review(review_id):
    review = reviews_col.find_one({'_id': ObjectId(review_id)})
    if not review:
        return "Review not found", 404
    if request.method == 'POST':
        reviews_col.update_one({'_id': ObjectId(review_id)}, {'$set': {'content': request.form['content']}})
        return redirect(url_for('movie_detail', id=review['movie_id']))
    return render_template('edit_review.html', review=review)

@app.route('/delete_review/<review_id>')
def delete_review(review_id):
    review = reviews_col.find_one({'_id': ObjectId(review_id)})
    if review:
        reviews_col.delete_one({'_id': ObjectId(review_id)})
    return redirect(url_for('movie_detail', id=review['movie_id']))
@app.route('/search')
def search_movies():
    query = request.args.get('query', '').strip()
    if query:
        # Case-insensitive search on title
        movies = list(movies_col.find({'title': {'$regex': query, '$options': 'i'}}))
    else:
        movies = list(movies_col.find())
    return render_template('index.html', movies=movies)


if __name__ == '__main__':
    app.run(debug=True)
