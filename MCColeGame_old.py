import random
import csv
import os
from pathlib import Path
from tabulate import tabulate
from abc import abstractmethod
import keras.layers as Kl
import keras.models as Km
import numpy as np
import matplotlib.pyplot as plt


dir_dict = {0:(-1, 0), 1:(1, 0), 2:(0, -1), 3:(0, 1)}
dir_angle_dict = {0:(1, 1), 1:(-1, 1), 2:(1, -1), 3:(-1, -1)}
dir_str_dict = {"U":0, "D":1, "L":2, "R":3}

class ColeGame():

    def __init__(self, player1, player2):
        self.n = 9
        self.state = np.zeros((self.n, self.n), dtype=int)
        player1 = globals()[player1]
        self.player1 = player1(tag='X')
        player2 = globals()[player2]
        self.player2 = player2(tag='O')
        self.winner = None
        self.turn = 'X'
        self.player_turn = self.player1

        self.Xcount = 0
        self.Ocount = 0
        self.all_count = 0

    def play_game(self):

        while True:

            #if type(self.player_turn) == Player:
                #print(self.turn)
            self.print_game()
            new_state = self.play_move()
            if np.array_equal(new_state, self.state):
                print(self.turn + '\'s won!')
                break
            self.state = new_state
            #self.game_winner()

           #if self.winner is not None:
               # break

        #self.print_game()


    def play_move(self):

        if self.turn == 'X':
            new_state = self.player1.make_move(self.state)
            self.turn = 'O'
            self.player_turn = self.player2
        else:
            new_state = self.player2.make_move(self.state)
            #print(self.show_board(new_state))
            self.turn = 'X'
            self.player_turn = self.player1
        return new_state

    def show_board(self, state):
        result = "   a b c d e f g h i\n"
        for i in range(self.n):
            result += str(i).zfill(2) + ' '
            for j in range(self.n):
                if state[i][j] == 1:
                    result += 'X '
                elif state[i][j] == -1:
                    result += 'O '
                else:
                    result += '. '
            result += '\n'
        return result

    def print_game(self):
        print(self.show_board(self.state))


class Player():

    def __init__(self, tag):
        self.tag = tag
        self.n = 9
        self.len = 3
        self.print_value = False
        if self.tag == 'X':
            self.num = 1
        else:
            self.num = -1

    def show_board(self, state):
        result = "   a b c d e f g h i j k l m\n"
        for i in range(self.n):
            result += str(i).zfill(2) + ' '
            for j in range(self.n):
                if state[i][j] == 1:
                    result += 'X '
                elif state[i][j] == -1:
                    result += 'O '
                else:
                    result += '. '
            result += '\n'
        return result

    def valid(self, x, y):
        return (0 <= x and x < self.n and 0 <= y and y < self.n)
    def feasible(self,state, x,y,player):
        if not self.valid(x, y):
            return False
        if state[x][y] != 0:
            return False
        if player == 'X':
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                if self.valid(x+dx, y+dy) and state[x+dx][y+dy] == -1:
                    return False
            return True
        else:
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                if self.valid(x+dx, y+dy) and state[x+dx][y+dy] == 1:
                    return False
            return True

    def valid_move(self, state, x, y, dr, player):
        for i in range(self.len):
            if not self.feasible(state, x+dir_dict[dr][0]*i, y+dir_dict[dr][1]*i, player):
                return False
        return True

    def get_moves(self, state, tag):
        moves = []
        for i in range(self.n):
            for j in range(self.n):
                for dr in range(self.len):
                    if self.valid_move(state, i, j, dr, tag):
                        moves.append((i, j, dr))
        return moves

    def apply_move_in_place(self, state, i, j, dr, num):
        for k in range(self.len):
            state[i+dir_dict[dr][0]*k][j+dir_dict[dr][1]*k] = num

    def apply_move(self, state, i, j, dr, num):
        new_state = np.copy(state)
        for k in range(self.len):
            new_state[i+dir_dict[dr][0]*k][j+dir_dict[dr][1]*k] = num
        return new_state

    def undo_move_in_place(self, state, i, j, dr):
        for k in range(self.len):
            state[i+dir_dict[dr][0]*k][j+dir_dict[dr][1]*k] = 0


    def valid_angle_move(self, state, x, y, dr, player):
        dx, dy = dir_angle_dict[dr]
        if not self.feasible(state, x, y, player) or not self.feasible(state, x+dx, y, player) or not self.feasible(state, x, y+dy, player):
                return False
        return True

    def get_angle_moves(self, state, tag):
        moves = []
        for i in range(self.n):
            for j in range(self.n):
                for dr in range(self.len):
                    if self.valid_angle_move(state, i, j, dr, tag):
                        moves.append((i, j, dr))
        return moves

    def apply_angle_move_in_place(self, state, i, j, dr, num):
        dx, dy = dir_angle_dict[dr]
        state[i][j] = num
        state[i+dx][j] = num
        state[i][j+dy] = num

    def apply_angle_move(self, state, i, j, dr, num):
        new_state = np.copy(state)
        dx, dy = dir_angle_dict[dr]
        new_state[i][j] = num
        new_state[i+dx][j] = num
        new_state[i][j+dy] = num
        return new_state

    def undo_angle_move_in_place(self, state, i, j, dr):
        dx, dy = dir_angle_dict[dr]
        state[i][j] = 0
        state[i+dx][j] = 0
        state[i][j+dy] = 0

    def make_move(self, state):
        lt, i, dr = input('Choose move number: ').split(' ')
        i = int(i)
        j = ord(lt[0]) - ord('a')
        dr = dir_str_dict[dr]

        s = self.apply_move(state, i, j, dr, self.num)
        return s


class Agent(Player):

    def __init__(self, tag):
        super().__init__(tag)
        self.state = None
        self.print_value = False

        if self.tag == 'X':
            self.op_tag = 'O'
            self.num = 1
        else:
            self.op_tag = 'X'
            self.num = -1




    def eval_pos(self, state):
        win = 0
        tot = 10
        for qq in range(tot):
            cur_state = np.copy(state)
            #print(self.show_board(cur_state))
            moves = self.get_moves(cur_state, self.tag)
            moves_op = self.get_moves(cur_state, self.op_tag)
            while moves_op and moves:
                ind = np.random.randint(len(moves_op))
                i, j, dr = moves_op[ind]
                #print(i, j, dr)
                game_won = 0
                while not self.valid_move(cur_state, i, j, dr, self.op_tag):
                    del moves_op[ind]
                    if not moves_op:
                        game_won = 1
                        break
                    ind = np.random.randint(len(moves_op))
                    i, j, dr = moves_op[ind]
                if game_won == 1:
                    win += 1
                    break
                #print(i, j, dr)
                self.apply_move_in_place(cur_state, i, j, dr, -self.num)
                #print(self.show_board(cur_state))
                ind = np.random.randint(len(moves))
                i, j, dr = moves[ind]
                while not self.valid_move(cur_state, i, j, dr, self.tag):
                    del moves[ind]
                    if not moves:
                        break
                    ind = np.random.randint(len(moves))
                    i, j, dr = moves[ind]
                self.apply_move_in_place(cur_state, i, j, dr, self.num)
                #print(self.show_board(cur_state))
                #print(len(moves))
                #print(len(moves_op))
        return win/tot
        

class Agent_Angle(Player):

    def __init__(self, tag):
        super().__init__(tag)
        self.state = None
        self.print_value = False

        if self.tag == 'X':
            self.op_tag = 'O'
            self.num = 1
        else:
            self.op_tag = 'X'
            self.num = -1



    def eval_pos(self, state):
        win = 0
        tot = 10
        for qq in range(tot):
            cur_state = np.copy(state)
            #print(self.show_board(cur_state))
            moves = self.get_moves(cur_state, self.tag)
            moves_op = self.get_moves(cur_state, self.op_tag)
            while moves_op and moves:
                ind = np.random.randint(len(moves_op))
                i, j, dr = moves_op[ind]
                #print(i, j, dr)
                game_won = 0
                while not self.valid_move(cur_state, i, j, dr, self.op_tag):
                    del moves_op[ind]
                    if not moves_op:
                        game_won = 1
                        break
                    ind = np.random.randint(len(moves_op))
                    i, j, dr = moves_op[ind]
                if game_won == 1:
                    win += 1
                    break
                #print(i, j, dr)
                self.apply_move_in_place(cur_state, i, j, dr, -self.num)
                #print(self.show_board(cur_state))
                ind = np.random.randint(len(moves))
                i, j, dr = moves[ind]
                while not self.valid_move(cur_state, i, j, dr, self.tag):
                    del moves[ind]
                    if not moves:
                        break
                    ind = np.random.randint(len(moves))
                    i, j, dr = moves[ind]
                self.apply_move_in_place(cur_state, i, j, dr, self.num)
                #print(self.show_board(cur_state))
                #print(len(moves))
                #print(len(moves_op))
        return win/tot
        



    def make_move(self, state):

        moves = self.get_moves(state, self.tag)
        if not moves:
            return state
        best = 0
        #print(self.show_board(state))
        for i, j, dr in moves:
            #print(i, j, dr)
            self.apply_move_in_place(state, i, j, dr, self.num)
            ev = self.eval_pos(state)
            if ev >= best:
                best = ev
                best_move = (i, j, dr)
            self.undo_move_in_place(state, i, j, dr)
        print(best_move)
        #print(self.show_board(state))
        return self.apply_move(state, best_move[0], best_move[1], best_move[2], self.num)

    def make_random_move(self, state):
        moves = self.get_moves(state, self.tag)
        if not moves:
            return state
        #print(self.show_board(state))
        best_move = random.choice(moves)
        #print(self.show_board(state))
        return self.apply_move(state, best_move[0], best_move[1], best_move[2], self.num)

   
def check_player():
    game = ColeGame('Agent', 'Agent')
    game.play_game()


check_player()