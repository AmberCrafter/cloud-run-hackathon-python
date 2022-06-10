
# Copyright 2020 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import logging
import random
from flask import Flask, request
import numpy

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
logger = logging.getLogger(__name__)

app = Flask(__name__)
campus = ['N', 'E', 'S', 'W']
# moves = ['F', 'T', 'L', 'R']
moves = ['F', 'L', 'R']

PRE_MOVE = None
MY_URL = 'https://cloud-run-hackathon-python-gmlbzotaqa-uc.a.run.app'

class Board:
    def __init__(self, dims, status):
        self.width = int(dims[0])
        self.height = int(dims[1])
        self.player = dict(
            x = int(status[MY_URL]['x']),
            y = int(status[MY_URL]['y']),
            dir = status[MY_URL]['direction'],
            hited = status[MY_URL]['wasHit'],
        )
        self.status = status
        self.board = None

    def gen_board(self):
        self.board = numpy.zeros((self.height, self.width))
        for purl in self.status:
            p = self.status[purl]
            x = int(p['x'])
            y = int(p['y'])
            self.board[y][x] = 1
    
    def enemy_checker(self,dir):
        is_enemy = False
        if dir=='N':
            for i in range(1,4):
                xx = self.player['x']
                yy = self.player['y']-i
                if (yy)<0: break
                if self.board[yy][xx]==1: is_enemy=True
        
        if dir=='S':
            for i in range(1,4):
                xx = self.player['x']
                yy = self.player['y']+i
                if (yy)>=self.height: break
                if self.board[yy][xx]==1: is_enemy=True

        if dir=='W':
            for i in range(1,4):
                xx = self.player['x']-i
                yy = self.player['y']
                if (xx)<0: break
                if self.board[yy][xx]==1: is_enemy=True

        if dir=='E':
            for i in range(1,4):
                xx = self.player['x']+i
                yy = self.player['y']
                if (xx)>=self.width: break
                if self.board[yy][xx]==1: is_enemy=True

        return is_enemy

    def fighting_mode(self):
#         # select target
#         player_dir = self.player['dir']
#         # forward
#         if self.enemy_checker(player_dir): 
#             logger.info(f"find enemy at: {player_dir}")
#             return 'T'
        
#         # left side
#         if self.enemy_checker((campus.index(player_dir)+3)%4): 
#             logger.info(f"find enemy at: {(campus.index(player_dir)+3)%4}\n Turn left!")
#             return 'L'

#         # right side
#         if self.enemy_checker((campus.index(player_dir)+5)%4): 
#             logger.info(f"find enemy at: {(campus.index(player_dir)+5)%4}\n Right left!")
#             return 'R'

        # no enemy
        movent = moves[random.randrange(len(moves))]
        logger.info(f"Didn't find enemy, random move: {movent}")
        return movent

def is_valid_request(ctx):
    if not MY_URL==ctx["_links"]["self"]["href"]: return False
    return True

@app.route("/", methods=['GET'])
def index():
    return "Let the battle begin!"

@app.route("/", methods=['POST'])
def move():
    request.get_data()
    logger.info(request.json)

    info = request.json

    ## vailfied request
    if not is_valid_request(info): return 'bed request!', 400

    # if isinstance(MY_URL, type(None)):
    #     MY_URL = info["_links"]["self"]["href"]

    arena = info["arena"]
    board = Board(arena["dims"], arena["state"])
    board.gen_board()

    return board.fighting_mode()

if __name__ == "__main__":
  app.run(debug=False,host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))
  
