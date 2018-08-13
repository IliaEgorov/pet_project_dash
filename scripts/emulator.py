import random
import numpy as np
import scipy as sp
from joblib import Parallel, delayed
from multiprocessing import Pool


class Bananas:
    def __init__(self):
        self.settings = {}
        self.settings['gamename'] = 'bananas'
        self.settings['symbols_lines'] = \
            [[2, 5, 8, 11, 14],
             [1, 4, 7, 10, 13],
             [3, 6, 9, 12, 15],
             [1, 5, 9, 11, 13],
             [3, 5, 7, 11, 15],
             [2, 6, 9, 12, 14],
             [2, 4, 7, 10, 14],
             [3, 6, 8, 10, 13],
             [1, 4, 8, 12, 15]]

        self.settings['sc'] = 12
        self.settings['w'] = 11
        self.settings['lines_count'] = 1
        self.settings['freespins'] = 45

        #self.settings['p'] = [15, 15, 13, 13, 9, 9, 5, 4, 4, 4, 3, 3, 2]
        #1013|906|706|861|967|522|760|682|952|810|916|38|307
        self.settings['p'] = [1013, 906, 706, 861, 967, 522, 760, 682, 952, 810, 916, 38, 307]

        #self.settings['p'] = [14, 14, 12, 12, 10, 10, 8, 6, 6, 5, 3, 3, 0]

        self.sumSettings = sum(self.settings['p'])

        self.settings['c'] = [[0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,    0],
                              [2,   0,   0,   0,   0,   0,   0,   0,   0,   2,   2,   10,   2],
                              [5,   5,   5,   5,   10,  10,  15,  15,  20,  25,  25,  250,  5],
                              [25,  25,  25,  25,  50,  50,  75,  75,  100, 125, 125, 2500, 20],
                              [100, 100, 100, 100, 125, 125, 250, 250, 400, 750, 750, 9000, 500]]

        self.symb_count = len(self.settings['c'][0])

        self.bet = 1
        self.allbet = self.bet * self.settings['lines_count']
        self.symbols = []
        self.lines = []

        self.balance = 0
        self.score = []
        self.wincount = 0
        self.action = 'spin'
        self.freespins_left = 0

        self.sc1bar = 0


    def win_cost(self, sym, count):
        if count > 0:
            return self.bet * self.settings['c'][count-1][sym]
        return 0

    def create_symbols(self):
        self.symbols = []
        for i in range(5):
            self.symbols.extend(np.random.choice(self.symb_count, 3, p=[x / self.sumSettings for x in self.settings['p']], replace=False))

    def create_lines(self):
        self.lines = []
        for i in range(self.settings['lines_count']):
            self.lines.append([self.symbols[self.settings['symbols_lines'][i][j] - 1] for j in range(5)])


    def check_line(self, line_i):
        line = self.lines[line_i]

        comb_num = 0
        wild_num = 0
        win_coef = 1

        first = -1
        for i in line:
            if first == -1 and i != self.settings['w']:
                first = i
                break
        #print(line)

        # Количество символов подряд начиная с первого
        if first != -1 and first != self.settings['sc']:
            for s in line:
                if s == first or s == self.settings['w']:
                    comb_num += 1
                else:
                    break

        # Количество wild подряд начиная с первого
        for s in line:
            if s == self.settings['w']:
                wild_num += 1
            else:
                break

        if self.settings['w'] in line[:comb_num] and first != self.settings['w']:  # НАДО ДОДУМАТЬ!
            win_coef = 2

        line_win     = win_coef * self.win_cost(first,comb_num)
        count = comb_num
        #print('line_win = ',line_win)

        winWild = self.win_cost(self.settings['w'],wild_num)
        if winWild > line_win:
            line_win = winWild
            count = wild_num
        #print('wild_win = ',winWild)
        return line_win,count

    def check_lines(self):
        spin_win = 0

        for i in range(self.settings['lines_count']):
            win,count = self.check_line(i)
            spin_win += win

        countScatter = self.symbols.count(self.settings['sc'])

        scatter_win = self.settings['lines_count'] * self.win_cost(self.settings['sc'],countScatter)
        #spin_win += scatter_win

        if self.settings['sc'] in self.symbols[:3]:
            self.sc1bar += 1


        freegame = False
        if countScatter>2:
            freegame = True

        return spin_win,scatter_win,freegame

    def spin(self):
        self.create_symbols()
        self.create_lines()
        spin_win, scatter_win, freegame = self.check_lines()
        spin_result = {}
        spin_result['win'] = spin_win
        spin_result['freegame'] = freegame
        spin_result['scatter_win'] = scatter_win
        return spin_result

    def game(self,spins):
        state = 'main'
        freespins_left = 0
        game_win = 0
        spent = 0
        sc_win = 0
        freegame_number = 0

        for i in range(spins):
            if state == 'main':
                spent += self.allbet

            spin_result = self.spin()

            if spin_result['freegame']:
                state = 'freegame'
                freespins_left += self.settings['freespins']
                freegame_number +=1

            else:
                if state == 'freegame':
                    freespins_left -= 1
                    if freespins_left == 0:
                        state = 'main'

            sc_win   += spin_result['scatter_win']
            game_win += spin_result['win']

        print('freegamec = ',freegame_number)
        print('sc1bar = ',self.sc1bar)
        #print('scatter_win = ',sc_win)
        #print('win = ', game_win)
        return game_win,sc_win,spent

def emulate_game(spins):
    sp.random.seed()
    a = Bananas()
    b = a.game(spins)
    return b

# code     500K - 0.679, 0.66575, 0.6732
# emulator 500K - 0.6834, 0.6686, 0.6679
games_win = []
spins = 1000000
bet = 1
k = 4

#for i in range(k):
#    games_win.append(self.game(spins//k))

with Pool(k) as p:
    b = p.map(emulate_game, [spins//k]*k)

win_sum = 0
sc_win_sum = 0
all_spent = 0
for i in b:
    win_sum += i[0]
    sc_win_sum += i[1]
    all_spent += i[2]

print('spent = ', all_spent)
print ((win_sum + sc_win_sum)/all_spent)