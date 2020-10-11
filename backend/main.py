from flask import Flask, render_template, request
import json
import random
import numpy as np
import scipy.sparse as sparse
import implicit
import pickle
import requests

app = Flask(__name__)

model = pickle.load(open('backend/model/finalized_model.sav', 'rb'))
user_items = sparse.load_npz('backend/model/user_items.npz')
maps_dict = pickle.load(open('backend/model/maps_dict.sav', 'rb'))
id_list = pickle.load(open('backend/model/id_list.sav', 'rb'))
inv_map = {v: k for k, v in maps_dict.items()}

@app.route('/user', methods=['POST'])
def recommendations():
    global model, user_items, inv_map, id_list
    
    user_id = request.json['input']
    recommendations = model.recommend(id_list.index(int(user_id)), user_items.T.tocsr())
    rec = random.choice(recommendations)[0]

    return {'output': 'https://osu.ppy.sh/beatmapsets/' + str(inv_map[rec])}

@app.route('/')
def index():
    return render_template('index.html')