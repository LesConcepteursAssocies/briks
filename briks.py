#!/usr/bin/env python3
# -*- coding: utf8 -*-
#
# Un casse-briques (hommage à Arkanoid)
#
# 01/2018 PG (pguillaumaud@april.org)
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
import os
import re
import random
import pygame
from pygame.locals import *
from pygame.color import *
import Config
import Tools
import Border
import Bonus
import Ball
import Player
import Level
import Enemys
import Boss

# --------------------------------------------------------------------------------
# gestion des événements
def event_handler():
    for event in pygame.event.get():
        if event.type == QUIT:
            Tools.OnExit()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                Tools.OnExit()
            if event.key == K_r:
                # RàZ du jeu
                Tools.GameInit()
            if event.key == K_SPACE:
                Config.Sounds['intro'].stop()
                Config.Sounds['intro-2'].play()
                # on lance les balles
                Ball.Ballsmoving()
                if Config.player.laserMode:
                    Config.player.laserFire()
            if event.key == K_LEFT:
                Config.player.moveLeft()
            if event.key == K_RIGHT:
                Config.player.moveRight()
            if (event.key == K_PLUS or event.key == K_KP_PLUS) and Config.godMode:
                # cheat code, on change de niveau
                Tools.NextLevel()
            if (event.key == K_MINUS or event.key == K_KP_MINUS) and Config.godMode:
                # cheat code, on change de niveau
                if Config.level > 1:
                    Config.level -= 1
                else:
                    # on boucle
                    Config.level = Config.maxlevel
                Level.LoadLevel(Config.level)
                if Config.bossLevel:
                    # niveau d'un boss
                    Boss.doBossLevel()
                else:
                    Tools.InitBG()
                Bonus.initBonus()
                Config.player.reset()
                Ball.Ballsreset()
        elif event.type == KEYUP:
            if event.key == K_LEFT or event.key == K_RIGHT:
                Config.player.state = "still"
        elif event.type == USEREVENT:
            # MàJ des fps toutes les secondes
            pygame.display.set_caption(Config.titre+' (fps: {0:.0f})'.format(Config.clock.get_fps()))
        elif event.type == (USEREVENT + 1):
            # génération d'ennemis (toutes les 10s)
            if not Config.Perdu and not Level.FinishedLevel():
                Enemys.randomGen()
        elif event.type == (USEREVENT + 2):
            # génération des bombes et missiles du boss (déclenché toutes les 5s)
            if Config.bossLevel:
                Config.boss.attack()

# --------------------------------------------------------------------------------
def main():
    # Initialisation de la fenêtre d'affichage
    pygame.init()
    Config.screen = pygame.display.set_mode((Config.screenWidth, Config.screenHeight), HWSURFACE | DOUBLEBUF)
    pygame.display.set_caption(Config.titre)

    # le son
    pygame.mixer.init(44100, -16, 2, 4096)

    # le logo d'hommage ^^
    Config.logo, Config.logo_r = Tools.load_png('logo.png')

    # les bords de la surface de jeu
    Config.bords = Border.Border()

    # le niveau
    Level.LoadLevel(Config.level)

    if Config.bossLevel:
        # niveau d'un boss
        Boss.doBossLevel()
    else:
        # le fond
        Tools.InitBG()

    Tools.ReadHighScore()

    # la zone d'info
    Config.zinfo = pygame.Surface([(Config.screenWidth - Config.bords.width), Config.screenHeight])
    Config.zinfo.fill(THECOLORS["black"])

    # Le joueur (la raquette)
    Config.player = Player.Bat('player-bat-02.png', 'player-bat-02-L.png', 'player-bat-02-S.png')

    # La première balle
    Ball.BallInit()

    # les ennemis
    Enemys.init()

    # les sons
    Tools.InitSounds()
    pygame.mixer.music.set_volume((Config.Volume/100))

    # Affichage
    Config.screen.blit(Config.bg, (0, 0))
    Config.bords.draw()
    Tools.MsgInfo()
    Level.DrawLevel()
    Config.player.draw()
    Ball.Ballsdraw()
    Enemys.draw()
    pygame.display.flip()

    # Initialisation de l'horloge
    Config.clock = pygame.time.Clock()

    # timer user pour la màj des fps (déclenché 1 fois/seconde)
    pygame.time.set_timer(USEREVENT, 1000)
    # timer pour la génération des ennemis (déclenché toutes les 10s)
    pygame.time.set_timer((USEREVENT + 1), 10000)
    # timer pour la génération des bombes et missiles du boss (déclenché toutes les 5s)
    pygame.time.set_timer((USEREVENT + 2), 5000)

    Config.Sounds['intro'].play()

    # Boucle d'évènements
    while True:
        event_handler()

        dt = Config.clock.tick(Config.FPS) / 1000

        Ball.Ballsupdate()

        if Config.Perdu:
            Config.life -= 1
            if Config.life > 0:
                Tools.MsgCenter("Oops...", 28, Config.zinfo.get_rect().centery, "cyan", True)
                pygame.display.flip()
                # petite tempo
                pygame.time.wait(1500)
                Config.Perdu = False
                Bonus.initBonus()
                Config.player.reset()
                Ball.BallInit()
            else:
                # perdu...
                Tools.GameOver()
        else:
            if Config.bossLevel:
                if Config.boss.update():
                    Config.life -= 1
                    if Config.life <= 0:
                        # perdu...
                        Tools.GameOver()
            Config.player.update()
            Bonus.update()
            Enemys.update()

        if Config.bossLevel:
            if Config.boss.isDead:
                # niveau suivant
                Tools.MsgCenter("!! Bravo !!", 28, Config.zinfo.get_rect().centery, "blue", True)
                pygame.display.flip()
                # petite tempo
                pygame.time.wait(5000)
                Tools.NextLevel()

        if Level.FinishedLevel():
            # niveau suivant
            Tools.MsgCenter("Level UP!", 28, Config.zinfo.get_rect().centery, "green", True)
            pygame.display.flip()
            # petite tempo
            pygame.time.wait(1500)
            Tools.NextLevel()

        # affichages
        Config.screen.blit(Config.bg, (0, 0))
        Config.bords.draw()
        Tools.MsgInfo()
        Level.DrawLevel()
        Config.player.draw()
        Ball.Ballsdraw()
        Bonus.draw()
        Bonus.drawAdds()
        Enemys.draw()
        pygame.display.flip()

# --------------------------------------------------------------------------------
if __name__ == '__main__':
    import argparse

    # les arguments éventuels
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-G', required=False, default=Config.godMode, action='store_true', help='Cheat code (god Mode)')
    parser.add_argument("-t", required=False, dest="testfile", action="store", help='level to test')
    parser.add_argument("-v", required=False, type=int, dest="volume", action="store", help='sound volume(0-100)')
    args = parser.parse_args()

    if args.volume is not None:
        Config.Volume = max(0,min(abs(int(arg.volume)),100))

    if args.testfile is not None:
        Config.testMode = True
        Config.testFile = args.testfile
        # on met à jour le niveau courant
        Config.level = int(re.findall(r'-(\d+)',Config.testFile)[0])
    elif args.G is not None:
        Config.godMode = args.G

    main()
# eof
