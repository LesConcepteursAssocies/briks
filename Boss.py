# -*- coding: utf8 -*-
#
# Un casse-briques (hommage à Arkanoid)
#
# 01/2018 PG (pguillaumaud@april.org)
#
# Les boss de niveau
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
from pygame.color import *
import Config
import Tools
import Spritesheet

# --------------------------------------------------------------------------------
# utilisée par les objets générés par un boss
class BossStuff(object):
    # nouvelle position en fonction du bord touché du sprite donné
    def checkBorder(self, orect, nx, ny):
        x = nx
        y = ny
        # on cherche le bord touché
        (fromLeft, fromTop, fromRight, fromBottom) = self.findBorder(orect)
        if fromLeft:
            x          = float(orect.x - self.rect.width - 1)
            self.angle = - self.angle
        if fromRight:
            x          = float(orect.x + orect.width + 1)
            self.angle = - self.angle
        if fromTop:
            y          = float(orect.y - self.rect.height - 1)
            self.angle = math.pi - self.angle
        if fromBottom:
            y          = float(orect.y + orect.height + 1)
            self.angle = math.pi - self.angle
        return (x, y)

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
class Boss(pygame.sprite.Sprite):
    # sname (spritessheets,cols,rows): boss en mode normal
    # sname_hit (spritessheets,cols,rows): quand le boss est touché
    # sname_death (spritessheets,cols,rows): quand il est mort
    # bras_G (spritessheets,cols,rows): bras gauche (boss doh)
    # bras_D (spritessheets,cols,rows): bras droit (boss doh)
    def __init__(self, sname, sname_hit, sname_death, bras_G, bras_D):
        pygame.sprite.Sprite.__init__(self)
        self.setPos()
        self.sps_n   = Spritesheet.SpriteSheet(sname[0], sname[1], sname[2], (self.x, self.y), True)
        self.sps_h   = Spritesheet.SpriteSheet(sname_hit[0], sname_hit[1], sname_hit[2], (self.x, self.y), True)
        self.sps_d   = Spritesheet.SpriteSheet(sname_death[0], sname_death[1], sname_death[2], (self.x, self.y), True)
        self.sps_brL = None
        self.sps_brR = None
        self.brticks = pygame.time.get_ticks()
        # flag pour les bras, False: vers le bas, True: vers le haut
        self.brLUp   = True
        self.brRUp   = True
        if bras_G is not None:
            # on place les bras
            x            = self.x - (self.sps_n.rect.width - 44)
            y            = self.y + 27
            self.sps_brL = Spritesheet.SpriteSheet(bras_G[0], bras_G[1], bras_G[2], (x, y), True)
        if bras_D is not None:
            x            = self.x - (self.sps_n.rect.width - 44) + (self.sps_n.rect.width + 56)
            y            = self.y + 27
            self.sps_brR = Spritesheet.SpriteSheet(bras_D[0], bras_D[1], bras_D[2], (x, y), True)
        self.maxhits = 20
        self.hits    = self.maxhits
        self.npts    = 500
        # ticks max par image (en ms) pour l'animation, fonction du mode
        self.ticks_m = 250
        # timer du mode 'hit'
        self.time_h  = pygame.time.get_ticks()
        # les bombes larguées
        self.bombs   = []
        # les lasers (missiles)
        self.laser   = []
        # boss mort?
        self.isDead  = False
        # la gauge de vie
        self.gauge   = pygame.Surface([(Config.screenWidth - Config.bords.width) - 20, 20])
        self.gauge.fill(THECOLORS["black"])
        self.gauge_r = self.gauge.get_rect()
        # centrée dans la zone d'info
        self.gauge_r.x  = Config.bords.width + ((Config.screenWidth - Config.bords.width) // 2)
        self.gauge_r.x -= self.gauge_r.width // 2
        self.gauge_r.y  = 550
        # mode normal par défaut
        self.setNormalMode()

    # position du boss
    def setPos(self):
        # on place l'image du boss au centre
        # taille en briques: 3x8
        # la marge
        marge  = (Config.bords.rectT.w - (Config.maxbr * Config.brw)) // 2
        row    = (Config.maxli - 8) // 2
        col    = (Config.maxbr - 3) // 2
        self.x = (Config.bords.rectL.w + marge) + (col * Config.brw)
        self.y = (Config.bords.rectT.h + 5) + (row * Config.brh)

    # mode normal
    def setNormalMode(self):
        self.sps     = self.sps_n
        self.state   = "normal"
        self.ticks_m = 250
        self.ticks   = pygame.time.get_ticks()

    # mode hit (touché)
    def setHitMode(self):
        self.sps     = self.sps_h
        self.state   = "hit"
        self.ticks_m = 250
        self.time_h  = pygame.time.get_ticks()
        self.ticks   = pygame.time.get_ticks()

    # mode death (mort)
    def setDeathMode(self):
        self.sps     = self.sps_d
        self.state   = "death"
        self.sps.setImage(0, 0)
        self.ticks_m = 1000
        # tirs stoppés
        self.bombs   = []
        self.laser   = []
        self.ticks   = pygame.time.get_ticks()

    # lance (ou pas) une rafale de m missiles
    def launchMissiles(self, m):
        if random.randrange(1,11) in [ 1, 3, 6, 8 ]:
            # positionnés sous le boss, répartis sur la largeur
            x   = self.sps.rect.x
            y   = self.sps.rect.y + self.sps.rect.height + 1
            gap = (self.sps.rect.width // m)
            for i in range(m):
                missile = BossStuff()
                (missile.image, missile.rect) = Tools.load_png('missile-boss-01.png')
                missile.mask                  = pygame.mask.from_surface(missile.image)
                missile.x                     = x
                missile.y                     = y
                missile.rect.x                = missile.x
                missile.rect.y                = missile.y
                missile.speed                 = 5.0
                # le rayon
                missile.radius                = missile.rect.height // 2
                # vers le bas par défaut, au hasard
                missile.angle                 = math.radians(random.choice([-random.randrange(300, 330), random.randrange(300, 330)]))
                self.laser.append(missile)
                x                            += gap

    # lance une rafale de b bombes
    def launchBombes(self, b):
        # positionnés sous le boss, répartis sur la largeur
        x   = self.sps.rect.x
        y   = self.sps.rect.y + self.sps.rect.height + 1
        gap = (self.sps.rect.width // b)
        # position du joueur
        target = Tools.Vector2(Config.player.rect.centerx, Config.player.rect.centery)
        for i in range(b):
            bomb = BossStuff()
            (bomb.image, bomb.rect) = Tools.load_png(random.choice(['bombe-boss-01.png', 'bombe-boss-02.png']))
            bomb.mask               = pygame.mask.from_surface(bomb.image)
            # position du centre
            bomb.x                  = x + (bomb.rect.width // 2)
            bomb.y                  = y + (bomb.rect.height // 2)
            bomb.rect.centerx       = bomb.x
            bomb.rect.centery       = bomb.y
            bomb.speed              = 4.0
            # on vise le joueur
            position                = Tools.Vector2(bomb.x, bomb.y)
            bomb.dist               = target - position
            bomb.dir                = bomb.dist.normalize()
            self.bombs.append(bomb)
            x                      += gap

    # le boss attaque !!
    def attack(self):
        if self.state != "death":
            # rafale de missiles
            self.launchMissiles(4)
            # rafale de bombes
            self.launchBombes(3)

    def updateBras(self):
        if self.state != "death":
            brnd = random.randrange(1,11)
            # animation des bras, une image toutes les 200ms
            ct = pygame.time.get_ticks()
            if self.sps_brL is not None:
                if brnd in [ 1, 3, 5, 7 ]:
                    if (ct - self.brticks) > 200:
                        self.brticks = ct
                        if self.brLUp:
                            cc = self.sps_brL.cc + 1
                        else:
                            cc = self.sps_brL.cc - 1
                        cr = self.sps_brL.cr
                        if self.brLUp and cc >= (self.sps_brL.cols - 1):
                            cc         = self.sps_brL.cols - 1
                            # le bras redescent
                            self.brLUp = False
                        elif not self.brLUp and cc <= 0:
                            cc         = 0
                            # le bras monte
                            self.brLUp = True
                        self.sps_brL.setImage(cc, cr)
            if self.sps_brR is not None:
                if brnd in [ 2, 4, 6, 8 ]:
                    if (ct - self.brticks) > 200:
                        self.brticks = ct
                        if self.brRUp:
                            cc = self.sps_brR.cc + 1
                        else:
                            cc = self.sps_brR.cc - 1
                        cr = self.sps_brR.cr
                        if self.brRUp and cc >= (self.sps_brR.cols - 1):
                            cc         = self.sps_brR.cols - 1
                            # le bras redescent
                            self.brRUp = False
                        elif not self.brRUp and cc <= 0:
                            cc         = 0
                            # le bras monte
                            self.brRUp = True
                        self.sps_brR.setImage(cc, cr)

    def update(self):
        # animation, une image toutes les 200ms
        ct = pygame.time.get_ticks()
        if (ct - self.ticks) > self.ticks_m:
            self.ticks = ct
            cc = self.sps.cc + 1
            cr = self.sps.cr
            if cc >= (self.sps.cols - 1):
                if cr >= (self.sps.rows - 1):
                    cr  = 0
                    cc  = 0
                    # fin du cycle, boss mort?
                    if self.state == "death":
                        self.isDead = True
                else:
                    cr += 1
                    cc  = 0
            self.sps.setImage(cc, cr)
        # fin du hit?
        if self.state == "hit":
            # 1s par hit
            if (ct - self.time_h) > 1000:
                # on repasse en mode normal
                self.setNormalMode()
        # les bras
        self.updateBras()
        if self.state != "death":
            # les missiles
            for i in range(len(self.laser)):
                # déplacements
                newpos = Tools.Vector2(self.laser[i].x + math.sin(self.laser[i].angle) * self.laser[i].speed, self.laser[i].y + math.cos(self.laser[i].angle) * self.laser[i].speed)

                # vérif collisions
                # bord haut?
                if newpos.y <= Config.bords.rectT.h:
                    newpos.y            = float(Config.bords.rectT.h + 1)
                    self.laser[i].angle = math.pi - self.laser[i].angle
                # bord gauche?
                if newpos.x <= Config.bords.rectL.w:
                    newpos.x            = float(Config.bords.rectL.w + 1)
                    self.laser[i].angle = - self.laser[i].angle
                # bord droit?
                if newpos.x > Config.bords.rectR.x - self.laser[i].rect.width:
                    newpos.x            = float(Config.bords.rectR.x - self.laser[i].rect.width - 1)
                    self.laser[i].angle = - self.laser[i].angle
                # en bas?
                if newpos.y > Config.bords.height:
                    # le missile est détruit
                    self.laser.pop(i)
                    break

                # collision avec le joueur
                offset = (int(newpos.x - Config.player.rect.x), int(newpos.y - Config.player.rect.y))
                result = Config.player.mask.overlap(self.laser[i].mask, offset)
                if result:
                    (newpos.x, newpos.y) = self.laser[i].checkBorder(Config.player.rect, newpos.x, newpos.y)
                    break

                # collision avec les ennemis
                for e in range(len(Config.enemys)):
                    offset = (int(newpos.x - Config.enemys[e].rect.x), int(newpos.y - Config.enemys[e].rect.y))
                    result = Config.enemys[e].mask.overlap(self.laser[i].mask, offset)
                    if result:
                        (newpos.x, newpos.y) = self.laser[i].checkBorder(Config.enemys[e].rect, newpos.x, newpos.y)
                        break

                # nouvelle position
                self.laser[i].x      = newpos.x
                self.laser[i].y      = newpos.y
                self.laser[i].rect.x = self.laser[i].x
                self.laser[i].rect.y = self.laser[i].y
            # les bombes
            for i in range(len(self.bombs)):
                if self.bombs[i].dir:
                    # déplacements
                    newpos = Tools.Vector2(self.bombs[i].x + (self.bombs[i].dir[0] * self.bombs[i].speed), self.bombs[i].y + (self.bombs[i].dir[1] * self.bombs[i].speed))

                    # vérif collisions
                    # bord haut?
                    if newpos.y <= Config.bords.rectT.h:
                        newpos.y            = float(Config.bords.rectT.h + 1)
                    # bord gauche?
                    if newpos.x <= Config.bords.rectL.w:
                        newpos.x            = float(Config.bords.rectL.w + 1)
                    # bord droit?
                    if newpos.x > Config.bords.rectR.x - self.bombs[i].rect.width:
                        newpos.x            = float(Config.bords.rectR.x - self.bombs[i].rect.width - 1)
                    # en bas?
                    if newpos.y > Config.bords.height:
                        # la bombe est détruite
                        self.bombs.pop(i)
                        break

                    # collision avec le joueur
                    offset = (int(newpos.x - Config.player.rect.x), int(newpos.y - Config.player.rect.y))
                    result = Config.player.mask.overlap(self.bombs[i].mask, offset)
                    if result:
                        # la bombe est détruite
                        self.bombs.pop(i)
                        if not Config.godMode:
                            return True
                        break

                    # nouvelle position
                    self.bombs[i].x = newpos.x
                    self.bombs[i].y = newpos.y
                    self.bombs[i].rect.centerx = self.bombs[i].x
                    self.bombs[i].rect.centery = self.bombs[i].y
        return False

    def draw(self):
        self.sps.draw()
        # les bras
        if self.sps_brL is not None:
            self.sps_brL.draw()
        if self.sps_brR is not None:
            self.sps_brR.draw()
        # les missiles
        for i in range(len(self.laser)):
            Config.screen.blit(self.laser[i].image, self.laser[i].rect)
        # les bombes
        for i in range(len(self.bombs)):
            Config.screen.blit(self.bombs[i].image, self.bombs[i].rect)
        # la gauge
        pygame.draw.rect(Config.screen, THECOLORS["green"], self.gauge_r, 1)
        percent = self.hits / self.maxhits
        pygame.draw.rect(Config.screen, THECOLORS["red"], pygame.Rect(self.gauge_r.x + 2, self.gauge_r.y + 2, int(percent * (self.gauge_r.width - 4)), self.gauge_r.height - 4))

# --------------------------------------------------------------------------------
# le niveau courant est un niveau avec un boss
def doBossLevel():
    # on vide le niveau
    Config.bricks = []
    # le fond
    Tools.InitBG('bg-boss.png')
    brL = None
    brR = None
    if Config.level > 34:
        # le boss doh
        snormal = ('boss-doh.png', 3, 1)
        shit    = ('boss-doh-hit.png', 3, 1)
        sdeath  = ('boss-doh-death.png', 3, 1)
        brL     = ('boss-doh-bras-gauche.png', 6, 1)
        brR     = ('boss-doh-bras-droit.png', 6, 1)
    else:
        # le boss classique
        snormal = ('boss.png', 4, 1)
        shit    = ('boss-hit.png', 4, 1)
        sdeath  = ('boss-death.png', 4, 2)
    Config.boss = Boss(snormal, shit, sdeath, brL, brR)

# eof