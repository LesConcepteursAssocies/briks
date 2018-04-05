# -*- coding: utf8 -*-
#
# Un casse-briques (hommage à Arkanoid)
#
# 01/2018 PG (pguillaumaud@april.org)
#
# Le joueur (la raquette ...)
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
import math
import pygame
from pygame.locals import *
import Config
import Tools

# --------------------------------------------------------------------------------
class Bat(pygame.sprite.Sprite):
    # on donne 3 sprites: normal, petite et grande taille
    def __init__(self, sname, sname_large, sname_small):
        pygame.sprite.Sprite.__init__(self)
        # les sprites
        self.imgn, self.rectn = Tools.load_png(sname)
        self.imgl, self.rectl = Tools.load_png(sname_large)
        self.imgs, self.rects = Tools.load_png(sname_small)
        # et les masques
        self.maskn = pygame.mask.from_surface(self.imgn)
        self.maskl = pygame.mask.from_surface(self.imgl)
        self.masks = pygame.mask.from_surface(self.imgs)
        # lasers actifs ou pas
        self.laserMode = False
        # balles collantes ou pas
        self.stickyMode = False
        # double raquette ou pas
        self.dualMode   = False
        # paramètres de la seconde raquette
        self.dmpos      = (0, 0)
        self.dmrect     = None
        self.dmimg      = None
        self.dmmask     = None
        # positions des lasers (centre)
        self.laserL     = (0, 0)
        self.laserR     = (0, 0)
        self.laserColor = (0, 255, 255)
        self.rect       = None
        self.speed      = 10
        self.state      = "still"
        # les flags des tailles
        self.isNormalSz = True
        self.isLargeSz  = False
        self.isSmallSz  = False
        self.reset()

    def reset(self):
        # image normale par défaut
        self.setNormalSize()
        self.setDualMode(False)
        self.setLaserMode(False)
        self.setStickyMode(False)
        self.speed = 10
        self.state = "still"
        # au milieu en bas de la zone de jeu, on laisse une ligne vide sous la raquette
        self.x      = float(((Config.bords.width - self.rect.width) // 2))
        self.y      = float(Config.bords.height - (self.rect.height * 2))
        self.rect.x = self.x
        self.rect.y = self.y

    # active/désactive les mode balles collantes
    def setStickyMode(self, bfl):
        self.stickyMode = bfl

    # active/désactive les lasers
    def setLaserMode(self, blz):
        self.laserMode = blz
        self.__setLaserPos()

    # calcul les positions des lasers
    def __setLaserPos(self):
        if self.laserMode:
            # calcul des positions
            self.laserL = ((self.rect.centerx - (self.rect.width // 2)) + 6, self.rect.centery)
            self.laserR = ((self.rect.centerx + (self.rect.width // 2)) - 6, self.rect.centery)

    # active/désactive la double raquette
    def setDualMode(self, bdm):
        self.dualMode = bdm
        if self.dualMode:
            self.__setDMPos(True)
            self.__setLaserPos()
        else:
            # on remet la raquette courante
            if self.isNormalSz:
                self.setNormalSize()
            elif self.isLargeSz:
                self.setLargeSize()
            elif self.isSmallSz:
                self.setSmallSize()

    # calcul des positions de la seconde raquette
    def __setDMPos(self, bcnp):
        if bcnp:
            # on créé l'image vide
            self.dmimg = pygame.Surface([(self.rect.width * 2) + (Config.ball_sz * 2), self.rect.height])
            # on copie les raquettes dans l'image
            self.dmimg.blit(self.image, (0, 0), (0, 0, self.rect.width, self.rect.height))
            # on espace les raquettes de 2x le diamètre de la balle
            self.dmimg.blit(self.image, (self.rect.width + (Config.ball_sz * 2), 0), (0, 0, self.rect.width, self.rect.height))
            # la transparence
            colorkey = self.image.get_at((0,0))
            self.dmimg.set_colorkey(colorkey)
            self.dmrect = self.dmimg.get_rect()
            # le masque
            self.dmmask = pygame.mask.from_surface(self.dmimg)
            # calcul des positions
            if (self.rect.x + self.dmrect.width) < Config.bords.rectR.x:
                self.dmpos = (self.rect.x, self.rect.y)
            else:
                self.dmpos = (self.rect.x - self.dmrect.width, self.rect.y)
            self.dmrect.x = self.dmpos[0]
            self.dmrect.y = self.dmpos[1]
        self.image  = self.dmimg
        self.rect   = self.dmrect
        self.mask   = self.dmmask

    # les lasers tirent
    def laserFire(self):
        # missile de gauche
        (imgmL, rectmL) = Tools.load_png('missile-01.png')
        maskmL          = pygame.mask.from_surface(imgmL)
        rectmL.x        = self.laserL[0] - (rectmL.width // 2)
        rectmL.y        = self.laserL[1] - (self.rect.width // 2) - rectmL.height
        Config.bonus_adds['L'].append([imgmL, rectmL, maskmL])
        # missile de droite
        (imgmR, rectmR) = Tools.load_png('missile-01.png')
        maskmR          = pygame.mask.from_surface(imgmR)
        rectmR.x        = self.laserR[0] - (rectmL.width // 2)
        rectmR.y        = self.laserR[1] - (self.rect.width // 2) - rectmR.height
        Config.bonus_adds['L'].append([imgmR, rectmR, maskmR])

    # taille normale
    def setNormalSize(self):
        if self.rect is not None:
            # on garde la position courante
            self.x = self.rect.x
            # verif débordement à droite
            if (self.x + self.rectn.width) > Config.bords.rectR.x:
                self.x = (Config.bords.rectR.x - self.rectn.width)
            self.y = self.rect.y
        else:
            # au milieu en bas de la zone de jeu, on laisse une ligne vide sous la raquette
            self.x = float(((Config.bords.width - self.rectn.width) // 2))
            self.y = float(Config.bords.height - (self.rectn.height * 2))
        self.image      = self.imgn
        self.rect       = self.rectn
        self.mask       = self.maskn
        self.rect.x     = self.x
        self.rect.y     = self.y
        self.isNormalSz = True
        self.isLargeSz  = False
        self.isSmallSz  = False
        if self.dualMode:
            self.__setDMPos(True)
        self.__setLaserPos()

    # taille large
    def setLargeSize(self):
        if self.rect is not None:
            # on garde la position courante
            self.x = self.rect.x
            # verif débordement à droite
            if (self.x + self.rectl.width) > Config.bords.rectR.x:
                self.x = (Config.bords.rectR.x - self.rectl.width)
            self.y = self.rect.y
        else:
            # au milieu en bas de la zone de jeu, on laisse une ligne vide sous la raquette
            self.x = float(((Config.bords.width - self.rectl.width) // 2))
            self.y = float(Config.bords.height - (self.rectl.height * 2))
        self.image      = self.imgl
        self.rect       = self.rectl
        self.mask       = self.maskl
        self.rect.x     = self.x
        self.rect.y     = self.y
        self.isNormalSz = False
        self.isLargeSz  = True
        self.isSmallSz  = False
        if self.dualMode:
            self.__setDMPos(True)
        self.__setLaserPos()

    # taille small
    def setSmallSize(self):
        if self.rect is not None:
            # on garde la position courante
            self.x = self.rect.x
            # verif débordement à droite
            if (self.x + self.rects.width) > Config.bords.rectR.x:
                self.x = (Config.bords.rectR.x - self.rects.width)
            self.y = self.rect.y
        else:
            # au milieu en bas de la zone de jeu, on laisse une ligne vide sous la raquette
            self.x = float(((Config.bords.width - self.rects.width) // 2))
            self.y = float(Config.bords.height - (self.rects.height * 2))
        self.image      = self.imgs
        self.rect       = self.rects
        self.mask       = self.masks
        self.rect.x     = self.x
        self.rect.y     = self.y
        self.isNormalSz = False
        self.isLargeSz  = False
        self.isSmallSz  = True
        if self.dualMode:
            self.__setDMPos(True)
        self.__setLaserPos()

    def moveLeft(self):
        # au bord gauche?
        if (self.x - self.speed) < Config.bords.rectL.w:
            self.state = "still"
        else:
            self.x      = self.x - (self.speed)
            self.rect.x = self.x
            self.state = "moveleft"
            if Config.balls[0].state == "still":
                # la balle se déplace avec la raquette
                Config.balls[0].reset()
            self.__setLaserPos()

    def moveRight(self):
        # portail du niveau suivant actif et ouvert?
        if Config.bonus_actif['B']:
            if Config.bonus_adds['B'].state == "wait":
                if (self.x + self.rect.width + self.speed) >= Config.bords.rectR.x:
                    Tools.MsgCenter("Level UP!", 28, Config.zinfo.get_rect().centery, "green", True)
                    pygame.display.flip()
                    # petite tempo
                    pygame.time.wait(1500)
                    Tools.NextLevel()
                else:
                    self.x      = self.rect.x + (self.speed)
                    self.rect.x = self.x
                    self.state = "moveright"
                    if Config.balls[0].state == "still":
                        # la balle se déplace avec la raquette
                        Config.balls[0].reset()
                    self.__setLaserPos()
        # au bord droit?
        if (self.x + self.rect.width + self.speed) > Config.bords.rectR.x:
            self.state = "still"
        else:
            self.x      = self.rect.x + (self.speed)
            self.rect.x = self.x
            self.state = "moveright"
            if Config.balls[0].state == "still":
                # la balle se déplace avec la raquette
                Config.balls[0].reset()
            self.__setLaserPos()

    def update(self):
        if self.state == "moveleft":
            self.moveLeft()
        if self.state == "moveright":
            self.moveRight()

    def draw(self):
        if self.dualMode:
            # affichage des 2 raquettes
            Config.screen.blit(self.dmimg, self.dmrect)
        else:
            Config.screen.blit(self.image, self.rect)
        if self.laserMode:
            # on dessine les lasers
            pygame.draw.circle(Config.screen, self.laserColor, self.laserL, 5)
            pygame.draw.line(Config.screen, self.laserColor, self.laserL, (self.laserL[0] - 1, self.laserL[1] - (self.rect.height // 2)), 3)
            pygame.draw.circle(Config.screen, self.laserColor, self.laserR, 5)
            pygame.draw.line(Config.screen, self.laserColor, self.laserR, (self.laserR[0] - 1, self.laserR[1] - (self.rect.height // 2)), 3)

# eof