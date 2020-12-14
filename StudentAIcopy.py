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
    
    def __init__(self,parent,prob):
        self.u = 0
        self.parent = parent
        self.children = {}
        self.N = 0
        self.Q = 0
        self.p = prob

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
        return self.children=={}
    
    def turn_rotation(self):
        return 2 if self.color==1 else 1

    def update(self, value):
        if self.parent != None:
            self.parent.update(-value)
        self.N += 1
        self.Q += 1*(value-self.Q)/self.N

    def select(self, puct):
        return max(self.children.items(), key=lambda x:x[1].get_value(puct))

    def get_value(self, puct):
        self.u = puct * self.p * math.sqrt(self.parent.N) / (self.N+1)
        return self.Q+self.u

class MCTS():
    
    def __init__(self):
        self.root = Node(None,1)

    def update_tree(self, prev_move):
        #has issues
        if self.root.children.get(prev_move) != None:
            self.root = self.root.children[prev_move]
            self.parent = None
        else:
            self.root = Node(None,1)
        
    def search(self, board, turn):
        #rollout
        node = self.root
        node,board,turn,actions = self._select(node,board,turn)
        win = board.is_win(turn)
        
        if win==0:
            self._expand(node,actions)

        win_value = self._simulate(board, turn)
        self._backprop(node, win_value)

    def _select(self, node, board, turn):
        while True:
            if node.is_terminal(): #no children
                break
            puct = 5
            action,node = node.select(puct)
            board.make_move(action, turn)
            if turn == 1:
                turn = 2
            else:
                turn = 1
            board_moves = []
            for m in board.get_all_possible_moves(turn):
                board_moves.extend(m)
            board.all_moves = tuple(board_moves)
        actions = []
        for m in board.all_moves:
            actions.append([m,1/len(board.all_moves)])
        return node,board,turn,actions 

    def _expand(self, node, actions):
        #expand on the node - add to children
        for m,prob in actions:
            if node.children.get(m)==None:
                node.children[m] = Node(node,prob) 

    def _simulate(self, board, p):
        #return reward for random simulation
        #print("SIMULATION BEGIN")
        win_value = 0
        p2 = p
        for i in range(800): # set a limit. if it hits, return 0 instead.
            #board.show_board()
            #print("it is player: ", p2,"'s turn above")
            #win_value = self.game_value(board,p2)
            win_value = board.is_win(p2)
            if win_value!=0:
                break
            if len(board.all_moves)==0:
                break
            move = self.random_child(board, p2)
            board.make_move(move, p2)
            if p2 == 1:
                p2 = 2
            else:
                p2 = 1
            board_moves = []
            for m in board.get_all_possible_moves(p2):
                board_moves.extend(m)
            board.all_moves = tuple(board_moves)
       
        if win_value == 0:
       	    return 0
        #print("winvalue is: ", win_value)
        #print("winvalue==p? on turn", p, win_value==p)
        return 1 if win_value==p else -1

    def _backprop(self, node, win_value):
        node.update(win_value)

    def _ucb(self, node):
        #to select next node
        x = 2*math.log(self.count[node])
        ucb_lst = [(n, (self.win[n]/self.count[n] + math.sqrt(x/self.count[n]))) for n in self.children[node]] 
        #add second key later
        best_node = max(ucb_lst, key=lambda x:x[1])[0]
        return best_node
    
    def game_value(self, board, turn):
        winner= board.is_win(self.turn_rotation(turn))
        return winner

    def turn_rotation(self, turn):
        return 2 if turn==1 else 1    

    def random_child(self, board, turn):
        index = randint(0,len(board.all_moves)-1)
        move = board.all_moves[index]
        return move

    def best_child(self):
        #for move, child in self.root.children.items():
        #    print(move, child.N, child.Q)
        a = max(self.root.children.items(), key=lambda x:x[1].N) #max by number of visits, and get move
        #print("what's returned:", a[0], a[1].N, a[1].Q)
        return a[0]

class StudentAI():

    def __init__(self,col,row,p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col,row,p)
        self.board.initialize_game()
        self.opponent = {1:2,2:1}
        self.color = 2
        self.max_time = 480
        self.remaining_time = self.max_time

    def get_move(self,move):
        now = time.time()
        if len(move) != 0:
            self.board.make_move(move,self.opponent[self.color])
        else:
            self.color = 1 
        #color is based on who goes first.
        #if student ai goes first, color = 1
        #if I go first, color = 2 (bc ai goes second)
        
        #optimize 1 moves
        moves = self.board.get_all_possible_moves(self.color)
        board_moves = []
        for m in moves:
            board_moves.extend(m)
        self.board.all_moves = tuple(board_moves)
        if len(moves)==1 and len(moves[0])==1:
            move = moves[0][0]
        else:
            if self.remaining_time<30:
                iter_time = 3
            else:
                iter_time = 15 #default
            tree = MCTS()
            move = self.playout(tree,iter_time,self.board,move,self.color)

        #self.tree.update_tree(move)
        self.board.make_move(move,self.color)
        end = time.time()
        self.remaining_time -=(end-now)
        return move

    def playout(self,tree,iter_time,board,move,turn):
        now = time.time()
        timer = 0
        i = 0
        while timer<=iter_time:
            end = time.time()
            board2 = copy.deepcopy(board)
            #print("AI TURN:", turn)
            tree.search(board2,turn)
            #print("iteration: ", i)
            i += 1
            if i>1000:
                break
            timer = end-now
        return tree.best_child()
