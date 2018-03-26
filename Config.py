#!/usr/bin/env python3
# -*- coding: utf8 -*-
#
# Un casse-briques (hommage à Arkanoid)
#
# 01/2018 PG (pguillaumaud@april.org)
#
# les globales
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
import sys, os, fnmatch

# --------------------------------------------------------------------------------
titre  = 'Briks! (hommage à Arkanoid)'
logo   = None
logo_r = None

# taille des briques
brw    = 43
brh    = 20
# nombre de briques / ligne
maxbr  = 13
# nombre de lignes de briques maxi
maxli  = 25

# taille des balles
ball_sz = 10

# l'écran et le fond
screenWidth, screenHeight = (800, 800)
screen = None
bg     = None
bg_r   = None

FPS    = 60
clock  = None

Perdu  = False

# le volume (0-100)
Volume = 10
# les sons
Sounds = {}

# test d'un niveau (appelé par level-editor)
testMode = False
# le fichier à tester
testFile = ""
# cheat code (god mode)
godMode  = False

# les bords
bords  = None
# les briques du niveau
bricks = []
# le joueur (la raquette)
player = None
# la ou les balles
balls  = []
# les bonus (pastilles):
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
bonus  = []
# les flags actif ou pas des bonus concernés
bonus_actif = { 'B': False, 'C': False, 'E': False, 'F': False, 'L': False, 'M': False, 'R': False, 'S': False, 'T': False, 'V': False }
# les timers max (en secondes) des bonus qui en ont besoin
bonus_tmax  = { 'B': 10, 'C': 10, 'E': 10, 'F': 15, 'L': 15, 'M': 10, 'R': 10, 'S': 10, 'T': 10, 'V': 10 }
# les timers des bonus qui en ont besoin
bonus_timer = { 'B': 0.0, 'C': 0.0, 'E': 0.0, 'F': 0.0, 'L': 0.0, 'M': 0.0, 'R': 0.0, 'S': 0.0, 'T': 0.0, 'V': 0.0 }
# les objets générés par certains bonus
bonus_adds  = { 'B': None, 'F': None, 'L': [] }
# les ennemis
enemys = []
# les générateurs d'ennemis
generator = []
# nombre maximum d'ennemis en même temps
max_E     = 4
# niveau avec un boss
bossLevel = False
# le boss
boss      = None

# la zone d'info
zinfo     = None
maxlife   = 5
life      = maxlife
score     = 0
highScore = 0

level     = 1

# le nom du programme (sans l'extension)
name_app  = os.path.splitext(os.path.basename(sys.argv[0]))[0]
# le répertoire principal
path_app  = os.path.dirname(sys.argv[0])

# max level = nombre de fichiers dans le répertoire des niveaux
maxlevel  = len(fnmatch.filter(os.listdir(os.path.join(path_app,'levels','')), 'level-*.txt'))
# eof
