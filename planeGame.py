# coding=utf-8

import os, sys
import pygame
from pygame.locals import *
from gameobj import *
import random

if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

#SCREEN_WIDTH = 480
#SCREEN_HEIGHT = 700

#初始化游戏
pygame.init()#initializes modules
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT)) #create a graphical window, set size
pygame.display.set_caption('飞机大作战') #set title of window

#载入背景图片
background_img = pygame.image.load('data\\img\\background.png')
background_img_rect = background_img.get_rect()

#载入游戏结束图片
game_over_img = pygame.image.load('data\\img\\gameover.png')
game_over_img_rect = game_over_img.get_rect()

#载入shoot图片（包含各飞机、子弹。。。图片）
shoot = pygame.image.load('data\\img\\shoot.png')

#载入游戏音效
bullet_sound = pygame.mixer.Sound('data\\audio\\bullet.wav')
enemy1_down_sound = pygame.mixer.Sound('data\\audio\\enemy1_down.wav')
enemy2_down_sound = pygame.mixer.Sound('data\\audio\\enemy2_down.wav')
enemy3_down_sound = pygame.mixer.Sound('data\\audio\\enemy3_down.wav')
game_music_sound = pygame.mixer.music.load('data\\audio\\game_music.wav')
game_over_sound = pygame.mixer.Sound('data\\audio\\game_over.wav')

bullet_sound.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0)
pygame.mixer.music.set_volume(0.2)

#各种玩家飞机在shoot图片上的位置的列表(有多种玩家飞机)
hero_rects = []
hero_rects.append(pygame.Rect(0, 99, 102, 126)) #hero1
hero_rects.append(pygame.Rect(165, 360, 102, 126)) #hreo2
#玩家爆炸图片
hero_rects.append(pygame.Rect(165, 234, 102, 126)) #hero_blowup_n1
hero_rects.append(pygame.Rect(330, 624, 102, 126)) #hero_blowup_n2
hero_rects.append(pygame.Rect(330, 498, 102, 126)) #hero_blowup_n3
hero_rects.append(pygame.Rect(432, 624, 102, 126)) #hero_blowup_n4

hero_pos = [189, 500] #设置玩家的初始位置
hero = Hero(shoot, hero_rects, hero_pos) #生成一个Hero对象

#子弹图片(暂时只有一种子弹)
bullet_rect = pygame.Rect(1004, 987, 9, 21)
bullet_img = shoot.subsurface(bullet_rect)

#敌机图片(暂时只有一种敌机)
enemy1_rect = pygame.Rect(534, 612, 57, 43)
enemy1_img = shoot.subsurface(enemy1_rect)

#敌机爆炸图片列表(多种爆炸效果)
enemy1_down_imgs = []
enemy1_down_imgs.append(shoot.subsurface(pygame.Rect(267, 347, 57, 51))) #enemy1_down1
enemy1_down_imgs.append(shoot.subsurface(pygame.Rect(873, 697, 57, 51))) #enemy1_down2
enemy1_down_imgs.append(shoot.subsurface(pygame.Rect(267, 296, 57, 51))) #enemy1_down3
enemy1_down_imgs.append(shoot.subsurface(pygame.Rect(930, 697, 57, 51))) #enemy1_down4

#敌机组
enemies1 = pygame.sprite.Group()

#敌机死亡组
enemies_down = pygame.sprite.Group()

shot_frequency = 0 #子弹发射频率
enemy_frequency = 0 #敌机出现频率

hero_down_index = 2 #用于索引玩家爆炸图片

score = 0 #分数

running = True
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()

	#控制游戏最大帧率
	pygame.time.Clock().tick(60)

	#发射子弹
	if not hero.is_hit:
		if shot_frequency % 15 == 0:
			bullet_sound.play() #播放音效
			hero.shoot(bullet_img) #发射
		shot_frequency += 1
		if shot_frequency >= 15:
			shot_frequency = 0
	
	#生成敌机
	if enemy_frequency % 50 == 0:
		enemy1_pos = [random.randint(0, SCREEN_WIDTH - enemy1_rect.width),0] #敌机位置
		enemy1 = Enemy(enemy1_img, enemy1_down_imgs, enemy1_pos)
		enemies1.add(enemy1) #加入到敌机组
	enemy_frequency += 1
	if enemy_frequency > 50:
		enemy_frequency = 0

	#移动子弹
	for bullet in hero.bullets:
		bullet.move()
		if bullet.rect.top < 0:
			hero.bullets.remove(bullet)
	
	#移动敌机
	for enemy1 in enemies1:
		enemy1.move()

		#判断玩家是否与敌机相撞
		if pygame.sprite.collide_circle(enemy1, hero):
			enemies_down.add(enemy1) #加入敌机死亡组
			enemies1.remove(enemy1) #从敌机组中移除
			hero.is_hit = True
			game_over_sound.play()
			pygame.mixer.music.stop()
			running = False
			break
		if enemy1.rect.top > SCREEN_HEIGHT:
			enemies1.remove(enemy1)

	#将被子弹击中的敌机加入敌机死亡组
	collisions = pygame.sprite.groupcollide(enemies1, hero.bullets, 1, 1)
	for enemy_down in collisions:
		enemies_down.add(enemy_down)
		score += 99


	#绘制背景
	screen.fill(0)
	screen.blit(background_img,background_img_rect)
	
	#绘制玩家飞机
	if not hero.is_hit:
		screen.blit(hero.image[hero.img_index], hero.rect)
		hero.img_index += 1
		if hero.img_index >=2 :
			hero.img_index = 0


	#绘制子弹和敌机
	hero.bullets.draw(screen)
	enemies1.draw(screen)

	#绘制得分
	score_font = pygame.font.Font('data\\font\\CHILLER.TTF', 36)
	score_text = score_font.render(str(score), True, (240, 0, 87)) #获得一个surface
	score_text_rect = score_text.get_rect()
	screen.blit(score_text,score_text_rect)
	
	#更新屏幕
	pygame.display.update()

	key_pressed = pygame.key.get_pressed()
	if not hero.is_hit:
		if key_pressed[K_UP] or key_pressed[K_w]:
			hero.moveUp()
		if key_pressed[K_DOWN] or key_pressed[K_s]:
			hero.moveDown()
		if key_pressed[K_LEFT] or key_pressed[K_a]:
			hero.moveLeft()
		if key_pressed[K_RIGHT] or key_pressed[K_d]:
			hero.moveRight()

screen.blit(game_over_img, game_over_img_rect)
pygame.display.update()
while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()
   
