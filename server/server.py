from flask import Flask, jsonify, make_response, send_from_directory
import os
os.chdir(os.getcwd() + '/server') 
from os.path import exists, join
from basketball_reference_scraper.players import get_stats, get_player_headshot
from model import DefenseClassifier
from constants import CONSTANTS
from flask_cors import CORS
from urllib.request import urlopen
from bs4 import BeautifulSoup
import json

app = Flask(__name__, static_folder='build')
CORS(app)
model = DefenseClassifier()

# Catching all routes
# This route is used to serve all the routes in the frontend application after deployment.
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    file_to_serve = path if path and exists(join(app.static_folder, path)) else 'index.html'
    return send_from_directory(app.static_folder, file_to_serve)

# Error Handler
@app.errorhandler(404)
def page_not_found(error):
    json_response = jsonify({'error': 'Page not found'})
    return make_response(json_response, CONSTANTS['HTTP_STATUS']['404_NOT_FOUND'])

@app.route('/predict/<name>')
def get_prediction(name):
    rookie_dataframe = get_stats(name, stat_type='ADVANCED', playoffs=False, career=False)
    player_classification = model.predict(rookie_dataframe.loc[0:0])
    return json.dumps({'playerPrediction':player_classification})

@app.route('/player-image/<name>')
def get_player_thumbnail(name):
    player_picture_url = get_player_headshot(name)
    return json.dumps({'imageLink':player_picture_url})

@app.route('/rookies')
def get_rookies():
    url = "https://www.basketball-reference.com/leagues/NBA_2020_rookies.html"
    html = urlopen(url)
    soup = BeautifulSoup(html, features="lxml")
    rows = soup.findAll('tr')[1:]
    
    rookies = []
    for i in range (1,len(rows)):
        row_text = rows[i].findAll('td')
        if len(row_text) != 0:
            rookies.append(row_text[0].getText())
    
    return json.dumps({'rookies':rookies})


if __name__ == '__main__':
    app.run(port=CONSTANTS['PORT'])