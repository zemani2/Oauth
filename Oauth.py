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
CALLBACK_URI = 'https://yourdomain.com/callback'  # Update this to your actual callback URL
HRV_API_URL = "https://apis.garmin.com/wellness-api/rest/hrv"

@app.route('/start_oauth')
def start_oauth():
    oauth = OAuth1Session(CONSUMER_KEY, client_secret=CONSUMER_SECRET, callback_uri=CALLBACK_URI)
    try:
        fetch_response = oauth.fetch_request_token(REQUEST_TOKEN_URL)
        session['resource_owner_key'] = fetch_response.get('oauth_token')
        session['resource_owner_secret'] = fetch_response.get('oauth_token_secret')
        authorization_url = oauth.authorization_url(AUTHORIZE_URL)
        # Update redirect URL to HTTPS
        return redirect(authorization_url.replace("http://", "https://"))
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

# Endpoint to receive push notifications containing HRV data
@app.route('/push_endpoint', methods=['POST'])
def push_endpoint():
    try:
        # Parse the JSON data from the POST request
        data = request.json
        # Check if the request contains HRV data
        if 'hrv_data' in data:
            hrv_data = data['hrv_data']
            # Process the received HRV data as needed
            return jsonify({'message': 'HRV data received successfully', 'data': hrv_data}), 200
        else:
            return jsonify({'error': 'No HRV data found in the request'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_hrv')
def get_hrv_data():
    try:
        oauth = OAuth1Session(CONSUMER_KEY,
                              client_secret=CONSUMER_SECRET,
                              resource_owner_key=session['oauth_token'],
                              resource_owner_secret=session['oauth_token_secret'])
        response = oauth.get(HRV_API_URL)
        if response.status_code == 200:
            hrv_data = response.json()
            return jsonify(hrv_data)
        else:
            return jsonify({'error': 'Failed to fetch HRV data', 'status_code': response.status_code})
    except Exception as e:
        return jsonify({'error': 'An error occurred', 'message': str(e)}), 500

@app.route('/')
def index():
    return "Hey"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=443)
