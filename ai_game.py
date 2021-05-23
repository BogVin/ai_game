import pyxel
import random
from agent import Agent
from collections import namedtuple
import numpy as np
from helper import plot


class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Apple:
    def __init__(self, img_id, speed):
        self.pos = Position(10, 32)
        self.w = 8
        self.h = 8
        self.color_tr = 0
        self.img = img_id
        self.speed = speed

    def update(self, x, y):
        self.pos.x = x
        self.pos.y = y


class Man:
    def __init__(self, img_id):
        self.pos = Position(0, 0)
        self.w = 15
        self.h = 15
        self.img = img_id

    def update(self, x, y):
        self.pos.x = x
        self.pos.y = y


class App:
    def __init__(self):
        self.img_id0 = 0
        self.WINDOW_H = 128
        self.START_SPEED = 1
        self.APPLE_INTERVAL = 400
        self.HEALTH = 0
        self.POINTS = 0
        self.DIFFICULTY_COUNTER = 0
        pyxel.init(192, 128, scale=8, caption="CATCH", fps=120)
        pyxel.load("assets/resources.pyxres")
        self.man = Man(self.img_id0)
        self.man.pos.x = 17
        self.man.pos.y = 100
        self.apple = Apple(self.img_id0, self.START_SPEED)
        self.apple_w = self.apple.w
        self.apple_h = self.apple.h
        self.apples_list = []
        self.apple_x_pos = [20, 40, 60, 80, 100, 120, 140, 160]
        self.MAN_SPEED = 3
        self.agent = Agent(50, True)
        self.done = False
        self.reward = 0
        self.counter = 0
        self.plot_scores = []
        self.plot_mean_scores = []
        self.total_score = 0
        self.record = 0
        self.ai_reaction = 0
        pyxel.run(self.update, self.draw)

    def update(self):
        self.DIFFICULTY_COUNTER = self.DIFFICULTY_COUNTER + 1
        if self.DIFFICULTY_COUNTER == 400:
            self.update_difficulty()
            self.DIFFICULTY_COUNTER = 0
            self.counter = 0

        self.counter = self.counter + 1
        if self.counter == self.APPLE_INTERVAL:
            apple = Apple(self.img_id0, self.START_SPEED)
            apple.pos.x = random.choice(self.apple_x_pos)
            apple.pos.y = 8
            self.apples_list.append(apple)
            self.counter = 0
        if 0 < len(self.apples_list):
            for apple in self.apples_list:
                apple.update(apple.pos.x, apple.pos.y + apple.speed)
        self.ai_reaction += 1
         # get game status
        if self.ai_reaction == 1:
            game_status = self.apple_pos_distance()
            state_old = self.agent.get_state(game_status)
            self.reward = 0
            final_move = self.agent.get_action(state_old)
            self.move(final_move)
            for apple in self.apples_list:
                if apple.pos.x + int(self.apple_w / 2) in range(self.man.pos.x, self.man.pos.x + self.man.w):
                    self.reward = 5
                if apple.pos.y > 120:
                    self.apples_list.remove(apple)
                    self.HEALTH = self.HEALTH - 1
                    self.reward = - 10

                if self.check_position(apple.pos.x, apple.pos.y):
                    self.apples_list.remove(apple)
                    self.POINTS = self.POINTS + 1
                    self.reward = 10
            state_new = self.agent.get_state(game_status)
            # train short memory
            self.agent.train_short_memory(state_old, final_move, self.reward, state_new, self.done)
            # remember
            self.agent.remember(state_old, final_move, self.reward, state_new, self.done)
            self.ai_reaction = 0
        if self.HEALTH == -1:
            self.done = True

        if self.done:

            self.agent.n_games += 1
            self.agent.train_long_memory()

            if self.POINTS > self.record:
                self.record = self.POINTS
                self.agent.model.save()

            print('Game', self.agent.n_games, 'Score', self.POINTS, 'Record:', self.record)

            self.plot_scores.append(self.POINTS)
            self.total_score += self.POINTS
            mean_score = self.total_score / self.agent.n_games
            self.plot_mean_scores.append(mean_score)
            plot(self.plot_scores, self.plot_mean_scores)
            self.drop_game()

    def draw(self):
        pyxel.cls(0)
        if 0 < len(self.apples_list):
            for apple in self.apples_list:
                pyxel.blt(apple.pos.x, apple.pos.y, self.img_id0, 32, 8, apple.w, apple.h, 12)
        pyxel.blt(self.man.pos.x, self.man.pos.y, self.img_id0, 16, 0, self.man.w, self.man.h, 12)
        pyxel.text(8, 0, "Score %s" % self.POINTS, pyxel.frame_count % 16)
        pyxel.text(160, 0, "Life %s" % self.HEALTH, pyxel.frame_count % 16)

    def check_position(self, pos_x, pos_y):
        if pos_x + int(self.apple_w / 2) in range(self.man.pos.x, self.man.pos.x + self.man.w) and \
                int(pos_y + self.apple_h) in range(self.man.pos.y, self.man.pos.y + self.man.h):
            return True
        else:
            return False

    def move(self, action):
        if np.array_equal(action, [1, 0, 0, 0, 0, 0, 0, 0]):
            self.man.pos.x = 17
        if np.array_equal(action, [0, 1, 0, 0, 0, 0, 0, 0]):
            self.man.pos.x = 37
        if np.array_equal(action, [0, 0, 1, 0, 0, 0, 0, 0]):
            self.man.pos.x = 57
        if np.array_equal(action, [0, 0, 0, 1, 0, 0, 0, 0]):
            self.man.pos.x = 77
        if np.array_equal(action, [0, 0, 0, 0, 1, 0, 0, 0]):
            self.man.pos.x = 97
        if np.array_equal(action, [0, 0, 0, 0, 0, 1, 0, 0]):
            self.man.pos.x = 117
        if np.array_equal(action, [0, 0, 0, 0, 0, 0, 1, 0]):
            self.man.pos.x = 137
        if np.array_equal(action, [0, 0, 0, 0, 0, 0, 0, 1]):
            self.man.pos.x = 157

    def apple_pos_distance(self):
        range_list = [0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 0]
        for index, item in enumerate(self.apple_x_pos):
            for apple in self.apples_list:
                if apple.pos.x == item:
                    range_list[index] = apple.pos.x + int(apple.w / 2)
                    range_list[8 + index] = apple.pos.y + apple.h
        return range_list

    def can_move_right(self):
        if self.man.pos.x + 20 < 192:
            return True
        else:
            return False

    def can_move_left(self):
        if self.man.pos.x - 20 > 0:
            return True
        else:
            return False

    def drop_game(self):
        self.apples_list.clear()
        self.START_SPEED = 1
        self.APPLE_INTERVAL = 100
        self.HEALTH = 0
        self.POINTS = 0
        self.DIFFICULTY_COUNTER = 0
        self.done = False
        self.counter = 0
        self.man.pos.x = 17
        self.reward = 0
        self.record = 0
        self.counter = 0

    def update_difficulty(self):
        self.START_SPEED = self.START_SPEED + 0.1
        if self.START_SPEED >= 2:
            self.START_SPEED = 2
        self.APPLE_INTERVAL = self.APPLE_INTERVAL - 5
        self.MAN_SPEED = self.MAN_SPEED + 1
        if self.MAN_SPEED > 20:
            self.MAN_SPEED = 20
        if self.APPLE_INTERVAL < 20:
            self.APPLE_INTERVAL = 20


App()
