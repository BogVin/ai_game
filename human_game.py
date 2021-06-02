import pyxel
import random
from agent import Agent
import numpy as np


class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Apple:
    def __init__(self, img_id, speed):
        self.pos = Position(10, 32)
        self.w = 8
        self.h = 8
        self.img = img_id
        self.speed = speed

    def update(self, x, y):
        self.pos.x = x
        self.pos.y = y
    
     def draw_position(self, pos_x, pos_y):
        self.draw_x = pos_x
        self.draw_y = pos_y


class Man:
    def __init__(self, img_id):
        self.pos = Position(0, 0)
        self.w = 15
        self.h = 15
        self.img = img_id

    def update(self, x, y):
        self.pos.x = x
        self.pos.y = y

    def draw_position(self, pos_x, pos_y):
        self.draw_x = pos_x
        self.draw_y = pos_y


class App:
    def __init__(self):
        self.img_id0 = 0
        self.WINDOW_H = 128
        self.START_SPEED = 0.3
        self.APPLE_INTERVAL = 200
        self.HEALTH = 3
        self.POINTS = 0
        self.DIFFICULTY_COUNTER = 0
        pyxel.init(192, 128, scale=8, caption="CATCH", fps=120)
        pyxel.load("assets/resources.pyxres")
        self.man = Man(self.img_id0)
        self.man.pos.x = 17
        self.man.pos.y = 100
        self.man.draw_x = 0
        self.man.draw_y = 0
        self.apple = Apple(self.img_id0, self.START_SPEED)
        self.apple_w = self.apple.w
        self.apple_h = self.apple.h
        self.apples_list = []
        self.apple_x_pos = [20, 40, 60, 80, 100, 120, 140, 160]
        self.MAN_SPEED = 3
        self.player_name = 'PLAYER'
        self.name_entered = False
        self.menu_pass = False
        self.show_leader_board = False
        self.difficulty = "EASY"
        self.difficulty_list = ["EASY", "MEDIUM", "HARD"]
        self.square_pos = 20
        self.game_over = False
        self.counter = 0
        self.difficulty_check = False
        self.agent = Agent(0, False)
        self.ai_is_play = False
        self.play_music = True
        self.apple_draw_x = [32, 40]
        self.apple_draw_y = [0, 8]
        if self.play_music:
            pyxel.playm(1)
        pyxel.run(self.update, self.draw)

    def update(self):
        if not self.name_entered:
            self.name_enter()
        elif not self.menu_pass:
            self.menu()
        elif self.show_leader_board:
            self.leader_board()
        elif self.game_over:
            self.game_over_logic()
        else:
            self.game_logic()

    def draw(self):
        if not self.name_entered:
            pyxel.cls(0)
            self.draw_player_name()
        elif not self.menu_pass:
            pyxel.cls(0)
            self.draw_menu()
        elif self.show_leader_board:
            pyxel.cls(0)
            self.draw_leader_board()
        elif self.game_over:
            self.draw_game_over()
        else:
            self.draw_game()

    def check_position(self, pos_x, pos_y):
        if pos_x + int(self.apple_w / 2) in range(self.man.pos.x, self.man.pos.x + self.man.w) and \
                int(pos_y + self.apple_h) in range(self.man.pos.y, self.man.pos.y + int(self.man.h / 2)):
            return True
        else:
            return False

    def game_logic(self):
        if not self.difficulty_check:
            self.set_difficulty()
            self.difficulty_check = True
        self.DIFFICULTY_COUNTER = self.DIFFICULTY_COUNTER + 1
        if self.DIFFICULTY_COUNTER == 1500:
            self.START_SPEED = self.START_SPEED + 0.1
            self.APPLE_INTERVAL = self.APPLE_INTERVAL - 5
            self.MAN_SPEED = self.MAN_SPEED + 1
            if self.MAN_SPEED > 20:
                self.MAN_SPEED = 20
            if self.APPLE_INTERVAL < 20:
                self.APPLE_INTERVAL = 20
            self.DIFFICULTY_COUNTER = 0
            self.counter = 0

        if self.HEALTH == -1:
            self.save_to_board()
            self.game_over = True

        self.counter = self.counter + 1

        if self.counter == self.APPLE_INTERVAL:
            apple = Apple(self.img_id0, self.START_SPEED)
            apple.pos.x = random.choice(self.apple_x_pos)
            apple.pos.y = 8
            apple.draw_x = random.choice(self.apple_draw_x)
            apple.draw_y = random.choice(self.apple_draw_y)
            self.apples_list.append(apple)
            self.counter = 0

        if pyxel.btnp(pyxel.KEY_TAB):
            self.ai_is_play = not self.ai_is_play

        if self.ai_is_play:
            self.ai_play()
        else:
            if pyxel.btn(pyxel.KEY_A) and self.man.pos.x - 20 > 0:
                self.man.draw_x = 48
                self.man.update(self.man.pos.x - self.MAN_SPEED, self.man.pos.y)
            if pyxel.btn(pyxel.KEY_D) and self.man.pos.x + 20 < 170:
                self.man.draw_x = 16
                self.man.update(self.man.pos.x + self.MAN_SPEED, self.man.pos.y)
            elif 0 < len(self.apples_list):
                for apple in self.apples_list:
                    if apple.pos.x + int(apple.w / 2) in range(self.man.pos.x, self.man.pos.x + self.man.w) and \
                            self.man.pos.y - apple.pos.y < 20:
                        self.man.draw_x = 64
                    else:
                        self.man.draw_x = 0

        if 0 < len(self.apples_list):
            for apple in self.apples_list:
                apple.update(apple.pos.x, apple.pos.y + apple.speed)
                if apple.pos.y > 120:
                    self.apples_list.remove(apple)
                    self.HEALTH = self.HEALTH - 1
                    pyxel.play(3, 0)
                elif self.check_position(apple.pos.x, apple.pos.y):
                    self.apples_list.remove(apple)
                    self.POINTS = self.POINTS + 1
                    pyxel.play(2, 0)

    def draw_game(self):
        pyxel.cls(12)
        pyxel.blt(0, 0, self.img_id0, 0, 48, 250, 150, 12)
        if 0 < len(self.apples_list):
            for apple in self.apples_list:
                pyxel.blt(apple.pos.x, apple.pos.y, self.img_id0, apple.draw_x, apple.draw_y, apple.w, apple.h, 12)
        pyxel.blt(self.man.pos.x, self.man.pos.y, self.img_id0, self.man.draw_x, self.man.draw_y, self.man.w,
                  self.man.h, 12)

        pyxel.text(8, 0, "Score %s" % self.POINTS, pyxel.frame_count % 16)
        pyxel.text(160, 0, "Life %s" % self.HEALTH, pyxel.frame_count % 16)

    def name_enter(self):
        if pyxel.btnp(pyxel.KEY_A):
            self.player_name += "A"
        if pyxel.btnp(pyxel.KEY_B):
            self.player_name += "B"
        if pyxel.btnp(pyxel.KEY_C):
            self.player_name += "C"
        if pyxel.btnp(pyxel.KEY_D):
            self.player_name += "D"
        if pyxel.btnp(pyxel.KEY_E):
            self.player_name += "E"
        if pyxel.btnp(pyxel.KEY_F):
            self.player_name += "F"
        if pyxel.btnp(pyxel.KEY_G):
            self.player_name += "G"
        if pyxel.btnp(pyxel.KEY_H):
            self.player_name += "H"
        if pyxel.btnp(pyxel.KEY_I):
            self.player_name += "I"
        if pyxel.btnp(pyxel.KEY_J):
            self.player_name += "J"
        if pyxel.btnp(pyxel.KEY_K):
            self.player_name += "K"
        if pyxel.btnp(pyxel.KEY_L):
            self.player_name += "L"
        if pyxel.btnp(pyxel.KEY_M):
            self.player_name += "M"
        if pyxel.btnp(pyxel.KEY_N):
            self.player_name += "N"
        if pyxel.btnp(pyxel.KEY_O):
            self.player_name += "O"
        if pyxel.btnp(pyxel.KEY_P):
            self.player_name += "P"
        if pyxel.btnp(pyxel.KEY_Q):
            self.player_name += "Q"
        if pyxel.btnp(pyxel.KEY_R):
            self.player_name += "R"
        if pyxel.btnp(pyxel.KEY_S):
            self.player_name += "S"
        if pyxel.btnp(pyxel.KEY_T):
            self.player_name += "T"
        if pyxel.btnp(pyxel.KEY_U):
            self.player_name += "U"
        if pyxel.btnp(pyxel.KEY_V):
            self.player_name += "V"
        if pyxel.btnp(pyxel.KEY_W):
            self.player_name += "W"
        if pyxel.btnp(pyxel.KEY_X):
            self.player_name += "X"
        if pyxel.btnp(pyxel.KEY_Y):
            self.player_name += "Y"
        if pyxel.btnp(pyxel.KEY_Z):
            self.player_name += "Z"

        if pyxel.btnp(pyxel.KEY_BACKSPACE):
            self.player_name = self.player_name[0:-1]
        if pyxel.btnp(pyxel.KEY_ENTER):
            self.name_entered = True

    def draw_player_name(self):
        pyxel.text(40, 50, "ENTER NAME: %s" % self.player_name, 7)

    def menu(self):
        if pyxel.btnp(pyxel.KEY_DOWN) and self.square_pos != 60:
            self.square_pos += 20
        if pyxel.btnp(pyxel.KEY_UP) and self.square_pos != 20:
            self.square_pos -= 20
        if pyxel.btnp(pyxel.KEY_RIGHT) and self.difficulty == "EASY" and self.square_pos == 60:
            self.difficulty = "MEDIUM"
        elif pyxel.btnp(pyxel.KEY_RIGHT) and self.difficulty == "MEDIUM" and self.square_pos == 60:
            self.difficulty = "HARD"
        if pyxel.btnp(pyxel.KEY_LEFT) and self.difficulty == "HARD" and self.square_pos == 60:
            self.difficulty = "MEDIUM"
        elif pyxel.btnp(pyxel.KEY_LEFT) and self.difficulty == "MEDIUM" and self.square_pos == 60:
            self.difficulty = "EASY"
        if pyxel.btnp(pyxel.KEY_ENTER) and self.square_pos == 20:
            self.menu_pass = True
        elif pyxel.btnp(pyxel.KEY_ENTER) and self.square_pos == 40:
            self.show_leader_board = True
            self.menu_pass = True

    def leader_board(self):
        if self.show_leader_board and pyxel.btnp(pyxel.KEY_SPACE):
            self.show_leader_board = False
            self.menu_pass = False

    def draw_menu(self):
        pyxel.rectb(20, self.square_pos, 80, 20, pyxel.frame_count % 2)
        pyxel.text(25, 22, "START", 7)
        pyxel.text(25, 42, "LEADER BOARD", 7)
        pyxel.text(25, 62, "DIFFICULTY %s" % self.difficulty, 7)

    def save_to_board(self):
        with open("leader_board.txt", 'a') as f:
            f.write(self.player_name + " " + str(self.POINTS) + '\n')

    def get_leader_board(self):
        result_dict = {}
        with open("leader_board.txt", 'r') as f:
            for line in f:
                n_s = line.split()
                result_dict[n_s[0]] = n_s[1]

        return result_dict

    def draw_leader_board(self):
        dict_r = self.get_leader_board()
        dict_p = sorted(dict_r.items(), key=lambda x: x[1], reverse=True)
        draw_pos_counter = 0
        pyxel.text(55, 0, "LEADER BOARD", pyxel.frame_count % 16)
        for key in dict_p:
            draw_pos_counter += 10
            pyxel.text(30, draw_pos_counter, "%s" % key[0], 7)
            pyxel.text(90, draw_pos_counter, "%s" % key[1], 7)

    def game_over_logic(self):
        if pyxel.btnp(pyxel.KEY_R):
            self.drop_game()

    def draw_game_over(self):
        pyxel.cls(0)
        pyxel.text(int(pyxel.width / 2) - 22, int(pyxel.height / 2 - 30), "GAME OVER", pyxel.frame_count % 16)
        pyxel.text(int(pyxel.width / 2) - 22, int(pyxel.height / 2 ), "SCORE %s" % self.POINTS, pyxel.frame_count % 16)
        pyxel.text(int(pyxel.width / 2) - 30, int(pyxel.height / 2 + 20), "PRESS R TO MENU", pyxel.frame_count % 2)

    def drop_game(self):
        self.apples_list.clear()
        self.START_SPEED = 1
        self.APPLE_INTERVAL = 100
        self.HEALTH = 3
        self.POINTS = 0
        self.DIFFICULTY_COUNTER = 0
        self.counter = 0
        self.man.pos.x = 17
        self.counter = 0
        self.game_over = False
        self.name_entered = True
        self.menu_pass = False
        self.difficulty_check = False
        self.MAN_SPEED = 3


    def set_difficulty(self):
        if self.difficulty == "EASY":
            self.APPLE_INTERVAL = 300
            self.START_SPEED = 0.3
        elif self.difficulty == "MEDIUM":
            self.APPLE_INTERVAL = 200
            self.START_SPEED = 0.5
        else:
            self.APPLE_INTERVAL = 100
            self.START_SPEED = 1
            self.MAN_SPEED = 8

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

    def ai_play(self):
        game_status = self.apple_pos_distance()
        state = self.agent.get_state(game_status)
        final_move = self.agent.get_action(state)
        self.move(final_move)


App()
