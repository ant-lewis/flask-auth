import os
import pathlib

import requests
from flask import Flask, session, abort, redirect, request
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googledocreader import read_structural_elements
from modules.drivehelper import download_g_drive_file

app = Flask("Google Login App")
app.secret_key = "CodeSpecialist.com"
credentials = None
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


GOOGLE_CLIENT_ID = "954876674036-mn9j311v2fsbaki2aesctgcqagvg3quk.apps.googleusercontent.com"
client_secrets_file = os.path.join(
    pathlib.Path(__file__).parent, "client_secret.json")


flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/documents.readonly", "https://www.googleapis.com/auth/drive.file", "openid"],
    # scopes=["https://www.googleapis.com/auth/documents.readonly"],
    redirect_uri="http://localhost:5000/callback",
)

# , "https://www.googleapis.com/auth/documents.readonly",


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function()

    return wrapper


@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

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

    try:
        DOCUMENT_ID = "1FGwmWOvV48oYMle3o8LiUNyFw8zYTkSAYpBmIDfMeKo"

        service = build('docs', 'v1', credentials=credentials)

        # Retrieve the documents contents from the Docs service.
        # document = service.documents().get(documentId=DOCUMENT_ID).execute()

        doc = service.documents().get(documentId=DOCUMENT_ID).execute()
        doc_content = doc.get('body').get('content')
        text = read_structural_elements(doc_content)
        print("Sample text: "+text[:50])
    except HttpError as err:
        print(err)

    download_g_drive_file(credentials)

    return redirect("/protected_area")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/")
def index():
    return "Hello World <a href='/login'><button>Login</button></a>"


@app.route("/protected_area")
@login_is_required
def protected_area():

    # try:
    #     DOCUMENT_ID = "1FGwmWOvV48oYMle3o8LiUNyFw8zYTkSAYpBmIDfMeKo"

    #     service = build('docs', 'v1', credentials=credentials)

    #     # Retrieve the documents contents from the Docs service.
    #     # document = service.documents().get(documentId=DOCUMENT_ID).execute()

    #     doc = service.documents().get(documentId=DOCUMENT_ID).execute()
    #     doc_content = doc.get('body').get('content')
    #     text = read_structural_elements(doc_content)
    #     print("Sample text: "+text[50])
    #     # print('The title of the document is: {}'.format(document.get('title')))

    #     # print('The document content is: {}'.format(document.get('body').get('content')))

    # except HttpError as err:
    #     print(err)

    return f"Hello {session['name']}! <br/> <a href='/logout'><button>Logout</button></a>"


if __name__ == "__main__":
    app.run(debug=True)
