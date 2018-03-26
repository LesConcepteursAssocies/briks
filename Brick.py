# -*- coding: utf8 -*-
#
# Un casse-briques (hommage à Arkanoid)
#
# 01/2018 PG (pguillaumaud@april.org)
#
# Les briques
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
from pygame.color import *
import Config
import Tools

# --------------------------------------------------------------------------------
# bn: numéro de la brique pour l'image (détermine aussi le type de brique)
#
class Brick(pygame.sprite.Sprite):
    def __init__(self, x, y, bn):
        super().__init__()
        # le sprite
        self.img, self.rect = Tools.load_png('brik-{0:02X}'.format(bn)+'.png')
        # et le masque
        self.mask = pygame.mask.from_surface(self.img)
        # positionnement
        self.x      = x
        self.y      = y
        self.rect.x = self.x
        self.rect.y = self.y
        # le numéro détermine le nombre de hits pour casser la brique, et le score obtenu
        if bn <= 9:
            # de 1 à 9: 1 hit
            self.hits = 1
            self.npts = 40 + (10 * bn)
        elif bn == 10:
            # 10 (or): incassable
            self.hits = -1
            self.npts = 0
        else:
            # 11 (grise) et plus: 3 hits
            self.hits = 3
            self.npts = 50

    def draw(self):
        Config.screen.blit(self.img, self.rect)

# eof