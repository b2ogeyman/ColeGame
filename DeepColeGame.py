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

class TicTacToe():

    def __init__(self, player1, player2, exp1=1, exp2=1):
        self.n = 13
        self.state = np.zeros((self.n, self.n))

        player1 = globals()[player1]
        self.player1 = player1(tag='X', exploration_factor=exp1)
        player2 = globals()[player2]
        self.player2 = player2(tag='O', exploration_factor=exp2)

        self.winner = None
        self.turn = 'X'
        self.player_turn = self.player1

        self.Xcount = 0
        self.Ocount = 0
        self.all_count = 0

    def play_game(self):

        while self.winner is None:

            if type(self.player_turn) == Player:
                print(self.turn)
                self.print_game()

            self.state = self.play_move()
            self.game_winner()

            if self.winner is not None:
                break

        self.print_game()

    def play_to_learn(self, episodes):

        for i in range(episodes):
            # print('Episode number: ' + str(i))

            while self.winner is None:
                self.state = self.play_move(learn=True)
                self.game_winner()

                if self.winner is not None:
                    break

                self.state = self.play_move(learn=True)
                self.game_winner()

            # update last state
            self.state = self.play_move(learn=True)
            self.state = self.play_move(learn=True)
            # update winning state
            self.state = self.play_move(learn=True)
            self.state = self.play_move(learn=True)

            if i% 500 == 0:
                self.print_bar()
                print('-------------------')
                self.print_summary()
                self.player1.print_value = True
            else:
                self.player1.print_value = False

            if i % 2000 == 0:
                self.Xcount = 0
                self.Ocount = 0

            self.all_count = i
            self.init_game()

        self.print_summary()
        self.player1.save_values()
        self.player2.save_values()

    def play_move(self, learn=False):

        if self.turn == 'X':
            if learn is True:
                new_state = self.player1.make_move_and_learn(self.state, self.winner)
            else:
                new_state = self.player1.make_move(self.state, self.winner)
            self.turn = 'O'
            self.player_turn = self.player2
        else:
            if learn is True:
                new_state = self.player2.make_move_and_learn(self.state, self.winner)
            else:
                new_state = self.player2.make_move(self.state, self.winner)
            self.turn = 'X'
            self.player_turn = self.player1
        return new_state

    def show_board(self):
        result = "   a b c d e f g h j k l m n\n"
        for i in range(self.n):
            result += str(i).zfill(2) + ' '
            for j in range(self.n):
                if self.state[i][j] == 1:
                    result += 'X '
                elif self.state[i][j] == -1:
                    result += 'O '
                else:
                    result += '. '
            result += '\n'
        return result

    def print_game(self):
        print(self.show_board())

    def valid(self, x, y):
        return (0 <= x and x < self.n and 0 <= y and y < self.n)
    def feasible(self,state, x,y,player):
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
        for i in range(4):
            if not self.feasible(state, x+dir_dict[dr][0]*i, y+dir_dict[dr][1]*i, player):
                return False
        return True

    def can_move(self):
        for i in range(self.n):
            for j in range(self.n):
                for k in range(4):
                    if self.valid_move(self.state, i, j, k, self.turn):
                        return True
        return False
        


    def game_winner(self):
        if not self.can_move():
            if self.turn == 'X':
                self.winner = 'O'
            else:
                self.winner = 'X'
        else:
            self.winner = None
        return self.winner

    def init_game(self):
        self.state = np.zeros((self.n, self.n))
        self.winner = None
        self.turn = 'X'
        self.player_turn = self.player1



class Player():

    def __init__(self, tag, exploration_factor=1):
        self.tag = tag
        self.n = 13
        self.print_value = False
        self.exp_factor = exploration_factor
        if self.tag == 'X':
            self.num = 1
        else:
            self.num = -1

    def show_board(self, state):
        result = "   a b c d e f g h j k l m n\n"
        for i in range(self.n):
            result += str(self.n - i).zfill(2) + ' '
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
        for i in range(4):
            if not self.feasible(state, x+dir_dict[dr][0]*i, y+dir_dict[dr][1]*i, player):
                return False
        return True

    def make_move(self, state, winner):
        i, j, dr = map(int, input('Choose move number: ').split(' '))
        s = state[:]
        for k in range(4):
            s[i+dir_dict[dr][0]*k][j+dir_dict[dr][1]*k] = self.num
        return s


class Agent(Player):

    def __init__(self, tag, exploration_factor=1):
        super().__init__(tag, exploration_factor)
        self.epsilon = 0.1
        self.alpha = 0.5
        self.prev_state = np.zeros((self.n, self.n))
        self.state = None
        self.print_value = False

        if self.tag == 'X':
            self.op_tag = 'O'
            self.num = 1
        else:
            self.op_tag = 'X'
            self.num = -1

    def make_move(self, state, num, i, j, dr):
        new_state = state[:]
        for k in range(4):
            new_state[i+dir_dict[dr][0]*k][j+dir_dict[dr][1]*k] = num
        return new_state

    def get_moves(self, state, tag):
        moves = []
        for i in range(self.n):
            for j in range(self.n):
                for dr in range(4):
                    if self.valid_move(state, i, j, dr, self.tag):
                        moves.append((i, j, dr))
        return moves


    def make_random_move(self, state, tag):
        moves = []
        for i in range(self.n):
            for j in range(self.n):
                for dr in range(4):
                    if self.valid_move(state, i, j, dr, self.tag):
                        moves.append((i, j, dr))
        if moves.empty():

        i, j, dr = random.choice(moves)
        return self.make_move(state, self.num, i, j, dr)

    def eval_pos(self, state):
        win = 0
        tot = 10
        for qq in range(tot):
            cur_state = state[:]
            moves = self.get_moves(cur_state, self.tag)
            moves_op = self.get_moves(cur_state, self.op_tag)
            while not moves_op.empty() and not moves.empty():
                ind = np.randint(len(moves_op))
                i, j, dr = moves_op[ind]
                game_won = 0
                while not self.valid_move(cur_state, i, j, dr, self.op_tag):
                    del moves_op[ind]
                    if moves_op.empty():
                        game_won = 1
                        break
                    ind = np.randint(len(moves_op))
                    i, j, dr = moves_op[ind]
                if game_won == 1:
                    win += 1
                    break
                cur_state = self.make_move(cur_state, self.op_tag)
                ind = np.randint(len(moves))
                i, j, dr = moves[ind]
                while not self.valid_move(cur_state, i, j, dr, self.tag):
                    del moves[ind]
                    if moves.empty():
                        break
                    ind = np.randint(len(moves))
                    i, j, dr = moves[ind]
        return win/tot
        




    def make_good_move(self, state, winner):

        moves = self.get_moves(state, self.tag)
        best = 0

        for i, j, dr in moves:
            temp_state = self.make_move(state, self.num, i, j, dr)
            ev = self.eval_pos(temp_state)
            if ev > best:
                best = ev
                best_move = (i, j, dr)

        return self.make_move(state, self.num, best_move[0], best_move[1], best_move[2])



def check_player():
     #print('QAgent X 1 and QAgent 1 0')
     #game = TicTacToe('QAgent', 'QAgent', 1, 0)
     #game.play_to_learn(1000)
    game = ColeGame('Player', 'Player', 0.8, 0.8)
    game.play_game()


check_player()