# -*- coding: utf8 -*-
#
# Un casse-briques (hommage à Arkanoid)
#
# 01/2018 PG (pguillaumaud@april.org)
#
# Les niveaux du jeu
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
import tempfile
import os, codecs
import pygame
from pygame.locals import *
import Config
import Tools
import Brick

# --------------------------------------------------------------------------------
# Chargement d'un niveau
def LoadLevel(nlv=1):
    # encodages éventuels du fichier
    encodings = ['utf-8', 'windows-1250', 'windows-1252', 'ascii']
    # ligne courante
    cl = 0
    # la marge
    marge = (Config.bords.rectT.w - (Config.maxbr * Config.brw)) // 2

    # reset du tableau
    Config.bricks    = []
    Config.bossLevel = False

    # lecture du niveau
    if Config.testMode:
        filename = os.path.join(os.path.abspath(os.sep), tempfile.gettempdir(), Config.testFile)
    else:
        filename = os.path.join(Config.path_app, 'levels', 'level-{0:03d}.txt'.format(nlv))
    for e in encodings:
        try:
            with codecs.open(filename, 'r', encoding=e) as f:
                for line in f:
                    # on passe les commentaires
                    if line[0] == '#':
                        continue
                    # on passe les lignes vides
                    if line[0] == '.' and len(line) == 1:
                        cl += 1
                        continue
                    # niveau d'un boss ?
                    if line[0] == 'X':
                        Config.bossLevel = True
                        break
                    # analyse de la ligne (sans le cr de la fin)
                    for i, bn in enumerate(line.rstrip()):
                        if bn == '0' or bn == '.' or bn == ' ':
                            # brique vide (espace)
                            continue
                        # position de la brique
                        x = (Config.bords.rectL.w + marge) + (i * Config.brw)
                        y = (Config.bords.rectT.h + 5) + (cl * Config.brh)
                        Config.bricks.append(Brick.Brick(x, y, int(bn, 16)))

                    # ligne suivante
                    cl += 1
        except UnicodeDecodeError:
            # mauvais encodage, on passe au suivant
            pass
        except IOError as message:
            print("Impossible de charger le niveau: {0}".format(filename))
            raise SystemExit(message)
        else:
            # on a lu le fichier, on sort de la boucle
            break

# --------------------------------------------------------------------------------
# affichage du niveau courant
def DrawLevel():
    if Config.bossLevel:
        Config.boss.draw()
    else:
        for b in Config.bricks:
            b.draw()

# --------------------------------------------------------------------------------
# renvoi True si le niveau courant est fini
def FinishedLevel():
    if not Config.bossLevel:
        # on compte les briques incassables
        nb = 0
        for b in Config.bricks:
            if b.hits < 0:
                nb += 1

        if nb == len(Config.bricks):
            return True

    return False

# eof