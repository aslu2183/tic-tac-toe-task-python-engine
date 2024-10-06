from typing import Union
from fastapi import FastAPI
from typing import List
from pydantic import BaseModel
import engine
import os
import numpy as np

class Item(BaseModel):
    player: str
    board: List[List[int]]
    

app = FastAPI()

env = engine.Environment()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/check")
def get_engine():
    env.draw_board()
    return {"status":True}

@app.post("/move")
def move_cursor(data:Item):
    
    env.set_state(np.array(data.board))
    
    def get_next_action(env, symbol='x', sv_path=''):
        vx_val = np.load(os.path.join(sv_path, 'vx.npy'))
        vo_val = np.load(os.path.join(sv_path, 'vo.npy'))
        x_agent = engine.AgentEval(env.x, vx_val)
        o_agent = engine.AgentEval(env.o, vo_val)
        if symbol == 'x':
            return x_agent.take_action(env)
        else:
            return o_agent.take_action(env)

    best_move = get_next_action(env, data.player, sv_path='')
    if not best_move:
        result = env.reward(0)    
        return {
            "status":True,
            "message": "Game OVer",
            "isGameOver": True,
            "result": result
        }
    else:
        return {
            "status":True,
            "move": best_move,
            "isGameOver": False
        }