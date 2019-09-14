import numpy as np


class PuyoPuyo(object):
    def __init__(self, width=6, height=10):
        self.width = width
        self.height = height
        self.colors = 4
        self.observation_space = ((self.height + 1, self.width), (2,), (2,))
        self.action_space = self.width * 4 - 2
        self.field = np.zeros(self.observation_space[0], dtype=np.uint8)
        self.next_puyo = self.__get_next_puyo()
        self.next_next_puyo = self.__get_next_puyo()
        self.score = 0
        self.done = False
        actions = [(i, j)for i in range(
            self.width) for j in range(4)]
        actions.pop(3)
        actions.pop(-3)
        self.actions = actions

    def __get_next_puyo(self):
        return np.random.randint(1, self.colors + 1, size=2)

    def legal_actions(self):
        legal = np.zeros(len(self.actions), dtype=np.bool)
        puttable = self.field[0] == 0
        for i in range(self.action_space):
            col, rotate = self.actions[i]
            if col < 2:
                if not np.all(puttable[col:2]):
                    continue
            elif 2 < col:
                if not np.all(puttable[3:col+1]):
                    continue
            if rotate == 0 or rotate == 2:
                if self.field[:, col][1] == 0:
                    legal[i] = True
            elif rotate == 1:
                if puttable[col] and puttable[col+1]:
                    legal[i] = True
            elif rotate == 3:
                if puttable[col] and puttable[col-1]:
                    legal[i] = True

        return np.where(legal)[0]

    def reset(self):
        self.field = np.zeros(self.observation_space[0], dtype=np.uint8)
        self.next_puyo = self.__get_next_puyo()
        self.next_next_puyo = self.__get_next_puyo()
        self.score = 0
        self.done = False
        return self.field, self.next_puyo, self.next_next_puyo

    def step(self, action):
        self.put(action)
        chain, point = self.chain()
        self.score += point
        if not self.field[1][2] == 0:
            self.done = True
        self.next_puyo = self.next_next_puyo
        self.next_next_puyo = self.__get_next_puyo()
        info = None
        return (self.field, self.next_puyo,
                self.next_next_puyo), chain, self.done, info

    def drop(self, col, puyopuyo):
        i = np.argmax(np.where(self.field[:, col] == 0))

        if isinstance(puyopuyo, np.int64):
            puyopuyo = [puyopuyo]
        for puyo in puyopuyo:
            self.field[:, col][i] = puyo
            i -= 1

    def put(self, action):
        col, rotate = self.actions[action]
        if rotate == 0:
            self.drop(col, self.next_puyo)
        elif rotate == 2:
            self.drop(col, self.next_puyo[::-1])
        elif rotate == 1:
            self.drop(col, self.next_puyo[0])
            self.drop(col + 1, self.next_puyo[1])
        elif rotate == 3:
            self.drop(col, self.next_puyo[0])
            self.drop(col - 1, self.next_puyo[1])

    def erase(self):
        return False, 0

    def chain(self):
        success, got_point = self.erase()
        chain = 0
        point = 0
        while success:
            chain += 1
            point += got_point * chain
            success, got_point = self.erase()

        return chain, point

    def render(self):
        for row in self.field:
            for puyo in row:
                if puyo == 0:
                    print('\x1b[0m\u00b7', end="")
                else:
                    print(self.int2puyo(puyo), end="")
                print(' ', end="")
            print('\x1b[0m')

    @staticmethod
    def int2puyo(n):
        return f"\x1b[3{n}m\u25cf"
