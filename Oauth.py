from flask import Flask, redirect, request, session, jsonify
from requests_oauthlib import OAuth1Session
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Replace these values with your own consumer key and secret
CONSUMER_KEY = "1f52cb42-4642-4ed0-8915-04347a549d68"
CONSUMER_SECRET = "zx7Wlh4sxWCWnR0o5mUf67SAIZ4KidWSV4M"
REQUEST_TOKEN_URL = "https://connectapi.garmin.com/oauth-service/oauth/request_token"
AUTHORIZE_URL = "https://connect.garmin.com/oauthConfirm"
ACCESS_TOKEN_URL = "https://connectapi.garmin.com/oauth-service/oauth/access_token"
CALLBACK_URI = 'http://127.0.0.1:5000/callback'  # Update this to your actual callback URL


@app.route('/start_oauth')
def start_oauth():
    oauth = OAuth1Session(CONSUMER_KEY, client_secret=CONSUMER_SECRET, callback_uri=CALLBACK_URI)
    try:
        fetch_response = oauth.fetch_request_token(REQUEST_TOKEN_URL)
        session['resource_owner_key'] = fetch_response.get('oauth_token')
        session['resource_owner_secret'] = fetch_response.get('oauth_token_secret')
        authorization_url = oauth.authorization_url(AUTHORIZE_URL)
        return redirect(authorization_url)
    except ValueError as e:
        return jsonify({'error': 'Error fetching request token', 'message': str(e)}), 400


@app.route('/callback')
def callback():
    resource_owner_key = session.get('resource_owner_key')
    resource_owner_secret = session.get('resource_owner_secret')

    if not resource_owner_key or not resource_owner_secret:
        return jsonify({'error': 'Missing resource owner key or secret'}), 400

    oauth = OAuth1Session(CONSUMER_KEY,
                          client_secret=CONSUMER_SECRET,
                          resource_owner_key=resource_owner_key,
                          resource_owner_secret=resource_owner_secret,
                          verifier=request.args.get('oauth_verifier'))
    try:
        oauth_tokens = oauth.fetch_access_token(ACCESS_TOKEN_URL)
        session['oauth_token'] = oauth_tokens.get('oauth_token')
        session['oauth_token_secret'] = oauth_tokens.get('oauth_token_secret')
        return jsonify({
            'oauth_token': oauth_tokens.get('oauth_token'),
            'oauth_token_secret': oauth_tokens.get('oauth_token_secret')
        })
    except ValueError as e:
        return jsonify({'error': 'Error fetching access token', 'message': str(e)}), 400


@app.route('/')
def index():
    return "Hi Flask"
    # return redirect('/start_oauth')


if __name__ == '__main__':
    app.run(debug=True)
