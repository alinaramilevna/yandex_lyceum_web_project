import datetime
import json

from flask import Flask, render_template, redirect, make_response, request, session, abort
from data import db_session
from flask import jsonify, make_response

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


def main():
    db_session.global_init("db/database.db")
    app.run(debug=True)


@app.route('/')
@app.route('/index')
def main_page():
    return render_template('index.html')


if __name__ == '__main__':
    main()
