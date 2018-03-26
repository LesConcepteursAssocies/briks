# -*- coding: utf8 -*-
#
# Un casse-briques (hommage à Arkanoid)
#
# 01/2018 PG (pguillaumaud@april.org)
#
# Les ennemis
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
import random
import math
import pygame
from pygame.locals import *
import Config
import Tools
import Spritesheet

# --------------------------------------------------------------------------------
# initialisations
def init():
    # on initialise les générateurs
    # on place le premier à gauche
    genL = Spritesheet.SpriteSheet('generator.png', 1, 6, (60, 0), False)
    # pour l'animation
    genL.state = "closed"
    genL.ticks = pygame.time.get_ticks()
    Config.generator.append(genL)
    # on place le second à droite
    genR = Spritesheet.SpriteSheet('generator.png', 1, 6, ((Config.bords.width - 60 - 88), 0), False)
    # pour l'animation
    genR.state = "closed"
    genR.ticks = pygame.time.get_ticks()
    Config.generator.append(genR)

# --------------------------------------------------------------------------------
# ouvre (ou pas) les générateurs
def randomGen():
    if len(Config.enemys) < Config.max_E:
        for i in range(len(Config.generator)):
            if random.random() > 0.5:
                # on ouvre le générateur
                Config.generator[i].state = "openning"
                Config.generator[i].ticks = pygame.time.get_ticks()

# --------------------------------------------------------------------------------
# mises à jour des divers éléments
def update():
    # les générateurs
    for i in range(len(Config.generator)):
        if Config.generator[i].state == "openning":
            # il s'ouvre
            # animation, une image toutes les 100ms
            ct = pygame.time.get_ticks()
            if (ct - Config.generator[i].ticks) > 100:
                Config.generator[i].ticks = ct
                if Config.generator[i].cr >= (Config.generator[i].rows - 1):
                    if len(Config.enemys) < Config.max_E:
                        # complètement ouvert, un ennemi arrive (centré en bas du générateur)
                        sname = random.choice(['enemy-01.png','enemy-02.png','enemy-03.png','enemy-04.png','enemy-05.png', 'enemy-06.png'])
                        enemy = Spritesheet.SpriteSheet(sname, 5, 5, (Config.generator[i].rect.midbottom[0] - 22, Config.generator[i].rect.midbottom[1]), True)
                        # on regarde si on peut le placer
                        dopl  = True
                        for b in range(len(Config.bricks)):
                            if Config.bricks[b].rect.y > enemy.rect.bottom:
                                # les briques restantes sont plus basses, on sort
                                break
                            offset = (int(enemy.x - Config.bricks[b].rect.x), int(enemy.y - Config.bricks[b].rect.y))
                            result = Config.bricks[b].mask.overlap(enemy.mask, offset)
                            if result:
                                # des briques gênent l'apparition
                                dopl = False
                                break
                        if dopl:
                            enemy.speed = 1.0
                            # vers le bas par défaut, au hasard
                            enemy.angle = math.radians(random.choice([random.randrange(300, 330), -random.randrange(300, 330)]))
                            enemy.ticks = pygame.time.get_ticks()
                            enemy.state = "moving"
                            # pour l'explosion si touché par une balle
                            enemy.xplod = None
                            # le score si touché par une balle
                            enemy.npts  = 50
                            Config.enemys.append(enemy)
                    # on referme le générateur
                    Config.generator[i].state = "closed"
                    Config.generator[i].setImage(0, 0)
                else:
                    Config.generator[i].setImage(Config.generator[i].cc, Config.generator[i].cr + 1)

    # les ennemis
    for i in range(len(Config.enemys)):
        if Config.enemys[i].state == "moving":
            # animation, une image toutes les 100ms
            ct = pygame.time.get_ticks()
            if (ct - Config.enemys[i].ticks) > 100:
                Config.enemys[i].ticks = ct
                cc = Config.enemys[i].cc + 1
                cr = Config.enemys[i].cr
                if cc >= (Config.enemys[i].cols - 1):
                    if cr >= (Config.enemys[i].rows - 1):
                        cr  = 0
                        cc  = 0
                    else:
                        cr += 1
                        cc  = 0
                Config.enemys[i].setImage(cc, cr)

            # déplacements
            newpos = Tools.Vector2(Config.enemys[i].x + math.sin(Config.enemys[i].angle) * Config.enemys[i].speed, Config.enemys[i].y + math.cos(Config.enemys[i].angle) * Config.enemys[i].speed)

            # vérif collisions
            # bord haut?
            if newpos.y <= Config.bords.rectT.h:
                newpos.y               = float(Config.bords.rectT.h + 1)
                Config.enemys[i].angle = math.pi - Config.enemys[i].angle
            # bord gauche?
            if newpos.x <= Config.bords.rectL.w:
                newpos.x               = float(Config.bords.rectL.w + 1)
                Config.enemys[i].angle = - Config.enemys[i].angle
            # bord droit?
            if newpos.x > Config.bords.rectR.x - Config.enemys[i].rect.width:
                newpos.x               = float(Config.bords.rectR.x - Config.enemys[i].rect.width - 1)
                Config.enemys[i].angle = - Config.enemys[i].angle
            # en bas?
            if newpos.y > Config.bords.height:
                # l'ennemi est détruit
                Config.enemys.pop(i)
                break

            if Config.bossLevel:
                # le boss?
                offset = (int(newpos.x - Config.boss.sps.rect.x), int(newpos.y - Config.boss.sps.rect.y))
                result = Config.boss.sps.mask.overlap(Config.enemys[i].mask, offset)
                if result:
                    (newpos.x, newpos.y, Config.enemys[i].angle) = checkBorder_E(Config.enemys[i], Config.boss.sps.rect, newpos.x, newpos.y)
                # les bras?
                if Config.boss.sps_brL is not None:
                    offset = (int(newpos.x - Config.boss.sps_brL.rect.x), int(newpos.y - Config.boss.sps_brL.rect.y))
                    result = Config.boss.sps_brL.mask.overlap(Config.enemys[i].mask, offset)
                    if result:
                        (newpos.x, newpos.y, Config.enemys[i].angle) = checkBorder_E(Config.enemys[i], Config.boss.sps_brL.rect, newpos.x, newpos.y)
                if Config.boss.sps_brR is not None:
                    offset = (int(newpos.x - Config.boss.sps_brR.rect.x), int(newpos.y - Config.boss.sps_brR.rect.y))
                    result = Config.boss.sps_brR.mask.overlap(Config.enemys[i].mask, offset)
                    if result:
                        (newpos.x, newpos.y, Config.enemys[i].angle) = checkBorder_E(Config.enemys[i], Config.boss.sps_brR.rect, newpos.x, newpos.y)
            else:
                # une brique?
                for b in range(len(Config.bricks)):
                    offset = (int(newpos.x - Config.bricks[b].rect.x), int(newpos.y - Config.bricks[b].rect.y))
                    result = Config.bricks[b].mask.overlap(Config.enemys[i].mask, offset)
                    if result:
                        (newpos.x, newpos.y, Config.enemys[i].angle) = checkBorder_E(Config.enemys[i], Config.bricks[b].rect, newpos.x, newpos.y)
                        break

            # nouvelle position
            Config.enemys[i].x      = newpos.x
            Config.enemys[i].y      = newpos.y
            Config.enemys[i].rect.x = Config.enemys[i].x
            Config.enemys[i].rect.y = Config.enemys[i].y

        elif Config.enemys[i].state == "xplod":
            # touché par une balle, l'ennemi explose
            if Config.enemys[i].xplod is None:
                # premier passage, on charge la page de sprites
                Config.enemys[i].xplod = Spritesheet.SpriteSheet('explosion.png', 12, 1, (Config.enemys[i].rect.centerx, Config.enemys[i].rect.centery), True)
                Config.enemys[i].ticks = pygame.time.get_ticks()

            # animation, une image toutes les 100ms
            ct = pygame.time.get_ticks()
            if (ct - Config.enemys[i].ticks) > 100:
                Config.enemys[i].ticks = ct
                if Config.enemys[i].xplod.cc >= (Config.enemys[i].xplod.cols - 1):
                    # explosion terminée, l'ennemi disparait
                    Config.score += Config.enemys[i].npts
                    Config.enemys.pop(i)
                    break
                else:
                    Config.enemys[i].xplod.setImage(Config.enemys[i].xplod.cc + 1, Config.enemys[i].xplod.cr)

# --------------------------------------------------------------------------------
# cherche le bord touché entre l'enemy et le sprite donné
def findBorder_E(e, orect):
    radius     = e.rect.width // 2
    isLeft     = orect.x - (e.rect.centerx + radius)
    isTop      = orect.y - (e.rect.centery + radius)
    isRight    = (e.rect.centerx - radius) - (orect.x + orect.width)
    isBottom   = (e.rect.centery - radius) - (orect.y + orect.height)
    plusPetit  =  max(isLeft, isTop, isRight, isBottom)
    fromLeft   = isLeft == plusPetit
    fromTop    = isTop == plusPetit
    fromRight  = isRight == plusPetit
    fromBottom = isBottom == plusPetit
    return (fromLeft, fromTop, fromRight, fromBottom)

# --------------------------------------------------------------------------------
# nouvelle position en fonction du bord touché du sprite donné
def checkBorder_E(e, orect, nx, ny):
    x     = nx
    y     = ny
    angle = e.angle
    # on cherche le bord touché
    (fromLeft, fromTop, fromRight, fromBottom) = findBorder_E(e, orect)
    if fromLeft:
        x     = float(orect.x - e.rect.width - 1)
        angle = - angle
    if fromRight:
        x     = float(orect.x + orect.width + 1)
        angle = - angle
    if fromTop:
        y     = float(orect.y - e.rect.height - 1)
        angle = math.pi - angle
    if fromBottom:
        y     = float(orect.y + orect.height + 1)
        angle = math.pi - angle
    return (x, y, angle)

# --------------------------------------------------------------------------------
# affichages
def draw():
    # les générateurs
    for g in Config.generator:
        g.draw()

    # les ennemis
    for e in Config.enemys:
        if e.state == "moving":
            e.draw()
        elif e.state == "xplod":
            e.xplod.draw()

# eof