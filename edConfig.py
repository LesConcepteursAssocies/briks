#!/usr/bin/env python3
# -*- coding: utf8 -*-
#
# Un casse-briques (hommage à Arkanoid)
#
# 01/2018 PG (pguillaumaud@april.org)
#
# les globales de l'éditeur
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
import Config

# --------------------------------------------------------------------------------
# la map du niveau en cours
lmap  = [[[0, None, None] for i in range(Config.maxbr)] for cl in range(Config.maxli)]

# undo max en édition
maxundo = 5
# les sauvegardes pour les undo
undos   = []

# les briques et les images associées
ico_br = [ [None, None, ''],
         [None, None, 'brik-01.png'],
         [None, None, 'brik-02.png'],
         [None, None, 'brik-03.png'],
         [None, None, 'brik-04.png'],
         [None, None, 'brik-05.png'],
         [None, None, 'brik-06.png'],
         [None, None, 'brik-07.png'],
         [None, None, 'brik-08.png'],
         [None, None, 'brik-09.png'],
         [None, None, 'brik-0A.png'],
         [None, None, 'brik-0B.png'] ]

# la brique sélectionnée
bsel_i = 0

# la brique pour les niveaux d'un boss
boss_br  = [None, None, 'menu-boss.png']
# le spritesheet idoine
boss_sps = None
# les bras du boss doh
boss_brL = None
boss_brR = None

# les boutons du menu
b_prev   = None
b_next   = None
b_save   = None
b_load   = None
b_raz    = None
b_select = None
b_copy   = None
b_cut    = None
b_paste  = None
b_cancel = None
b_undo   = None
b_grid   = None
b_test   = None

in_select = False
in_copy   = False
in_cut    = False
in_paste  = False
z_select  = None

view_grid = True

# le nom du fichier du niveau en cours
levelname = None

# eof
