from random import randint
from BoardClasses import Move
from BoardClasses import Board

from collections import defaultdict
import math
import copy
import time
#The following part should be completed by students.
#Students can modify anything except the class name and exisiting functions and varibles.

class Node():
    
    def __init__(self,parent):
    	self.parent = parent
    	self.children = {} #{ action:Node, action:Node}
    	self.N = 0
    	self.Q = 0 #rewards
        self.u = 0

    def find_children(self):
        #find all children
        s = set()
        moves = self.board.get_all_possible_moves(self.color)
        
        for i in range(len(moves)):
            for m in moves[i]:
                b2 = self.make_sim_move(m) #create board node
                s.add(Node(b2, b2.color, m))

        return s #s is a set of all the board cofigurations as nodes (children)     

    def is_terminal(self):
        #true if no children
        return len(self.children)==0

    def make_sim_move(self, move):
        b2 = copy.deepcopy(self.board)
        b2.make_move(move, self.color)
        b2.color = self.turn_rotation()
        return b2
    
    def turn_rotation(self):
        return 2 if self.color==1 else 1

    def update(self, value):
    	if self.parent != None:
    		self.parent.update(value*-1)
    	self.N +=1
    	self.Q += 1*(value-self.Q)/self.N

    def select(self, puct):
    	return max(self.children.items(), key=lambda x:x[1].get_value(puct))

    def get_value(self, puct):
    	self.u = puct * math.sqrt(self.parent.visits) / (self.N+1)
    	return self.Q+self.u

class MCTS():
    
    def __init__(self, color):
        self.root = Node(None)
        
    def search(self, board, turn):
        #rollout
        node,board = self._select(node,board,turn)
        win = board.is_win()

        if win==0 and len(board.all_moves)>0:
        	self._expand(node, board.all_moves)

        win_value = self._simulate(board, turn)
        self._backprop(node, win_value)

        #print("wins:", self.win[node])
        #print("out of:", self.count[node])
        #print("number of children:", len(self.children[node]))

    def _select(self, node, board, turn):
        while True:
        	if node.is_terminal(): #no children
        		break
        	puct = 5
        	action = node.select(puct)
        	board.make_move(action, turn)
        	if turn == 1:
        		turn = 2
        	else:
        		turn = 1
        	board.all_moves = board.get_all_possible_moves()
 
        return node,board 

    def _expand(self, node, moves):
        #expand on the node - add to children
        for move in moves:
        	if node.children.get(move)==None:
        		node.children[move] = Node(self) 

    def _simulate(self, board, turn):
        #return reward for random simulation
        win_value = 0
        for i in range(500): # set a limit. if it hits, return 0 instead.
            win_value = board.is_win()
            if win_value!=0:
                break
            move = self.random_child(board, turn)
            board.make_move(move, turn)
            if turn == 1:
        		turn = 2
        	else:
        		turn = 1
        	board.all_moves = board.get_all_possible_moves()
        #if win_value == 1, that means BLACK won. if 2, WHITE won.
       	if win_value == 0:
       		return 0
        return 1 if win_value==turn else -1

    def _backprop(self, node, win_value):
        node.update(win_value)

    def _ucb(self, node):
        #to select next node
        x = 2*math.log(self.count[node])
        ucb_lst = [(n, (self.win[n]/self.count[n] + math.sqrt(x/self.count[n]))) for n in self.children[node]] 
        #add second key later
        best_node = max(ucb_lst, key=lambda x:x[1])[0]
        return best_node

    def random_child(self, board, turn):
        moves = board.get_all_possible_moves(turn)
        index = randint(0,len(moves)-1)
        inner_index = randint(0,len(moves[index])-1)
        move = moves[index][inner_index]
        return move

    def best_child(self):
    	print("in best child")
    	print("self.root.children: ", self.root.children)
    	return max(self.root.children.items(), key=lambda x:x[1].N)[0] #max by number of visits, and get move

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
        self.board.all_moves = moves
        if len(moves)==1 and len(moves[0])==1:
            move = moves[0][0]
        else:
            tree = MCTS(self.color)
            move = self.playout(tree,self.board,move)

        self.board.make_move(move,self.color)
        return move

    def playout(self,tree,board,move):
        now = time.time()
        timer = 0
        i = 0
        while timer<=15:
            end = time.time()
            board = copy.deepcopy(board)
            tree.search(board)
            i += 1
            if i>1500:
                break
            timer = end-now
        return tree.best_child()
