# -*- coding: utf8 -*-
#
# Un casse-briques (hommage à Arkanoid)
#
# 01/2018 PG (pguillaumaud@april.org)
#
# Une petite GUI pour l'éditeur
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
import edConfig as Ced
import Tools

# --------------------------------------------------------------------------------
# les boutons
class Button(pygame.sprite.Sprite):
    def __init__(self, pos, file_off, file_on):
        super().__init__()
        if pos is not None:
            # position du centre du bouton
            (self.cx, self.cy) = pos
        else:
            (self.cx, self.cy) = (0, 0)
        # les sprites on/off
        self.img_off, self.rect_off = Tools.load_png(file_off)
        self.img_on,  self.rect_on  = Tools.load_png(file_on)
        self.image = None
        self.rect  = None
        # off (non cliqué) par défaut
        self.setClicked(False)

    # sélectionne le sprite donné
    # (True: on, False: off)
    def setClicked(self, on_off):
        if on_off:
            self.image = self.img_on
            self.rect  = self.rect_on
        else:
            self.image = self.img_off
            self.rect  = self.rect_off
        self.on_off       = on_off
        self.rect.centerx = self.cx
        self.rect.centery = self.cy

    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN or event.type == MOUSEBUTTONUP:
            # bouton cliqué ?
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def draw(self):
        Config.screen.blit(self.image, self.rect)

# --------------------------------------------------------------------------------
# une zone de saisie/affichage
# (inspiré de: https://stackoverflow.com/questions/46390231/how-to-create-a-text-input-box-with-pygame)
class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.font  = pygame.font.Font(pygame.font.match_font('freemono'), 24)
        self.rect  = pygame.Rect(x, y, w, h)
        # couleur actif/inactif
        self.c_on  = THECOLORS["white"]
        self.c_off = THECOLORS["grey"]
        self.color = self.c_off
        self.text  = text
        self.imgt  = self.font.render(text, True, self.color)
        self.actif = False
        # le curseur à la fin du texte par défaut
        self.cpos  = len(self.text) - 1
        # couleur du curseur
        self.col_c = THECOLORS["red"]

    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN:
            # clic dans la zone ?
            if self.rect.collidepoint(event.pos):
                # switch actif/inactif
                self.actif = not self.actif
            else:
                self.actif = False
            # couleur actif/inactif
            self.color = self.c_on if self.actif else self.c_off
            self.imgt  = self.font.render(self.text, True, self.color)
        if event.type == KEYDOWN:
            if self.actif:
                if event.key == K_RETURN:
                    return
                elif event.key == K_BACKSPACE:
                    if self.cpos > 0:
                        self.text = self.text[:max(self.cpos - 1, 0)] + self.text[self.cpos:]
                        # nouvelle position du curseur
                        self.cpos = max(self.cpos - 1, 0)
                elif event.key == K_DELETE:
                    self.text = self.text[:self.cpos] + self.text[self.cpos + 1:]
                elif event.key == K_RIGHT:
                    # curseur à droite
                    self.cpos = min(self.cpos + 1, len(self.text) - 1)
                elif event.key == K_LEFT:
                    # curseur à gauche
                    self.cpos = max(self.cpos - 1, 0)
                elif event.key == K_END:
                    # curseur à la fin du texte
                    self.cpos = len(self.text) - 1
                elif event.key == K_HOME:
                    # curseur au début
                    self.cpos = 0
                else:
                    self.text  = self.text[:self.cpos] + event.unicode + self.text[self.cpos:]
                    self.cpos += len(event.unicode)
                    self.cpos  = min(self.cpos, len(self.text) - 1)
                self.imgt = self.font.render(self.text, True, self.color)

    def setText(self, text):
        self.text = text
        self.imgt = self.font.render(text, True, self.color)

    def getText(self):
        return self.text

    def draw(self):
        # le texte
        Config.screen.blit(self.imgt, (self.rect.x+5, self.rect.y+5))
        # le curseur
        if self.actif:
            curw  = 12
            cposx = min(self.font.size(self.text[:self.cpos])[0], self.rect.w)
            cposy = 22
            pygame.draw.rect(self.imgt, self.col_c, (cposx, cposy, curw, 2))
        # le rectangle de la zone
        pygame.draw.rect(Config.screen, self.color, self.rect, 2)

# --------------------------------------------------------------------------------
# Outil de sélection
# (inspiré de http://www.pygame.org/pcr/box_selection/index.php)
class SelectionRect:
    def __init__(self, start):
        # position de départ (ligne/colonne)
        row,col    = start
        self.start = (row, col)
        self.rect  = row, col, 0, 0
        # le clipboard
        self.clipboard = [[0 for i in range(Config.maxbr)] for cl in range(Config.maxli)]
        # pour le undo
        self.undo      = [[0 for i in range(Config.maxbr)] for cl in range(Config.maxli)]
        self.rect_undo = None

    # copie de la map dans le clipboard
    # on ne garde que le type de la brique
    def _copylmap(self):
        for cl in range(Config.maxli):
            for i in range(Config.maxbr):
                self.clipboard[cl][i] = Ced.lmap[cl][i][0]

    # copie de la map dans le undo
    def _copyundo(self):
        for cl in range(Config.maxli):
            for i in range(Config.maxbr):
                self.undo[cl][i] = Ced.lmap[cl][i][0]
                
    # mise à jour de la sélection
    def updateRect(self, now):
        row,col   = self.start
        mrow,mcol = now
        if mcol < col:
            if mrow < row:
                self.rect = mrow, mcol, row-mrow, col-mcol
            else:
                self.rect = row, mcol, mrow-row, col-mcol
        elif mrow < row:
            self.rect = mrow, col, row-mrow, mcol-col
        else:
            self.rect = row, col, mrow-row, mcol-col
        return self.rect

    # dessine un rectangle autour des briques sélectionnées
    def draw(self):
		# top/left du rectangle
        x  = Ced.lmap[self.rect[0]][self.rect[1]][2].x
        y  = Ced.lmap[self.rect[0]][self.rect[1]][2].y
        # taille du rectangle
        w  = Config.brw + (self.rect[3] * Config.brw)
        h  = Config.brh + (self.rect[2] * Config.brh)
		# grey33 transparent
        cc = (84, 84, 84, 160)
        # surface vide transparente
        image = pygame.Surface([w, h])
        image.set_alpha(160)
        image.fill(cc)
        Config.screen.blit(image, (x, y))
        pygame.display.update((x, y, w, h))

    # copie la sélection de la map dans le clipboard
    def copySelect(self):
        self._copylmap()
    
    # supprime (cut) la sélection de la map
    def cutSelect(self):
        # copie dans le clipboard avant le cut
        self._copylmap()
        for cl in range(self.rect[0], (self.rect[0] + self.rect[2]) + 1):
            for i in range(self.rect[1], (self.rect[1] + self.rect[3]) + 1):
                Ced.lmap[cl][i][0] = 0

    # copie de la sélection à la position donnée
    def pasteSelect(self, pos):
        # copie dans le undo avant
        self._copyundo()
        # position de départ
        row,col = pos
        self.rect_undo = row, col, self.rect[2], self.rect[3]
        for cl in range(self.rect[0], (self.rect[0] + self.rect[2]) + 1):
            pcol = col
            for i in range(self.rect[1], (self.rect[1] + self.rect[3]) + 1):
                Ced.lmap[row][pcol][0] = self.clipboard[cl][i]
                Ced.lmap[row][pcol][1] = Ced.ico_br[self.clipboard[cl][i]][0]
                pcol += 1
                if pcol >= Config.maxbr:
                    break
            row += 1
            if row >= Config.maxli:
                break
                
    # reset de la sélection
    def undoSelect(self):
        if self.rect_undo is not None:
            for cl in range(self.rect[0], (self.rect[0] + self.rect[2]) + 1):
                for i in range(self.rect[1], (self.rect[1] + self.rect[3]) + 1):
                    Ced.lmap[cl][i][0] = self.clipboard[cl][i]
                    Ced.lmap[cl][i][1] = Ced.ico_br[self.clipboard[cl][i]][0]
            # position de départ
            row = self.rect_undo[0]
            for cl in range(self.rect_undo[0], (self.rect_undo[0] + self.rect_undo[2]) + 1):
                pcol = self.rect_undo[1]
                for i in range(self.rect_undo[1], (self.rect_undo[1] + self.rect_undo[3]) + 1):
                    Ced.lmap[row][pcol][0] = self.undo[cl][i]
                    Ced.lmap[row][pcol][1] = Ced.ico_br[self.undo[cl][i]][0]
                    pcol += 1
                    if pcol >= Config.maxbr:
                        break
                row += 1
                if row >= Config.maxli:
                    break

# eof