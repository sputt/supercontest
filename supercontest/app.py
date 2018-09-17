from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required, current_user
from supercontest.forms import EmailPasswordForm

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)

# Must be after db definition and before creation.
from supercontest import models


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = EmailPasswordForm()
    # if form.validate_on_submit():
    #    # check password here later
    #    return redirect(url_for('index'))
    return render_template('login.html', form=form)


# @APP.route('/')
# def home():
#     week, results = compare_scores_to_lines()
#     trs_list = []
#     for result in results:
#         status = result.pop(-1)
#         tds_list = ['<td>{}</td>'.format(cell) for cell in result]
#         if status == 'game is over':
#             if float(result[-1]) > float(result[-2]):
#                 tds_list[0] = tds_list[0].replace('td', 'td bgcolor=lightgreen', 1)
#             elif float(result[-2]) == float(result[-1]):
#                 tds_list[0] = tds_list[0].replace('td', 'td bgcolor=lightblue', 1)
#                 tds_list[1] = tds_list[1].replace('td', 'td bgcolor=lightblue', 1)
#             else:
#                 tds_list[1] = tds_list[1].replace('td', 'td bgcolor=lightgreen', 1)
#         tds_str = ''.join(tds_list)
#         trs_list.append('<tr>{}</tr>'.format(tds_str))
#     trs_str = ''.join(trs_list)
#
#     return render_template('home.html', week=week, trs=trs_str)


def create_db():
    db.create_all()


def run_app():
    app.run(host='0.0.0.0')


if __name__ == '__main__':
    run_app()
