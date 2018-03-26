# -*- coding: utf8 -*-
#
# Un casse-briques (hommage à Arkanoid)
#
# 01/2018 PG (pguillaumaud@april.org)
#
# Les pages de sprite (sprite sheet)
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
import pygame
from pygame.locals import *
import Config
import Tools

# --------------------------------------------------------------------------------
class SpriteSheet(pygame.sprite.Sprite):
    def __init__(self, filename, cols, rows, pos, trp):
        super().__init__()
        # la page
        self.sheet, self.srect = Tools.load_png(filename)
        # taille (en nombre de sprites)
        self.cols  = cols
        self.rows  = rows
        self.total = cols * rows
        # taille (en px)
        self.w = self.cellWidth  = int(self.srect.width / cols)
        self.h = self.cellHeight = int(self.srect.height / rows)
        # position initiale
        if pos is not None:
            self.x = pos[0]
            self.y = pos[1]
        else:
            # en haut a gauche par défaut
            self.x = Config.bords.rectL.w + 1
            self.y = Config.bords.rectT.h + 1
        # flag pour la transparence
        self.trp = trp
        # on sélectionne le premier par défaut
        self.setImage(0, 0)

    # sélectionne le sprite donné
    def setImage(self, col, row):
        # on garde la position pour l'animation
        self.cc = col
        self.cr = row
        ix = self.cc * self.cellWidth
        iy = self.cr * self.cellHeight
        # on créé l'image vide
        self.image = pygame.Surface([self.cellWidth, self.cellHeight])
        # on copie le sprite choisi dans l'image
        self.image.blit(self.sheet, (0, 0), (ix, iy, self.cellWidth, self.cellHeight))
        # la transparence
        if self.trp:
            colorkey = self.image.get_at((0,0))
            self.image.set_colorkey(colorkey)
        self.rect = self.image.get_rect()
        # position initiale
        self.rect.x = self.x
        self.rect.y = self.y
        # le masque
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self):
        Config.screen.blit(self.image, self.rect)

# eof