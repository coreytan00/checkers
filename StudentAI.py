from random import randint
from BoardClasses import Move
from BoardClasses import Board

from collections import defaultdict
import math
import copy
import time
#The following part should be completed by students.
#Students can modify anything except the class name and exisiting functions and varibles.

class MCTS():
    
    def __init__(self, color):
        self.win = defaultdict(int) #the rewards
        self.count = defaultdict(int) #the visit count
        self.children = {}
        self.ai = color 
        
    def search(self,node):
        #rollout
        path = self._select(node)
        self._expand(path[-1]) #take leaf of the path
        win_value = self._simulate(path[-1])
        self._backprop(path, win_value)

        #print("wins:", self.win[node])
        #print("out of:", self.count[node])
        #print("number of children:", len(self.children[node]))

    def _select(self, node):
        path = []
        while True:
            path.append(node)
            if node not in self.children or not self.children[node]:
                return path
            n = self.children[node] - self.children.keys() 
            #keys = explored nodes. take away from children = unexplored nodes
            if n:
                path.append(n.pop())
                return path
            node = self._ucb(node)

    def _expand(self, node):
        #expand on the node - add to children
        if node not in self.children:
            self.children[node] = node.find_children()

    def _simulate(self, node):
        #return reward for random simulation
        win_value = None
        while True:
            win_value = node.game_value()
            if win_value!=0:
                break
            node = node.random_child()
        #if win_value == 1, that means BLACK won. if 2, WHITE won.
        return 1 if win_value==self.ai else 0

    def _backprop(self, path, win_value):
        #print("IN BACKPROPOGATION")
        for n in reversed(path):
            self.win[n] += win_value
            self.count[n] += 1
            #win_value = 1 - win_value #invert value while traversing up
        #print("END OF BACKPROPOGATION")

    def _ucb(self, node):
        #to select next node
        x = 2*math.log(self.count[node])
        ucb_lst = [(n, (self.win[n]/self.count[n] + math.sqrt(x/self.count[n]))) for n in self.children[node]] 
        #add second key later
        best_node = max(ucb_lst, key=lambda x:x[1])[0]
        return best_node

    def best_child(self, node):
        if node not in self.children:
            return node.find_random_child()
        reward_lst = [(n, (self.win[n]/self.count[n] if self.count[n]!=0 else float("-inf"))) for n in self.children[node]]
        best_child = max(reward_lst, key=lambda x:x[1])[0]
        return best_child.prev_move

class Node():
    
    def __init__(self,board,color,move):
        self.board = board
        self.color = color #make it change according to the turn    
        self.prev_move = move

    def find_children(self):
        #find all children
        s = set()
        moves = self.board.get_all_possible_moves(self.color)
        
        for i in range(len(moves)):
            for m in moves[i]:
                b2 = self.make_sim_move(m) #create board node
                s.add(Node(b2, b2.color, m))

        return s #s is a set of all the board cofigurations as nodes (children)		

    def random_child(self):
        #find random child for simulation
        if self.is_terminal():
            return None
        #return random child
        moves = self.board.get_all_possible_moves(self.color)
        index = randint(0,len(moves)-1)
        inner_index = randint(0,len(moves[index])-1)
        move = moves[index][inner_index]
        b2 = self.make_sim_move(move)	
        return Node(b2, b2.color, move)        

    def game_value(self):
        #value of reward : self or opponent        
        winner = self.board.is_win(self.turn_rotation())
        return winner

    def is_terminal(self):
        #true if no children
        return self.board.is_win(self.turn_rotation())!=0

    def make_sim_move(self, move):
        b2 = copy.deepcopy(self.board)
        b2.make_move(move, self.color)
        b2.color = self.turn_rotation()
        return b2
    
    def turn_rotation(self):
        return 2 if self.color==1 else 1

class StudentAI():

    def __init__(self,col,row,p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col,row,p)
        self.board.initialize_game()
        self.color = ''
        self.opponent = {1:2,2:1}
        self.color = 2
        self.tree = MCTS(self.color)
        self.max_time = 480
        self.remaining_time = self.max_time

    def get_move(self,move):
        if len(move) != 0:
            self.board.make_move(move,self.opponent[self.color])
        else:
            self.color = 1 
        #color is based on who goes first.
        #if student ai goes first, color = 1
        #if I go first, color = 2 (bc ai goes second)
        
        #optimize 1 moves
        moves = self.board.get_all_possible_moves(self.color)
        if len(moves)==1 and len(moves[0])==1:
            move = moves[0][0]
        else:
            tree = MCTS(self.color)
            move = self.playout(tree,move)
        print(moves)
        self.board.moves = moves
        self.board.make_move(move,self.color)
        return move

    def playout(self,tree,move):
        node = Node(self.board, self.color,move)
        now = time.time()
        timer = 0
        i = 0
        while timer<=20:
            end = time.time()
            tree.search(node)
            print("iteration:", i)
            i += 1
            if i>1000:
                break
            timer = end-now
        return tree.best_child(node)
