# -*- coding: utf8 -*-
#
# Un casse-briques (hommage à Arkanoid)
#
# 01/2018 PG (pguillaumaud@april.org)
#
# La balle
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
import Bonus

# --------------------------------------------------------------------------------
class Ball(pygame.sprite.Sprite):
    # sbb = sprite en mode MégaBall (black ball)
    def __init__(self, pos, speed, sname, sbb):
        super().__init__()
        # les sprites
        self.imgn, self.rectn = Tools.load_png(sname)
        self.imgm, self.rectm = Tools.load_png(sbb)
        # et les masques
        self.maskn = pygame.mask.from_surface(self.imgn)
        self.maskm = pygame.mask.from_surface(self.imgm)
        # flag mode MégaBall (black ball) ou pas
        self.isMega = False
        self.x      = 0.0
        self.y      = 0.0
        if pos is not None:
            (self.x, self.y) = pos
        self.rect   = None
        # mode normal par défaut
        self.setNormalBall()
        # on garde la vitesse initiale (pour le reset sur un bonus)
        self.init_s = speed
        self.speed  = speed
        self.angle  = 5/6*math.pi
        self.state  = "still"
        self.reset()

    # initialise la position de la balle
    # (sur la raquette, au milieu)
    def reset(self):
        self.state  = "still"
        self.x = float(Config.player.rect.midtop[0] - self.rect.width)
        self.y = float(Config.player.rect.midtop[1] - self.rect.height - 1)
        self.rect.centerx = self.x + self.rect.width
        self.rect.centery = self.y + self.radius
        # angle (vers le haut au hasard)
        self.angle  = math.radians(random.choice([random.randrange(30, 60), random.randrange(120, 150), -random.randrange(30, 60), -random.randrange(120, 150)]))

    # mode normal
    def setNormalBall(self):
        self.isMega = False
        if self.rect is not None:
            # on garde la position courante
            self.x = self.rect.x
            # verif débordement à droite
            if (self.x + self.rectn.width) > Config.bords.rectR.x:
                self.x = (Config.bords.rectR.x - self.rectn.width)
            self.y = self.rect.y
        else:
            # (sur la raquette, au milieu)
            self.x = float(Config.player.rect.midtop[0] - self.rectn.width)
            self.y = float(Config.player.rect.midtop[1] - self.rectn.height - 1)
        self.image  = self.imgn
        self.rect   = self.rectn
        self.mask   = self.maskn
        # le rayon
        self.radius = self.rect.width // 2
        self.rect.centerx = self.x + self.rect.width
        self.rect.centery = self.y + self.radius

    # mode MégaBall (black ball)
    def setMegaBall(self):
        self.isMega = True
        if self.rect is not None:
            # on garde la position courante
            self.x = self.rect.x
            # verif débordement à droite
            if (self.x + self.rectm.width) > Config.bords.rectR.x:
                self.x = (Config.bords.rectR.x - self.rectm.width)
            self.y = self.rect.y
        else:
            self.x = float(Config.player.rect.midtop[0] - self.rectm.width)
            self.y = float(Config.player.rect.midtop[1] - self.rectm.height - 1)
        self.image  = self.imgm
        self.rect   = self.rectm
        self.mask   = self.maskm
        # le rayon
        self.radius = self.rect.width // 2
        self.rect.centerx = self.x + self.rect.width
        self.rect.centery = self.y + self.radius

    # déplacements
    def move(self):
        self.newpos = Tools.Vector2(self.x + math.sin(self.angle) * self.speed, self.y + math.cos(self.angle) * self.speed)
        self.mvt    = Tools.Vector2(self.newpos.x - self.x, self.newpos.y - self.y)
        self.fixed  = False

    # collisions avec les bords
    def borderBounce(self):
        # à droite?
        if self.newpos.x > Config.bords.rectR.x - self.rect.width:
            self.newpos.x = float(Config.bords.rectR.x - self.rect.width - 1)
            self.angle    = - self.angle
        # à gauche?
        if self.newpos.x <= Config.bords.rectL.w:
            self.newpos.x = float(Config.bords.rectL.w + 1)
            self.angle    = - self.angle
        # en haut?
        if self.newpos.y <= Config.bords.rectT.h:
            self.newpos.y = float(Config.bords.rectT.h + 1)
            self.angle    = math.pi - self.angle
        # champs de force sous la raquette?
        if Config.bonus_actif['F']:
            offset = (int(self.newpos.x - Config.bonus_adds['F'].rect.x), int(self.newpos.y - Config.bonus_adds['F'].rect.y))
            result = Config.bonus_adds['F'].mask.overlap(self.mask, offset)
            if result:
                self.newpos.y = float(Config.bords.height - self.rect.height - Config.bonus_adds['F'].rect.height - 1)
                self.angle    = math.pi - self.angle
        # en bas?
        if self.newpos.y + self.rect.height > Config.bords.height:
            if Config.godMode:
                # god Mode on rebondit ...
                self.newpos.y = float(Config.bords.height - self.rect.height - 1)
                self.angle    = math.pi - self.angle
            else:
                # perdu
                return True
        return False

    # collisions avec le joueur
    def playerBounce(self):
        offset = (int(self.newpos.x - Config.player.rect.x), int(self.newpos.y - Config.player.rect.y))
        result = Config.player.mask.overlap(self.mask, offset)
        if result:
            self.checkBorder(Config.player.rect)
            if Config.player.stickyMode:
                # la balle colle à la raquette
                self.state  = "still"
                self.x = float(Config.player.rect.midtop[0] - self.rect.width)
                self.y = float(Config.player.rect.midtop[1] - self.rect.height - 1)
                self.rect.centerx = self.x + self.rect.width
                self.rect.centery = self.y + self.radius
                # angle (vers le haut au hasard)
                self.angle  = math.radians(random.choice([random.randrange(30, 60), random.randrange(120, 150), -random.randrange(30, 60), -random.randrange(120, 150)]))

    # collisions avec une brique
    def bricksBounce(self):
        for i in range(len(Config.bricks)):
            offset = (int(self.newpos.x - Config.bricks[i].rect.x), int(self.newpos.y - Config.bricks[i].rect.y))
            result = Config.bricks[i].mask.overlap(self.mask, offset)
            if result:
                if self.isMega:
                    # brique cassée
                    Config.score += Config.bricks[i].npts
                    # on garde la position pour le bonus (en bas au centre de la brique)
                    posb = (Config.bricks[i].rect.midbottom[0] - 22, Config.bricks[i].rect.midbottom[1])
                    Config.bricks.pop(i)
                    # un bonus?
                    Bonus.randomBonus(posb)
                else:
                    self.checkBorder(Config.bricks[i].rect)
                    if Config.bricks[i].hits > 0:
                        # on peut casser la brique
                        Config.bricks[i].hits -= 1
                        if Config.bricks[i].hits <= 0:
                            # brique cassée
                            Config.score += Config.bricks[i].npts
                            # on garde la position pour le bonus (en bas au centre de la brique)
                            posb = (Config.bricks[i].rect.midbottom[0] - 22, Config.bricks[i].rect.midbottom[1])
                            Config.bricks.pop(i)
                            # un bonus?
                            Bonus.randomBonus(posb)
                break

    # collision avec les ennemis
    def enemysBounce(self):
        for i in range(len(Config.enemys)):
            offset = (int(self.newpos.x - Config.enemys[i].rect.x), int(self.newpos.y - Config.enemys[i].rect.y))
            result = Config.enemys[i].mask.overlap(self.mask, offset)
            if result:
                self.checkBorder(Config.enemys[i].rect)
                # l'ennemi explose
                Config.enemys[i].state = "xplod"
                break

    # collision avec un boss
    def bossBounce(self):
        offset = (int(self.newpos.x - Config.boss.sps.rect.x), int(self.newpos.y - Config.boss.sps.rect.y))
        result = Config.boss.sps.mask.overlap(self.mask, offset)
        if result:
            self.checkBorder(Config.boss.sps.rect)
            if Config.boss.state != "death":
                Config.boss.setHitMode()
                if Config.boss.hits > 0:
                    Config.boss.hits -= 1
                    if Config.boss.hits <= 0:
                        # boss mort!!
                        Config.boss.setDeathMode()
                        # on fige la balle, pour profiter du spectacle
                        self.state = "still"
        if Config.boss.state != "death":
            # les bras?
            if Config.boss.sps_brL is not None:
                offset = (int(self.newpos.x - Config.boss.sps_brL.rect.x), int(self.newpos.y - Config.boss.sps_brL.rect.y))
                result = Config.boss.sps_brL.mask.overlap(self.mask, offset)
                if result:
                    self.checkBorder(Config.boss.sps_brL.rect)
            if Config.boss.sps_brR is not None:
                offset = (int(self.newpos.x - Config.boss.sps_brR.rect.x), int(self.newpos.y - Config.boss.sps_brR.rect.y))
                result = Config.boss.sps_brR.mask.overlap(self.mask, offset)
                if result:
                    self.checkBorder(Config.boss.sps_brR.rect)

    def update(self):
        self.move()
        perdu = self.borderBounce()
        if not perdu:
            self.playerBounce()
            if Config.bossLevel:
                self.bossBounce()
            else:
                self.bricksBounce()
            self.enemysBounce()
            self.x      = self.newpos.x
            self.y      = self.newpos.y
            self.rect.x = self.x
            self.rect.y = self.y
        return perdu

    def draw(self):
        Config.screen.blit(self.image, self.rect)

    # nouvelle position en fonction du bord touché du sprite donné
    def checkBorder(self, orect):
        # on cherche le bord touché
        (fromLeft, fromTop, fromRight, fromBottom) = self.findBorder(orect)
        if fromLeft:
            self.newpos.x = float(orect.x - self.rect.width - 1)
            self.angle    = - self.angle
        if fromRight:
            self.newpos.x = float(orect.x + orect.width + 1)
            self.angle    = - self.angle
        if fromTop:
            self.newpos.y = float(orect.y - self.rect.height - 1)
            self.angle    = math.pi - self.angle
        if fromBottom:
            self.newpos.y = float(orect.y + orect.height + 1)
            self.angle    = math.pi - self.angle

    # cherche le bord touché entre la balle et le sprite donné
    def findBorder(self, orect):
        isLeft     = orect.x - (self.rect.centerx + self.radius)
        isTop      = orect.y - (self.rect.centery + self.radius)
        isRight    = (self.rect.centerx - self.radius) - (orect.x + orect.width)
        isBottom   = (self.rect.centery - self.radius) - (orect.y + orect.height)
        plusPetit  =  max(isLeft, isTop, isRight, isBottom)
        fromLeft   = isLeft == plusPetit
        fromTop    = isTop == plusPetit
        fromRight  = isRight == plusPetit
        fromBottom = isBottom == plusPetit
        return (fromLeft, fromTop, fromRight, fromBottom)

# --------------------------------------------------------------------------------
# init de la première balle
def BallInit():
    Config.balls = []
    # La première balle
    Config.balls.append(Ball(None, 7.0, 'ball-01.png', 'ball-black.png'))

# --------------------------------------------------------------------------------
# gestion des balles
def Ballsreset():
    for i in range(len(Config.balls)):
        Config.balls[i].reset()

# --------------------------------------------------------------------------------
def Ballsmoving():
    for i in range(len(Config.balls)):
        Config.balls[i].state = "moving"

# --------------------------------------------------------------------------------
def Ballsdraw():
    for i in range(len(Config.balls)):
        Config.balls[i].draw()

# --------------------------------------------------------------------------------
def Ballsupdate():
    Config.Perdu = False
    perdu        = False
    for i in range(len(Config.balls)):
        if Config.balls[i].state == "moving":
            perdu = perdu or Config.balls[i].update()
            if perdu:
                # on supprime la balle
                Config.balls.pop(i)
                break
    if perdu and len(Config.balls) == 0:
        # on a perdu la dernière balle
        Config.Perdu = True

# eof
