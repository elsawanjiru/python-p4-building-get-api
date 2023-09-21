# app.py

from flask import Flask, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy_serializer import SerializerMixin

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json_compact = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Define your models here

class Game(db.Model, SerializerMixin):
    __tablename__ = 'games'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=True)
    genre = db.Column(db.String)
    platform = db.Column(db.String)
    price = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    reviews = db.relationship('Review', backref='game')

    def to_dict(self):
        return {
            "title": self.title,
            "genre": self.genre,
            "platform": self.platform,
            "price": self.price,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "reviews": [review.to_dict() for review in self.reviews]
        }

class Review(db.Model, SerializerMixin):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer)
    comment = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    game_id = db.Column(db.Integer, db.ForeignKey('games.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    game = db.relationship('Game', back_populates='reviews')
    user = db.relationship('User', back_populates='reviews')

    def to_dict(self):
        return {
            "score": self.score,
            "comment": self.comment,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "game": self.game.to_dict(),
            "user": self.user.to_dict()
        }

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    reviews = db.relationship('Review', back_populates='user')

    def to_dict(self):
        return {
            "name": self.name,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

# Define your routes here

@app.route('/')
def index():
    return "Index for Game/Review/User API"

@app.route('/games')
def get_all_games():
    games = Game.query.all()
    game_list = [game.to_dict() for game in games]
    return jsonify(game_list)

@app.route('/games/<int:id>')
def get_game_by_id(id):
    game = Game.query.get(id)
    if game is not None:
        return jsonify(game.to_dict())
    else:
        return make_response("Game not found", 404)

if __name__ == '__main__':
    app.run(port=5555)
