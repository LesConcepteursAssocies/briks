# -*- coding: utf8 -*-
#
# Un casse-briques (hommage à Arkanoid)
#
# 01/2018 PG (pguillaumaud@april.org)
#
# Les bord de la zone de jeu
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
class Border(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # les sprites
        self.imgL, self.rectL = Tools.load_png('bord-gauche.png')
        self.imgT, self.rectT = Tools.load_png('bord-haut.png')
        self.imgR, self.rectR = Tools.load_png('bord-droit.png')
        # et les masques
        self.maskL  = pygame.mask.from_surface(self.imgL)
        self.maskT  = pygame.mask.from_surface(self.imgT)
        self.maskR  = pygame.mask.from_surface(self.imgR)
        # taille totale
        self.width  = self.rectL.w + self.rectT.w + self.rectR.w
        self.height = self.rectL.h
        # positionnement des bords
        self.rectL.x = 0
        self.rectL.y = 0
        self.rectT.x = self.rectL.w
        self.rectT.y = 0
        self.rectR.x = self.rectL.w + self.rectT.w
        self.rectR.y = 0

    def draw(self):
        Config.screen.blit(self.imgL, self.rectL)
        Config.screen.blit(self.imgT, self.rectT)
        Config.screen.blit(self.imgR, self.rectR)

# eof