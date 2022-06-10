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

    def blocker_checker(self,dir,dis):
        is_blocker = False
        if dir=='N':
            for i in range(1,dis+1):
                xx = self.player['x']
                yy = self.player['y']-i
                if (yy)<0: is_blocker=True; break
                if self.board[yy][xx]==1: is_blocker=True
        
        if dir=='S':
            for i in range(1,dis+1):
                xx = self.player['x']
                yy = self.player['y']+i
                if (yy)>=self.height: is_blocker=True; break
                if self.board[yy][xx]==1: is_blocker=True

        if dir=='W':
            for i in range(1,dis+1):
                xx = self.player['x']-i
                yy = self.player['y']
                if (xx)<0: is_blocker=True; break
                if self.board[yy][xx]==1: is_blocker=True

        if dir=='E':
            for i in range(1,dis+1):
                xx = self.player['x']+i
                yy = self.player['y']
                if (xx)>=self.width: is_blocker=True; break
                if self.board[yy][xx]==1: is_blocker=True

        return is_blocker

    def fighting_mode(self):
        # select target
        player_dir = self.player['dir']
        # forward
        if self.enemy_checker(player_dir): 
            logger.info(f"[Fighting] find enemy at: {player_dir}")
            return 'T'
        
        # left side
        if self.enemy_checker((campus.index(player_dir)+3)%4): 
            logger.info(f"[Fighting] find enemy at: {(campus.index(player_dir)+3)%4}\n Turn left!")
            return 'L'

        # right side
        if self.enemy_checker((campus.index(player_dir)+5)%4): 
            logger.info(f"[Fighting] find enemy at: {(campus.index(player_dir)+5)%4}\n Right left!")
            return 'R'

        # no enemy
        # movent = moves[random.randrange(len(moves))]
        movent = self.escape()
        logger.info(f"[Fighting] Didn't find enemy, move: {movent}")
        return movent
    
    def random_move(self):
        # no enemy
        movent = moves[random.randrange(len(moves))]
        logger.info(f"[Random Move] Random move: {movent}")
        return movent
    
    def escape(self):
        # select target
        player_dir = self.player['dir']
        # forward
        if not self.blocker_checker(player_dir,1): 
            logger.info(f"[Escape] move: {player_dir}")
            return 'F'
        
        # left side
        if not self.blocker_checker(campus[(campus.index(player_dir)+3)%4],1): 
            logger.info(f"[Escape] turn: {campus[(campus.index(player_dir)+3)%4]}\n Turn left!")
            return 'L'

        # right side
        if not self.blocker_checker(campus[(campus.index(player_dir)+5)%4],1): 
            logger.info(f"[Escape] turn: {campus[(campus.index(player_dir)+5)%4]}\n Turn right!")
            return 'R'

        return self.fighting_mode()

    def next(self):
        if self.player['hited']:
            return self.escape()
        return self.fighting_mode()

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

    arena = info["arena"]
    board = Board(arena["dims"], arena["state"])
    board.gen_board()
    
    try:
        next_move = board.next()
    except Exception as err:
        logger.error(f"Fatal error: {err}")
        return board.random_move()
    return next_move

if __name__ == "__main__":
    app.run(debug=False,host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))
