from flask import Flask, render_template, request, redirect, session, abort

import os
import pathlib
import requests

from datetime import date

from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests

import jounal


app = Flask(__name__)
app.secret_key = " "
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = " "
client_secrets_file = os.path.join(
    pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
)


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:  # authorization required
            return abort(401)
        else:
            return function()
    return wrapper


@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(
        session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    return redirect("/home")


@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/")
def index():
    return render_template('login.html')


@app.route('/link_redirect/<path:url>')
def link_redirect(url):
    print(url, "\n=====================\n")
    return redirect(url, code=302)


@app.route("/home")
def home():
    print(session['google_id'])
    mood, stress = jounal.mood_stress_table(session['google_id'])
    user = session["name"].title()
    return render_template('home.html', data=[user, mood, stress])


@app.route("/journal")
def journal():
    if jounal.check_entry(date.today(), session['google_id']):
        return render_template('cloud.html')
    return render_template('journal.html')


@app.route("/logs")
def logs():
    records = jounal.get_records_by_id(session['google_id'])
    return render_template('logs.html', records=records)


@app.route("/activities")
def activities():
    return render_template('activities.html')


@app.route("/entry", methods=['GET', 'POST'])
def entry():
    today_date = date.today()

    mood_rating = request.form.get('emotion')
    stress_rating = request.form.get('stress')

    smile = request.form.get('smile')
    challenges = request.form.get('challenges')
    bad_lost = request.form.get('bad-lost')
    grateful = request.form.get('grateful')
    better = request.form.get('better')
    record = request.form.get('record')

    journal_entry = f"Write about something that made you smile today?\n{smile}\nWhat challenges/goals did you try to/completely overcome/finish today?\n{challenges}\nA thought/action that made you feel bad/lost today\n{bad_lost}\nWhat are you grateful for today?\n{grateful}\nHow do you plan on making tommorow better?\n{better}\nWrite about something to either voice your thought or simply record.\n{record}\n"
    jounal.insert_record(session['google_id'], session['name'], today_date, journal_entry, mood_rating, stress_rating)
    jounal.word_cloud(journal_entry)
    return render_template('cloud.html')


if __name__ == "__main__":
    app.run(debug=True)
