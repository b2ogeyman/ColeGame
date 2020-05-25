import random
import numpy as np
import argparse

dir_dict = {0:(-1, 0), 1:(1, 0), 2:(0, -1), 3:(0, 1)}
dir_angle_dict = {0:(1, 1), 1:(-1, 1), 2:(1, -1), 3:(-1, -1)}
dir_str_dict = {"u":0, "d":1, "l":2, "r":3}
dirs = 'UDLR'
dir_str_angle_dict = {"dr": 0, 'ur':1, 'dl':2, 'ul':3}
dirs_angle = ['dr', 'ur', 'dl', 'ul']

class ColeGame():

    def __init__(self, player1, tp1, player2, tp2, filename, num, printing):
        self.n = 9
        self.savefile = open(filename, 'a')
        self.print = printing
        #print(self.print)
        self.state = np.zeros((self.n, self.n), dtype=int)
        player1 = globals()[player1]
        self.player1 = player1(tot=num, tag='X', tp=tp1, opp=tp2)
        player2 = globals()[player2]
        self.player2 = player2(tot=num, tag='O', tp=tp2, opp=tp1)
        self.winner = None
        self.turn = 'X'
        self.player_turn = self.player1
        self.last_move = None
        self.savefile.write('\n----------------------------\n\n')

    def play_game(self):

        while True:

            #if type(self.player_turn) == Player:
                #print(self.turn)
            self.print_game()
            new_state = self.play_move()
            if np.array_equal(new_state, self.state):
                print(self.turn + '\'s won!')
                self.savefile.write(self.turn + '\'s won!' + '\n')
                break
            self.state = new_state
            #self.game_winner()

           #if self.winner is not None:
               # break

        #self.print_game()


    def play_move(self):

        if self.turn == 'X':
            new_state, self.last_move = self.player1.make_move(self.state, self.last_move)
            self.turn = 'O'
            self.player_turn = self.player2
        else:
            new_state, self.last_move = self.player2.make_move(self.state, self.last_move)
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
        if self.print:
            print(self.show_board(self.state))
        self.savefile.write(self.show_board(self.state)+'\n')


class Player():

    def __init__(self, tot, tag, tp, opp):
        self.tag = tag
        self.tot = tot
        self.opp = opp
        self.type = tp
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
                for dr in range(4):
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
                for dr in range(4):
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

class Human(Player):
    def __init__(self, tot, tag, tp, opp):
        super().__init__(tot, tag, tp, opp)
        self.type = tp

    def make_move(self, state, last_move):
        lt, i, dr = input('Choose move number: ').split(' ')
        i = int(i)
        j = ord(lt[0]) - ord('a')
        if self.type == 'line':
            dr = dir_str_dict[dr]
        else:
            dr = dir_str_angle_dict[dr]
        if self.type == 'line':
            s = self.apply_move(state, i, j, dr, self.num)
        else:
            s = self.apply_angle_move(state, i, j, dr, self.num)
        return s, (i, j, dr)

class Agent(Player):

    def __init__(self, tot, tag, tp, opp):
        super().__init__(tot, tag, tp, opp)
        self.get = self.get_moves if self.type == 'line' else self.get_angle_moves
        self.opp_get = self.get_moves if self.opp == 'line' else self.get_angle_moves
        self.allowed = self.valid_move if self.type == 'line' else self.valid_angle_move
        self.opp_allowed = self.valid_move if self.opp == 'line' else self.valid_angle_move
        self.apply_in_place = self.apply_move_in_place if self.type == 'line' else self.apply_angle_move_in_place
        self.opp_apply_in_place = self.apply_move_in_place if self.opp == 'line' else self.apply_angle_move_in_place
        self.undo = self.undo_move_in_place if self.type == 'line' else self.undo_angle_move_in_place
        self.apply = self.apply_move if self.type == 'line' else self.apply_angle_move
        if self.tag == 'X':
            self.op_tag = 'O'
            self.num = 1
        else:
            self.op_tag = 'X'
            self.num = -1




    def eval_pos(self, state):
        win = 0
        for qq in range(self.tot):
            cur_state = np.copy(state)
            #print(self.show_board(cur_state))
            moves = self.get(cur_state, self.tag)

            moves_op = self.opp_get(cur_state, self.op_tag)
            if not moves_op:
                return 1.0
            if not moves:
                return 0.0
            while moves_op and moves:
                ind = np.random.randint(len(moves_op))
                i, j, dr = moves_op[ind]
                #print(i, j, dr)
                game_won = 0
                while not self.opp_allowed(cur_state, i, j, dr, self.op_tag):
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
                self.opp_apply_in_place(cur_state, i, j, dr, -self.num)
                #print(self.show_board(cur_state))
                ind = np.random.randint(len(moves))
                i, j, dr = moves[ind]
                while not self.allowed(cur_state, i, j, dr, self.tag):
                    del moves[ind]
                    if not moves:
                        break
                    ind = np.random.randint(len(moves))
                    i, j, dr = moves[ind]
                self.apply_in_place(cur_state, i, j, dr, self.num)
                #print(self.show_board(cur_state))
                #print(len(moves))
                #print(len(moves_op))
        return win/self.tot


    def make_move(self, state, last_move):

        moves = self.get(state, self.tag)
        if not moves:
            return state, None
        best = 0
        #print(self.show_board(state))
        for i, j, dr in moves:
            #print(i, j, dr)
            self.apply_in_place(state, i, j, dr, self.num)
            ev = self.eval_pos(state)
            if ev >= best:
                best = ev
                best_move = (i, j, dr)
            self.undo(state, i, j, dr)
        print(best)
        print(len(moves))
        if self.type == 'line':
            print(str(chr(ord('a')+best_move[1])) + ' ' + str(best_move[0]) + ' ' + dirs[best_move[2]])
        else:
            print(str(chr(ord('a')+best_move[1])) + ' ' + str(best_move[0]) + ' ' + dirs_angle[best_move[2]])
        #print(self.show_board(state))
        return self.apply(state, best_move[0], best_move[1], best_move[2], self.num), best_move



class Node():
    def __init__(self, par):
        self.w = 0
        self.tot = 0
        self.par = par
        self.dct = {}
        self.unexplored_moves = []

class AgentMC(Player):
    def __init__(self, tot, tag, tp, opp):
        super().__init__(tot, tag, tp, opp)
        self.get = self.get_moves if self.type == 'line' else self.get_angle_moves
        self.opp_get = self.get_moves if self.opp == 'line' else self.get_angle_moves
        self.allowed = self.valid_move if self.type == 'line' else self.valid_angle_move
        self.opp_allowed = self.valid_move if self.opp == 'line' else self.valid_angle_move
        self.apply_in_place = self.apply_move_in_place if self.type == 'line' else self.apply_angle_move_in_place
        self.opp_apply_in_place = self.apply_move_in_place if self.opp == 'line' else self.apply_angle_move_in_place
        self.undo = self.undo_move_in_place if self.type == 'line' else self.undo_angle_move_in_place
        self.opp_undo = self.undo_move_in_place if self.opp == 'line' else self.undo_angle_move_in_place
        self.apply = self.apply_move if self.type == 'line' else self.apply_angle_move
        if self.tag == 'X':
            self.op_tag = 'O'
            self.num = 1
        else:
            self.op_tag = 'X'
            self.num = -1
        self.C = np.sqrt(2)
        self.num_rolls = 10000 
        self.root = Node(None)

    def rollout(self, state, turn):
        cur_state = np.copy(state)
            #print(self.show_board(cur_state))
        moves = self.get(cur_state, self.tag)

        moves_op = self.opp_get(cur_state, self.op_tag)
        if turn == self.tag:
            if not moves:
                return 0
            ind = np.random.randint(len(moves))
            i, j, dr = moves[ind]
            while not self.allowed(cur_state, i, j, dr, self.tag):
                del moves[ind]
                if not moves:
                    return 0
                ind = np.random.randint(len(moves))
                i, j, dr = moves[ind]
            self.apply_in_place(cur_state, i, j, dr, self.num)

        if not moves_op:
            return 1

        while moves_op and moves:
            ind = np.random.randint(len(moves_op))
            i, j, dr = moves_op[ind]
            #print(i, j, dr)
            while not self.opp_allowed(cur_state, i, j, dr, self.op_tag):
                del moves_op[ind]
                if not moves_op:
                    return 1
                ind = np.random.randint(len(moves_op))
                i, j, dr = moves_op[ind]
            #print(i, j, dr)
            self.opp_apply_in_place(cur_state, i, j, dr, -self.num)
            #print(self.show_board(cur_state))
            ind = np.random.randint(len(moves))
            i, j, dr = moves[ind]
            while not self.allowed(cur_state, i, j, dr, self.tag):
                del moves[ind]
                if not moves:
                    return 0
                ind = np.random.randint(len(moves))
                i, j, dr = moves[ind]
            self.apply_in_place(cur_state, i, j, dr, self.num)
        return 0

    def build_tree(self, state):
        cur_state = np.copy(state)
        num_rolls = 0
        done = False
        #root.unexplored_moves = self.get(cur_state, self.tag)
        def dfs(cur_node, depth):
            nonlocal cur_state
            nonlocal num_rolls
            nonlocal done
            #num_rolls += 1
            if depth % 2 == 0:
                if cur_node.unexplored_moves:
                    i, j, dr = random.choice(cur_node.unexplored_moves)
                    self.apply_in_place(cur_state, i, j, dr, self.num)
                    cur_node.dct[(i, j, dr)] = Node(cur_node)
                    cur_node.dct[(i, j, dr)].unexplored_moves = self.opp_get(cur_state, self.op_tag)
                    win = self.rollout(cur_state, self.op_tag)
                    num_rolls += 1
                    cur_node.dct[(i, j, dr)].tot += 1
                    cur_node.dct[(i, j, dr)].w += win
                    cur_node.tot+= 1
                    cur_node.w += win
                    self.undo(cur_state, i, j, dr)
                    cur_node.unexplored_moves.remove((i, j, dr))
                    return win
                else:
                    best = 0
                    for key, value in cur_node.dct.items():
                        if best <= value.w/value.tot + self.C*np.sqrt(np.log(cur_node.tot)/value.tot):
                            best = value.w/value.tot + self.C*np.sqrt(np.log(cur_node.tot)/value.tot)
                            i, j, dr = key
                    if best == 0:
                        done = True
                        return 0
                    self.apply_in_place(cur_state, i, j, dr, self.num)
                    win = dfs(cur_node.dct[(i, j, dr)], depth + 1)
                    cur_node.w += win
                    cur_node.tot += 1
                    self.undo(cur_state, i, j, dr)
                    return win
            else:

                if cur_node.unexplored_moves:
                    i, j, dr = random.choice(cur_node.unexplored_moves)
                    self.opp_apply_in_place(cur_state, i, j, dr, -self.num)
                    cur_node.dct[(i, j, dr)] = Node(cur_node)
                    cur_node.dct[(i, j, dr)].unexplored_moves = self.get(cur_state, self.tag)
                    win = self.rollout(cur_state, self.tag)

                    num_rolls += 1
                    cur_node.dct[(i, j, dr)].tot += 1
                    cur_node.dct[(i, j, dr)].w += win
                    cur_node.tot+= 1

                    cur_node.w += win
                    self.opp_undo(cur_state, i, j, dr)
                    cur_node.unexplored_moves.remove((i, j, dr))
                    return win
                else:
                    best = 0
                    for key, value in cur_node.dct.items():
                        if best <= (value.tot - value.w)/value.tot + self.C*np.sqrt(np.log(cur_node.tot)/value.tot):
                            best = (value.tot - value.w)/value.tot + self.C*np.sqrt(np.log(cur_node.tot)/value.tot)
                            i, j, dr = key
                    if best == 0:
                        done = True
                        return 0
                    self.opp_apply_in_place(cur_state, i, j, dr, -self.num)
                    win = dfs(cur_node.dct[(i, j, dr)], depth + 1)
                    cur_node.w += win
                    cur_node.tot += 1
                    self.opp_undo(cur_state, i, j, dr)
                    return win
        while num_rolls < self.num_rolls:
            dfs(self.root, 0)
            if done:
                break



    def make_move(self, state, last_move):

        if last_move in self.root.dct:
            self.root = self.root.dct[last_move]
        else:
            self.root = Node(None)
            self.root.unexplored_moves = self.get(state, self.tag)

        self.build_tree(state)
        #print(len(self.root.dct))

        moves = self.get(state, self.tag)
        if not moves:
            return state, None
        best = 0
        #print(self.show_board(state))
        for key, value in self.root.dct.items():
            #print(i, j, dr)
            if value.w/value.tot >= best:
                best = value.w/value.tot
                best_move = key

        self.root = self.root.dct[best_move]

        print(best)
        print(len(moves))
        if self.type == 'line':
            print(str(chr(ord('a')+best_move[1])) + ' ' + str(best_move[0]) + ' ' + dirs[best_move[2]])
        else:
            print(str(chr(ord('a')+best_move[1])) + ' ' + str(best_move[0]) + ' ' + dirs_angle[best_move[2]])
        #print(self.show_board(state))
        return self.apply(state, best_move[0], best_move[1], best_move[2], self.num), best_move





        

class Rando(Player):
    def __init__(self, tot, tag, tp, opp):
        super().__init__(tot, tag, tp, opp)
        self.type = tp
        self.get = self.get_moves if self.type == 'line' else self.get_angle_moves
        self.apply = self.apply_move if self.type == 'line' else self.apply_angle_move

    def make_move(self, state, last_move):
        moves = self.get(state, self.tag)
        if not moves:
            return state, None
        #print(self.show_board(state))
        best_move = random.choice(moves)
        #print(self.show_board(state))
        return self.apply(state, best_move[0], best_move[1], best_move[2], self.num), best_move


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--first', type=str, default='botmc_line',
                        help='First player')
    parser.add_argument('--second', type=str, default='botmc_line',
                        help='Second Player')
    parser.add_argument('--num', type=int, default=50,
                        help='Number of random games in the Monte Carlo evaluation')
    parser.add_argument('--logfile', type=str, default='./game_log.txt',
                        help='File to record the games')
    parser.add_argument('--noprint', action='store_false', default=True,
                        help='Print')
    return parser.parse_args()

def main():
    args = get_arguments()
    if args.first == 'bot_line' or args.first == 'bot_angle':
        p1 = 'Agent'
        t1 = args.first[4:]
    elif args.first == 'human_line' or args.first == 'human_angle':
        p1 = 'Human'
        t1 = args.first[6:]
    elif args.first == 'botmc_line' or args.first == 'botmc_angle':
        p1 = 'AgentMC'
        t1 = args.first[6:]
    else:
        p1 = 'Rando'
        t1 = args.first[7:]

    if args.second == 'bot_line' or args.second == 'bot_angle':
        p2 = 'Agent'
        t2 = args.second[4:]
    elif args.second == 'human_line' or args.second == 'human_angle':
        p2 = 'Human'
        t2 = args.second[6:]
    elif args.second == 'botmc_line' or args.second == 'botmc_angle':
        p2 = 'AgentMC'
        t2 = args.second[6:]
    else:
        p2 = 'Rando'
        t2 = args.second[7:]

    #print(args.print)
    game = ColeGame(p1, t1, p2, t2, args.logfile, args.num, args.noprint)
    game.play_game()



if __name__ == "__main__":
    main()