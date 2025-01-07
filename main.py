# Welcome to Monster Herder!  Here are some directions:
# Your goal is to move the dog to herd the monsters through the door in the bottom left corner.
# Collect coins along the way for extra points!
# Each monster that goes through the gate is worth 3 points.
# Each coin collected is worth 1 point.
# Each monster that escapes through the right or left side of the window is a 1 point deduction.
# The monsters will scatter if you don't try to herd them.
# They'll move closer together and away from the robot when the robot is in motion.
# Have fun!

import pygame
import random
import math

class MonsterHerder:
    def __init__(self):
        self.window_width = 640
        self.window_height = 480
        self.monster_sf = 2
        self.n_coins = 3
        self.n_monsters = 3
        self.monster_speed = 0.5
        self.robot_speed = 2
        self.gate_width = 4
        self.com_dist_thresh = 50
        self.coins_caught = 0
        self.monsters_caught = 0
        self.monsters_lost = 0

        self.to_left = False
        self.to_right = False
        self.to_up = False
        self.to_down = False
    
        pygame.init()
        self.clock = pygame.time.Clock()
        self.game_font = pygame.font.SysFont("Arial", 24)

        self.load_images()
        self.new_game()

        self.window = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Monster Herder")

        self.main_loop()

    def load_images(self):
        self.robot = pygame.image.load("helmet_sprite_small.png")
        self.coin = pygame.image.load("coin.png")
        self.door = pygame.image.load("door.png")
        self.monster = pygame.image.load("monster.png")

    def new_game(self):
        self.monster_x = []
        self.monster_y = []
        self.coin_x = []
        self.coin_y = []
        monster_y_init = self.window_height//4 - self.monster.get_height()//2
        for ii in range(self.n_monsters):
            monster_x_init = random.randint(self.window_width//4,3*self.window_width//4)
            self.monster_x.append(monster_x_init)
            self.monster_y.append(monster_y_init)
        
        for ii in range(self.n_coins):
            coin_x_init = random.randint(self.window_width//4,3*self.window_width//4)
            coin_y_init = random.randint(self.window_height//4,self.window_height - self.robot.get_height() - 20)
            self.coin_x.append(coin_x_init)
            self.coin_y.append(coin_y_init)
        
        self.robot_x = (self.window_width - self.robot.get_width())//2
        self.robot_y = self.window_height - self.robot.get_height()
        self.door_loc = (10,self.window_height-self.door.get_height()-10)

    def main_loop(self):
        while True:
            self.check_events()
            self.calculate_positions()
            self.draw_window()
            self.clock.tick(60)

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.to_left = True
                if event.key == pygame.K_RIGHT:
                    self.to_right = True
                if event.key == pygame.K_UP:
                    self.to_up = True
                if event.key == pygame.K_DOWN:
                    self.to_down = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.to_left = False
                if event.key == pygame.K_RIGHT:
                    self.to_right = False
                if event.key == pygame.K_UP:
                    self.to_up = False
                if event.key == pygame.K_DOWN:
                    self.to_down = False

    def robot_positioning(self):
        if self.to_right and self.robot_x <= self.window_width + self.monster.get_width() + 10:
            self.robot_x += self.robot_speed
        if self.to_left and self.robot_x >= -self.monster.get_width() - self.robot.get_width() - 10:
            self.robot_x -= self.robot_speed
        if self.to_up and self.robot_y >= -self.robot.get_height() - self.monster.get_height() - 10:
            self.robot_y -= self.robot_speed
        if self.to_down and self.robot_y <= self.window_height + self.monster.get_height() + 10:
            self.robot_y += self.robot_speed

    def monster_positioning(self):

        if len(self.monster_x) > 0:
            monster_com_x = sum(self.monster_x)/len(self.monster_x)
            monster_com_y = sum(self.monster_y)/len(self.monster_y)
        exited_monsters = []

        # if the robot is moving, the monsters move closer to each other and away from the robot
        if self.to_right or self.to_left or self.to_up or self.to_down:
            for ii in range(len(self.monster_x)):
                movement_angle = random.random()*0.5*math.pi
                com_dist = ((self.monster_x[ii] - monster_com_x)**2 + (self.monster_y[ii] - monster_com_y)**2)**0.5

                # position changes to move closer to each other
                if self.monster_x[ii] > -self.monster.get_width() and self.monster_x[ii] < self.window_width:
                    if com_dist > self.com_dist_thresh:
                        if self.monster_x[ii] >= monster_com_x:
                            self.monster_x[ii] -= 0.25*self.monster_speed*math.cos(movement_angle)
                        else:
                            self.monster_x[ii] += 0.25*self.monster_speed*math.cos(movement_angle)
                    else:
                        self.monster_x[ii] += 0.25*random.randint(-2,2)
                else:
                    self.monsters_lost += 1
                    exited_monsters.append(ii)
                
                if self.monster_y[ii] > 0 and self.monster_y[ii] < (self.window_height - self.monster.get_height()):
                    if com_dist > self.com_dist_thresh:
                        if self.monster_y[ii] >= monster_com_y:
                            self.monster_y[ii] -= 0.25*self.monster_speed*math.sin(movement_angle)
                        else:
                            self.monster_y[ii] += 0.25*self.monster_speed*math.sin(movement_angle)
                    else:
                        self.monster_y[ii] += 0.25*random.randint(-2,2)

                # position changes to move away from the robot
                robot_dx = self.monster_x[ii] - self.robot_x
                robot_dy = self.monster_y[ii] - self.robot_y
                monster_robot_angle = math.atan2(robot_dy,robot_dx)
                monster_speed_factor = ((robot_dx**2 + robot_dy**2)/((self.window_width//4)**2 + (self.window_height//4)**2))**0.5
                if monster_speed_factor < 1:
                    monster_speed = self.monster_sf-monster_speed_factor*self.monster_sf
                    self.monster_y[ii] += monster_speed*math.sin(monster_robot_angle)
                    self.monster_x[ii] += monster_speed*math.cos(monster_robot_angle)

        # if the robot is stationary, the monsters scatter
        else:
            for ii in range(len(self.monster_x)):
                movement_angle = random.random()*0.5*math.pi

                if self.monster_x[ii] > -self.monster.get_width() and self.monster_x[ii] < self.window_width:
                    if self.monster_x[ii] >= monster_com_x:
                        self.monster_x[ii] += self.monster_speed*math.cos(movement_angle)
                    else:
                        self.monster_x[ii] -= self.monster_speed*math.cos(movement_angle)
                else:
                    self.monsters_lost += 1
                    exited_monsters.append(ii)
                
                if self.monster_y[ii] > 0 and self.monster_y[ii] < (self.window_height - self.monster.get_height()):
                    if self.monster_y[ii] >= monster_com_y:
                        self.monster_y[ii] += self.monster_speed*math.sin(movement_angle)
                    else:
                        self.monster_y[ii] -= self.monster_speed*math.sin(movement_angle)

        # check to see if monsters have gone through gate
        for ii in range(len(self.monster_x)):
            if self.monster_x[ii] > self.door_loc[0] and self.monster_x[ii] < self.door_loc[0] + (self.door.get_width()-16)*self.gate_width - self.monster.get_width():
                if self.monster_y[ii] > self.door_loc[1]:
                    exited_monsters.append(ii)
                    self.monsters_caught += 1
        
        for ii in sorted(exited_monsters, reverse=True):
            del self.monster_x[ii]
            del self.monster_y[ii]

    def coin_collecting(self):
        exited_coins = []
        for ii in range(len(self.coin_x)):
            if self.coin_x[ii] >= self.robot_x-self.coin.get_width() and self.coin_x[ii] <= self.robot_x+self.robot.get_width():
                if self.coin_y[ii] >= self.robot_y - self.coin.get_height() and self.coin_y[ii] < self.robot_y + self.robot.get_height():
                    self.coins_caught += 1
                    exited_coins.append(ii)

        for ii in sorted(exited_coins, reverse=True):
            del self.coin_x[ii]
            del self.coin_y[ii]

    def calculate_positions(self):

        self.robot_positioning()
        self.monster_positioning()
        self.coin_collecting()

    def draw_window(self):
        self.window.fill((128, 128, 128))

        for ii in range(self.gate_width):
            self.window.blit(self.door, (self.door_loc[0]+ (self.door.get_width()-16)*ii,self.door_loc[1]))

        for ii in range(len(self.monster_x)):
            self.window.blit(self.monster, (self.monster_x[ii],self.monster_y[ii]))
            
        for ii in range(len(self.coin_x)):
            self.window.blit(self.coin, (self.coin_x[ii],self.coin_y[ii]))

        text = self.game_font.render(f"Coins: {self.coins_caught}   Monsters Lost: {self.monsters_lost}   Monsters Caught: {self.monsters_caught}", True, (0, 0, 0))
        self.window.blit(text, (200, 15))

        if len(self.monster_x) == 0:
            final_score_text = self.game_font.render(f"FINAL SCORE: {self.coins_caught + 3*self.monsters_caught - self.monsters_lost}/{self.n_coins + 3*self.n_monsters}", True, (0, 0, 0))
            self.window.blit(final_score_text, (200,50))

        self.window.blit(self.robot, (self.robot_x,self.robot_y))
        pygame.display.flip()

if __name__ == "__main__":
    MonsterHerder()