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

# model = pickle.load(open('backend/model/finalized_model.sav', 'rb'))
user_items = sparse.load_npz('backend/model/user_items_weighted.npz')
maps_dict = pickle.load(open('backend/model/maps_dict.sav', 'rb'))
id_list = pickle.load(open('backend/model/id_list.sav', 'rb'))
inv_map = {v: k for k, v in maps_dict.items()}

# user_items_l = user_items.tolil()
# for i in tqdm(range(user_items_l.shape[0])):
#     user_items_l[i] *= ((1/user_items_l[i].sum())**0.05)
# items_id = user_items_l.tocoo()
# sparse.save_npz('backend/model/user_items_weighted.npz', items_id)
model = implicit.lmf.LogisticMatrixFactorization(factors=32, regularization=5)
model.fit(user_items)

@app.route('/user', methods=['POST'])
def recommendations():
    global model, user_items, inv_map, id_list
    
    user_id = request.json['input']
    recommendations = model.recommend(id_list.index(int(user_id)), user_items.T.tocsr(), N=25)
    rec = random.choice(recommendations)[0]

    return {'output': 'https://osu.ppy.sh/beatmapsets/' + str(inv_map[rec])}

@app.route('/beatmap', methods=['POST'])
def similar_maps():
    global model, user_items, inv_map, id_list

    mapset_id = request.json['input']
    similar_maps = model.similar_items(maps_dict[int(mapset_id)], N=25)[1:]
    rec = random.choice(similar_maps)[0]

    return {'output': 'https://osu.ppy.sh/beatmapsets/' + str(inv_map[rec])}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/maps')
def maps():
    return render_template('maps.html')