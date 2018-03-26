# -*- coding: utf8 -*-
#
# Un casse-briques (hommage à Arkanoid)
#
# 01/2018 PG (pguillaumaud@april.org)
#
# Les fonctions diverses
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA
#
import sys, os
import random
import pickle
import math
import pygame
from pygame.locals import *
from pygame.color import *
import Config
import Ball
import Level
import Bonus
import Boss

# --------------------------------------------------------------------------------
# Fin du programme
def OnExit():
    if not Config.testMode:
        SaveHighScore()
    pygame.quit()
    sys.exit()

# --------------------------------------------------------------------------------
# initialisation du fond
def InitBG(bgname=None):
    if bgname == None:
        Config.bg, Config.bg_r = load_png(random.choice(['bg-01.png','bg-02.png','bg-03.png','bg-04.png','bg-05.png','bg-06.png']))
    else:
        Config.bg, Config.bg_r = load_png(bgname)
    # on met à l'échelle le fond si besoin
    if (Config.bg_r.width, Config.bg_r.height) != (Config.bords.width, Config.bords.height):
        Config.bg = pygame.transform.scale(Config.bg, (Config.bords.width, Config.bords.height))

# --------------------------------------------------------------------------------
# initialisation des sons
def InitSounds():
    Config.Sounds['intro'] = pygame.mixer.Sound(os.path.join(Config.path_app, 'sounds', 'ArkanoidMainTheme.ogg'))
    Config.Sounds['intro'].set_volume((Config.Volume/100))
    Config.Sounds['bat']   = pygame.mixer.Sound(os.path.join(Config.path_app, 'sounds', 'ping1.ogg'))
    Config.Sounds['intro'].set_volume((Config.Volume/100))

# --------------------------------------------------------------------------------
# Init/Reset du jeu
def GameInit():
    Config.Perdu = False
    Config.life  = Config.maxlife
    Config.score = 0
    Config.level = 1
    Config.bossLevel= False

    Bonus.initBonus()
    Config.player.reset()
    Ball.BallInit()
    Level.LoadLevel(Config.level)

# --------------------------------------------------------------------------------
# On passe au niveau suivant
def NextLevel():
    if not Config.testMode:
        Config.level += 1
        if Config.level > Config.maxlevel:
            # on boucle
            Config.level = 1
    Level.LoadLevel(Config.level)
    if Config.bossLevel:
        # niveau d'un boss
        Boss.doBossLevel()
    else:
        InitBG()
    Bonus.initBonus()
    Config.player.reset()
    Ball.BallInit()

# --------------------------------------------------------------------------------
# game over
def GameOver():
    # perdu...
    MsgCenter("Game Over!", 28, Config.zinfo.get_rect().centery, "yellow", True)
    pygame.display.flip()
    # on attend une touche
    inLoop = True
    while inLoop:
        for event in pygame.event.get():
            if event.type == QUIT:
                OnExit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    OnExit()
                if event.key == K_r:
                    # RàZ du jeu
                    GameInit()
                    inLoop = False
                    break

# --------------------------------------------------------------------------------
# Sauvegarde du highscore
def SaveHighScore():
    if Config.score > Config.highScore:
        filename = os.path.join(Config.path_app, '', Config.name_app+'-highscore.bin')
        try:
            with open(filename,'wb') as fh:
                pickle.dump(Config.score, fh)
        except:
            pass

# --------------------------------------------------------------------------------
# Récupération du highscore
def ReadHighScore():
    filename = os.path.join(Config.path_app, '', Config.name_app+'-highscore.bin')
    try:
        with open(filename,'rb') as fh:
            Config.highScore = pickle.load(fh)
    except:
        pass

# --------------------------------------------------------------------------------
# charge une image
def load_png(name):
    filename = os.path.join(Config.path_app, 'data', name)
    try:
        image = pygame.image.load(filename)
        if image.get_alpha is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
    except pygame.error as message:
        print("Impossible de charger l'image: {0}".format(filename))
        raise SystemExit(message)
    return image, image.get_rect()

# --------------------------------------------------------------------------------
# affiche le message donné à la position donnée dans la zone d'info
def Msg(txt, sz, x, y, color, afont):
    if sz <= 0:
        if afont:
            # fonte arkanoid
            font = pygame.font.Font(os.path.join(Config.path_app, 'data', 'arkanoid.ttf'), 24)
        else:
            font = pygame.font.Font(None, 24)
    else:
        if afont:
            # fonte arkanoid
            font = pygame.font.Font(os.path.join(Config.path_app, 'data', 'arkanoid.ttf'), sz)
        else:
            font = pygame.font.Font(None, sz)

    text = font.render(txt, True, THECOLORS[color])
    textpos = text.get_rect()
    textpos.x = x
    textpos.y = y
    Config.screen.blit(text, textpos)

# --------------------------------------------------------------------------------
# affiche le message donné centré en x dans la zone d'info
def MsgCenter(txt, sz, y, color, afont):
    if sz <= 0:
        if afont:
            # fonte arkanoid
            font = pygame.font.Font(os.path.join(Config.path_app, 'data', 'arka_solid.ttf'), 24)
        else:
            font = pygame.font.Font(None, 24)
    else:
        if afont:
            # fonte arkanoid
            font = pygame.font.Font(os.path.join(Config.path_app, 'data', 'arka_solid.ttf'), sz)
        else:
            font = pygame.font.Font(None, sz)

    text = font.render(txt, True, THECOLORS[color])
    textpos = text.get_rect()
    textpos.x  = Config.bords.width + ((Config.screenWidth - Config.bords.width) // 2)
    textpos.x -= textpos.width // 2
    textpos.y  = y
    Config.screen.blit(text, textpos)

# --------------------------------------------------------------------------------
# affiche les infos du jeu
def MsgInfo():
    Config.screen.blit(Config.zinfo, (Config.bords.width, 0))
    # le titre
    MsgCenter("Briks!", 60, 0, "red", True)

    # le logo
    Config.screen.blit(Config.logo, (Config.bords.width, 70))

    # le niveau courant
    cy = 200
    MsgCenter("Niveau", 32, cy, "red", False)
    cy += 25
    MsgCenter("{0:03d}".format(Config.level), 32, cy, "white", False)

    # la vie courante
    cy = 270
    MsgCenter("Vie", 32, cy, "red", False)
    cy += 25
    MsgCenter("{0:03d}".format(Config.life), 32, cy, "white", False)

    # le score
    cy = 630
    MsgCenter("Score", 32, cy, "red", False)
    cy += 25
    MsgCenter("{0:09d}".format(Config.score), 32, cy, "white", False)

    # le highScore
    cy = 700
    MsgCenter("highScore", 32, cy, "red", False)
    cy += 25
    MsgCenter("{0:09d}".format(Config.highScore), 32, cy, "white", False)

    if Config.testMode:
        cy = Config.screenHeight - 45
        MsgCenter("-testMode-", 32, cy, "green", False)
    elif Config.godMode:
        cy = Config.screenHeight - 45
        MsgCenter("*godMode*", 32, cy, "yellow", False)

    # les touches diverses
    cy = Config.screenHeight - 15
    MsgCenter("SPC: launch - R: reset - ESC: quit", 18, cy, "white", False)

# --------------------------------------------------------------------------------
# petite classe vecteur
# (inspiré de https://gist.github.com/remram44/2760022)
class Vector2(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __getitem__(self, key):
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        else:
            raise IndexError("This "+str(key)+" key is not a vector key!")

    # subtraction
    def __sub__(self, o):
        return Vector2(self.x - o.x, self.y - o.y)

    # get length (used for normalize)
    def length(self):
        return math.sqrt((self.x**2 + self.y**2))

    # divides a vector by its length
    def normalize(self):
        l = self.length()
        if l != 0:
            return (self.x / l, self.y / l)
        return None

# eof
