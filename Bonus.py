# -*- coding: utf8 -*-
#
# Un casse-briques (hommage à Arkanoid)
#
# 01/2018 PG (pguillaumaud@april.org)
#
# Les divers bonus (pastilles, etc.)
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
import re
import random
import math
import pygame
from pygame.locals import *
import Config
import Tools
import Spritesheet
import Ball

# --------------------------------------------------------------------------------
# liste des bonus (pastilles):
#
# 'B': portail vers le niveau suivant
# 'C': la balle colle à la raquette
# 'D': 3 balles de plus
# 'E': raquette plus grande
# 'F': champs de force sous la raquette
# 'L': lasers sur la raquette
# 'M': les balles deviennent noires et détruisent toutes les briques sans rebondir dessus
# 'P': une vie en plus
# 'R': raquette plus petite
# 'S': les balles ralentissent
# 'T': on a 2 raquettes légèrement espacées
# 'V': la vitesse des balles augmente
# 'X': un bonus au hasard
#

# --------------------------------------------------------------------------------
# génère (ou pas) un bonus (pastille) à la position donnée
# appelé à la destruction d'une brique
def randomBonus(pos):
    if random.randrange(1,11) in [ 3, 6, 9 ]:
        sname    = random.choice(['pastille-D.png','pastille-B.png','pastille-P.png','pastille-S.png','pastille-C.png', 'pastille-E.png', 'pastille-L.png', 'pastille-V.png', 'pastille-T.png', 'pastille-M.png', 'pastille-X.png', 'pastille-R.png', 'pastille-F.png'])
        # la lettre de la pastille
        ptype    = re.findall(r'-([A-Z]{1})',sname)[0]
        pastille = Spritesheet.SpriteSheet(sname, 8, 1, pos, True)
        pastille.ticks = pygame.time.get_ticks()
        # vitesse entre 3 et 5
        pastille.speed = random.choice([3, 4, 5])
        bonus          = [ptype, pastille]
        Config.bonus.append(bonus)

# --------------------------------------------------------------------------------
# génère le bonus donné
def makeBonus(btype):
    if btype == 'B':
        # portail vers le niveau suivant
        Config.bonus_actif[btype] = True
        Config.bonus_timer[btype] = pygame.time.get_ticks()
        if Config.bonus_adds[btype] == None:
            # premier passage, on créé le sprite (placé à droite)
            sgate                    = Spritesheet.SpriteSheet('portail-next-level.png', 7, 1, (Config.bords.rectR.x, Config.bords.height - 88), True)
            Config.bonus_adds[btype] = sgate
        Config.bonus_adds[btype].setImage(0, 0)
        Config.bonus_adds[btype].state = "openning"
        Config.bonus_adds[btype].ticks = pygame.time.get_ticks()
    elif btype == 'C':
        # la balle colle à la raquette
        Config.bonus_actif[btype] = True
        Config.bonus_timer[btype] = pygame.time.get_ticks()
        Config.player.setStickyMode(True)
    elif btype == 'D':
        # 3 balles de plus
        for i in range(3):
            ball = Ball.Ball(None, 7.0, random.choice(['ball-02.png','ball-03.png','ball-04.png','ball-05.png']), 'ball-black.png')
            # on place la balle à la position de la balle actuelle
            ball.x = float(Config.balls[0].x - ball.rect.width)
            ball.y = float(Config.balls[0].y - ball.rect.height - 1)
            ball.rect.centerx = ball.x + ball.rect.width
            ball.rect.centery = ball.y + ball.radius
            ball.state        = "moving"
            Config.balls.append(ball)
    elif btype == 'E':
        # raquette plus grande
        Config.bonus_actif[btype] = True
        Config.bonus_timer[btype] = pygame.time.get_ticks()
        Config.player.setLargeSize()
    elif btype == 'F':
        # champs de force sous la raquette
        Config.bonus_actif[btype] = True
        Config.bonus_timer[btype] = pygame.time.get_ticks()
        if Config.bonus_adds[btype] == None:
            # premier passage, on créé le sprite
            ffield                   = Spritesheet.SpriteSheet('champs-de-force.png', 1, 2, (Config.bords.rectL.x + Config.bords.rectL.w, Config.bords.height - 17), True)
            Config.bonus_adds[btype] = ffield
        Config.bonus_adds[btype].ticks = pygame.time.get_ticks()
    elif btype == 'L':
        # lasers sur la raquette
        Config.bonus_actif[btype] = True
        Config.bonus_timer[btype] = pygame.time.get_ticks()
        Config.player.setLaserMode(True)
    elif btype == 'M':
        # les balles deviennent noires et détruisent toutes les briques
        # sans rebondir dessus
        Config.bonus_actif[btype] = True
        Config.bonus_timer[btype] = pygame.time.get_ticks()
        for i in range(len(Config.balls)):
            Config.balls[i].setMegaBall()
    elif btype == 'P':
        # une vie en plus
        Config.life += 1
    elif btype == 'R':
        # raquette plus petite
        Config.bonus_actif[btype] = True
        Config.bonus_timer[btype] = pygame.time.get_ticks()
        Config.player.setSmallSize()
    elif btype == 'S':
        # les balles ralentissent
        for i in range(len(Config.balls)):
            Config.balls[i].speed /= 2.0
        Config.bonus_actif[btype] = True
        Config.bonus_timer[btype] = pygame.time.get_ticks()
    elif btype == 'T':
        if not Config.player.dualMode:
            # on a 2 raquettes légèrement espacées
            Config.bonus_actif[btype] = True
            Config.bonus_timer[btype] = pygame.time.get_ticks()
            Config.player.setDualMode(True)
    elif btype == 'V':
        # la vitesse des balles augmente
        for i in range(len(Config.balls)):
            Config.balls[i].speed += 1.0
        Config.bonus_actif[btype] = True
        Config.bonus_timer[btype] = pygame.time.get_ticks()

# --------------------------------------------------------------------------------
# mise à jour des bonus
def update():
    for b in range(len(Config.bonus)):
        # animation, une image toutes les 50ms
        ct = pygame.time.get_ticks()
        if (ct - Config.bonus[b][1].ticks) > 50:
            Config.bonus[b][1].ticks = ct
            if Config.bonus[b][1].cc >= (Config.bonus[b][1].cols - 1):
                Config.bonus[b][1].setImage(0, 0)
            else:
                Config.bonus[b][1].setImage(Config.bonus[b][1].cc + 1, Config.bonus[b][1].cr)

        # déplacement (vers le bas)
        newy = Config.bonus[b][1].y + Config.bonus[b][1].speed

        # en bas?
        if newy > Config.bords.height:
            # on supprime le bonus
            Config.bonus.pop(b)
            break

        # collision avec le joueur?
        offset = (int(Config.bonus[b][1].x - Config.player.rect.x), int(newy - Config.player.rect.y))
        result = Config.player.mask.overlap(Config.bonus[b][1].mask, offset)
        if result:
            # on applique le bonus
            if Config.bonus[b][0] == 'X':
                # un bonus au hasard
                makeBonus(random.choice(['D', 'B', 'P', 'S', 'C', 'E', 'V', 'L', 'T', 'M', 'R', 'F']))
            else:
                makeBonus(Config.bonus[b][0])
            # 1000 pts de score en plus du bonus
            Config.score += 1000
            # on supprime le bonus
            Config.bonus.pop(b)
            break

        Config.bonus[b][1].y      = newy
        Config.bonus[b][1].rect.y = newy

    # mise à jour des bonus actifs
    for b in Config.bonus_actif:
        if Config.bonus_actif[b]:
            ct = pygame.time.get_ticks()
            if ((ct - Config.bonus_timer[b]) // 1000) >= Config.bonus_tmax[b]:
                if b == 'B':
                    if Config.bonus_adds[b].state == "wait":
                        # le portail est ouvert, fin du bonus
                        Config.bonus_actif[b] = False
                else:
                    # fin du bonus
                    Config.bonus_actif[b] = False
                    if b == 'C':
                        Config.player.setStickyMode(False)
                        Ball.Ballsmoving()
                    elif b in ['S', 'V']:
                        # on remet la vitesse de base
                        for i in range(len(Config.balls)):
                            Config.balls[i].speed = Config.balls[i].init_s
                    elif b in ['E', 'R']:
                        # on remet la taille normale
                        Config.player.setNormalSize()
                    elif b == 'L':
                        Config.player.setLaserMode(False)
                    elif b == 'M':
                        # on remet les balles en mode normal
                        for i in range(len(Config.balls)):
                            Config.balls[i].setNormalBall()
                    elif b == 'T':
                        Config.player.setDualMode(False)
            else:
                # on met à jour les éventuels objets des bonus actifs
                if b == 'B':
                    if Config.bonus_adds[b].state == "openning":
                        # le portail s'ouvre
                        # animation, une image toutes les 100ms
                        if (ct - Config.bonus_adds[b].ticks) > 100:
                            Config.bonus_adds[b].ticks = ct
                            if Config.bonus_adds[b].cc >= (Config.bonus_adds[b].cols - 1):
                                # portail ouvert, on déclenche le timer
                                Config.bonus_adds[b].state = "wait"
                                Config.bonus_timer[b]      = pygame.time.get_ticks()
                            else:
                                Config.bonus_adds[b].setImage(Config.bonus_adds[b].cc + 1, Config.bonus_adds[b].cr)
                elif b == 'F':
                    # animation, une image toutes les 50ms
                    if (ct - Config.bonus_adds[b].ticks) > 50:
                        Config.bonus_adds[b].ticks = ct
                        if Config.bonus_adds[b].cr >= (Config.bonus_adds[b].rows - 1):
                            Config.bonus_adds[b].setImage(0, 0)
                        else:
                            Config.bonus_adds[b].setImage(Config.bonus_adds[b].cc, Config.bonus_adds[b].cr + 1)
                elif b == 'L':
                    # les lasers
                    for l in range(len(Config.bonus_adds[b])):
                        # déplacement (vers le haut)
                        newy = Config.bonus_adds[b][l][1].y - 4
                        # en haut?
                        if newy <= Config.bords.rectT.h:
                            # on supprime le missile
                            Config.bonus_adds[b].pop(l)
                            break
                        ldel = False
                        # collision avec une brique?
                        for i in range(len(Config.bricks)):
                            offset = (int(Config.bonus_adds[b][l][1].x - Config.bricks[i].rect.x), int(newy - Config.bricks[i].rect.y))
                            result = Config.bricks[i].mask.overlap(Config.bonus_adds[b][l][2], offset)
                            if result:
                                # brique cassée
                                Config.score += Config.bricks[i].npts
                                # on garde la position pour le bonus (en bas au centre de la brique)
                                posb = (Config.bricks[i].rect.midbottom[0] - 22, Config.bricks[i].rect.midbottom[1])
                                Config.bricks.pop(i)
                                # un bonus?
                                randomBonus(posb)
                                ldel = True
                                break
                        if ldel:
                            # on a touché une brique, on supprime le missile
                            Config.bonus_adds[b].pop(l)
                            break
                        Config.bonus_adds[b][l][1].y = newy

# --------------------------------------------------------------------------------
# affichages
def draw():
    for b in Config.bonus:
        b[1].draw()

# --------------------------------------------------------------------------------
# affichage des objets générés
def drawAdds():
    for b in Config.bonus_actif:
        if Config.bonus_actif[b]:
            if b == 'B':
                # le portail
                Config.bonus_adds[b].draw()
            elif b == 'F':
                # le champs de force
                Config.bonus_adds[b].draw()
            elif b == 'L':
                # les lasers
                for l in range(len(Config.bonus_adds[b])):
                    Config.screen.blit(Config.bonus_adds[b][l][0], Config.bonus_adds[b][l][1])

# --------------------------------------------------------------------------------
# reset des bonus
def initBonus():
    Config.bonus           = []
    Config.bonus_adds['L'] = []
    for b in Config.bonus_actif:
        Config.bonus_actif[b] = False

# eof
