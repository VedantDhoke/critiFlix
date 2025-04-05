from flask import Flask, render_template, redirect, url_for, request, session, flash

app = Flask(__name__)
app.secret_key = 'testsecretkey'

# Dummy Data
users = []
movies = [
    {
        'id': 1,
        'title': 'Inception',
        'genre': 'Sci-Fi',
        'year': 2010,
        'description': 'A mind-bending thriller',
        'poster_url': 'https://image.tmdb.org/t/p/original/qmDpIHrmpJINaRKAfWQfftjCdyi.jpg'
    }
]
reviews = [
    {
        'movie_id': 1,
        'username': 'admin',
        'content': 'Amazing movie!'
    }
]

# Routes

@app.route('/')
def index():
    return render_template('index.html', movies=movies)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        for user in users:
            if user['username'] == uname and user['password'] == pwd:
                session['username'] = uname
                return redirect(url_for('index'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users.append({
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
    flash('Logged out.')
    return redirect(url_for('index'))

@app.route('/add_movie', methods=['GET', 'POST'])
def add_movie():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        new_id = len(movies) + 1
        movies.append({
            'id': new_id,
            'title': request.form['title'],
            'genre': request.form['genre'],
            'year': request.form['year'],
            'description': request.form['description'],
            'poster_url': request.form['poster_url']
        })
        return redirect(url_for('index'))
    return render_template('add_movie.html')

@app.route('/edit_movie/<int:id>', methods=['GET', 'POST'])
def edit_movie(id):
    movie = next((m for m in movies if m['id'] == id), None)
    if not movie:
        return "Movie not found", 404
    if request.method == 'POST':
        movie['title'] = request.form['title']
        movie['genre'] = request.form['genre']
        movie['year'] = request.form['year']
        movie['description'] = request.form['description']
        movie['poster_url'] = request.form['poster_url']
        return redirect(url_for('index'))
    return render_template('edit_movie.html', movie=movie)

@app.route('/delete_movie/<int:id>')
def delete_movie(id):
    global movies
    movies = [m for m in movies if m['id'] != id]
    return redirect(url_for('index'))

@app.route('/movie/<int:id>')
def movie_detail(id):
    movie = next((m for m in movies if m['id'] == id), None)
    movie_reviews = [r for r in reviews if r['movie_id'] == id]
    return render_template('movie_detail.html', movie=movie, reviews=movie_reviews)

@app.route('/add_review/<int:movie_id>', methods=['POST'])
def add_review(movie_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    content = request.form['content']
    reviews.append({
        'movie_id': movie_id,
        'username': session['username'],
        'content': content
    })
    return redirect(url_for('movie_detail', id=movie_id))

@app.route('/edit_review/<int:movie_id>/<int:review_index>', methods=['GET', 'POST'])
def edit_review(movie_id, review_index):
    review = [r for r in reviews if r['movie_id'] == movie_id][review_index]
    if request.method == 'POST':
        review['content'] = request.form['content']
        return redirect(url_for('movie_detail', id=movie_id))
    return render_template('edit_review.html', review=review, movie_id=movie_id, review_index=review_index)

@app.route('/delete_review/<int:movie_id>/<int:review_index>')
def delete_review(movie_id, review_index):
    review_list = [r for r in reviews if r['movie_id'] == movie_id]
    if review_index < len(review_list):
        reviews.remove(review_list[review_index])
    return redirect(url_for('movie_detail', id=movie_id))

if __name__ == '__main__':
    app.run(debug=True)
