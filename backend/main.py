from flask import Flask, render_template, request
import json
import random
import numpy as np
import scipy.sparse as sparse
import implicit
import pickle
import requests
from tqdm import tqdm

app = Flask(__name__)

model = pickle.load(open('backend/model/finalized_model_weighted.sav', 'rb'))
user_items = sparse.load_npz('backend/model/user_items_weighted.npz')
maps_dict = pickle.load(open('backend/model/maps_dict.sav', 'rb'))
id_list = pickle.load(open('backend/model/id_list.sav', 'rb'))
inv_map = {v: k for k, v in maps_dict.items()}

# user_items_l = user_items.tolil()
# for i in tqdm(range(user_items_l.shape[0])):
#     user_items_l[i] *= 1/1.000005**((user_items_l[i].sum() - 200)**2)
#     # user_items_l[i] *= 1/user_items_l[i].sum()**0.01
# items_id = user_items_l.tocoo()
# sparse.save_npz('backend/model/user_items_weighted.npz', items_id)
# model = implicit.lmf.LogisticMatrixFactorization(factors=32)
# model.fit(items_id)
# pickle.dump(model, open('backend/model/finalized_model_weighted.sav', 'wb'))

model_pp = pickle.load(open('backend/model/finalized_model_pp.sav', 'rb'))
id_maps_pp = sparse.load_npz('backend/model/id_maps.npz')
maps_dict_pp = pickle.load(open('backend/model/maps_dict_pp.sav', 'rb'))
id_list_pp = pickle.load(open('backend/model/id_list_10k.sav', 'rb'))
inv_map_pp = {v: k for k, v in maps_dict_pp.items()}

@app.route('/api/user', methods=['POST'])
def recommendations():
    global model, user_items, inv_map, id_list
    
    user_id = request.json['input']
    recommendations = model.recommend(id_list.index(int(user_id)), user_items.T.tocsr(), N=50)
    rec = random.choice(recommendations)[0]

    return {'output': 'https://osu.ppy.sh/beatmapsets/' + str(inv_map[rec])}

@app.route('/api/maps', methods=['POST'])
def similar_maps():
    global model, user_items, inv_map, id_list

    mapset_id = request.json['input']
    similar_maps = model.similar_items(maps_dict[int(mapset_id)], N=50)[1:]
    rec = random.choice(similar_maps)[0]

    return {'output': 'https://osu.ppy.sh/beatmapsets/' + str(inv_map[rec])}

@app.route('/api/pp', methods=['POST'])
def pp_rec():
    global model_pp, id_maps_pp, inv_map_pp, id_list_pp

    user_id = request.json['input']
    pp_recs = model_pp.recommend(id_list_pp.index(int(user_id)), id_maps_pp, N=50)
    rec = random.choice(pp_recs)[0]

    return {'output': 'https://osu.ppy.sh/b/' + str(inv_map_pp[rec])}

@app.route('/api/pp_players', methods=['POST'])
def similar_players():
    global model_pp, id_maps_pp, inv_map_pp, id_list_pp

    user_id = request.json['input']
    similar_players = model_pp.similar_users(id_list_pp.index(int(user_id)), N=10)[1:]
    rec = random.choice(similar_players)[0]

    return {'output': 'https://osu.ppy.sh/users/' + str(id_list_pp[rec])}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/maps')
def maps():
    return render_template('maps.html')

@app.route('/pp')
def pp():
    return render_template('pp.html')

@app.route('/pp_players')
def pp_players():
    return render_template('pp_players.html')