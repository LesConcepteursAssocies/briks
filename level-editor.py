#!/usr/bin/env python3
# -*- coding: utf8 -*-
#
# Un casse-briques (hommage à Arkanoid)
#
# L'éditeur des niveaux
#
# 01/2018 PG (pguillaumaud@april.org)
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
import sys, os, random, tempfile
import io, re, codecs
import datetime
import platform
import pygame
from pygame.locals import *
from pygame.color import *
import Config
import edConfig as Ced
import Tools
import Spritesheet
import Border
import Gui

# --------------------------------------------------------------------------------
# Fin du programme
def EditorExit():
    pygame.quit()
    sys.exit()

# --------------------------------------------------------------------------------
# sauve le niveau courant
def SaveLevel():
    fname = Ced.levelname.getText()
    if len(fname) > 0 and ((not isLevelEmpty()) or Config.bossLevel):
        if Config.testMode:
            # test, on sauve dans le répertoire tempo
            filename = os.path.join(os.path.abspath(os.sep), tempfile.gettempdir(), fname)
        else:
            filename = os.path.join(Config.path_app, 'levels', fname)
            if os.path.exists(filename) == True:
                # on fait un backup du fichier (si il n'existe pas déjà)
                newf = filename + '.save'
                if not os.path.exists(newf):
                    os.rename(filename, newf)
        # sauvegarde du niveau
        try:
            with io.open(filename,'w', encoding='utf-8') as f:
                # l'entête
                f.write(u'#\n')
                f.write(u'# Un casse-briques (hommage à Arkanoid)\n')
                f.write(u'#\n')
                f.write(u'# 01/2018 PG (pguillaumaud@april.org)\n')
                f.write(u'#\n')
                f.write(u'# Généré le '+datetime.datetime.now().strftime("%d/%m/%Y à %Hh%M")+u' par '+Config.name_app+u'\n')
                f.write(u'#\n')
                f.write(u'# .: ligne vide\n')
                f.write(u'# 0, ., \' \': brique vide (espace vide)\n')
                f.write(u'# 1: brique grise       ( 50 pts)\n')
                f.write(u'# 2: brique orange      ( 60 pts)\n')
                f.write(u'# 3: brique bleue       ( 70 pts)\n')
                f.write(u'# 4: brique verte       ( 80 pts)\n')
                f.write(u'# 5: brique rouge       ( 90 pts)\n')
                f.write(u'# 6: brique bleu fonçé  (100 pts)\n')
                f.write(u'# 7: brique violette    (110 pts)\n')
                f.write(u'# 8: brique jaune       (120 pts)\n')
                f.write(u'# 9: brique blanche     (130 pts)\n')
                f.write(u'# A: brique or          (incassable)\n')
                f.write(u'# B: brique métal       ( 50 pts)\n')
                f.write(u'# X: niveau d\'un BOSS   (500 pts)\n')
                f.write(u'#\n')
                if Config.bossLevel:
                    f.write(u'X\n')
                else:
                    for cl in range(Config.maxli):
                        line = ''
                        for i in range(Config.maxbr):
                            line = line + '{0:X}'.format(Ced.lmap[cl][i][0])
                        if len(re.findall(r'0',line)) == Config.maxbr:
                            # la ligne est entièrement vide, on abrège
                            line = '.'
                        f.write(line+'\n')
                f.write(u'# eof\n')
            # on met à jour le niveau courant
            Config.level = int(re.findall(r'-(\d+)',fname)[0])
            if Config.level > Config.maxlevel:
                Config.maxlevel = Config.level
        except IOError as message:
            print("Impossible de sauvegarder le niveau {0}: {1}".format(filename, message))

# --------------------------------------------------------------------------------
# charge le niveau courant
def LoadLevel():
    # encodages éventuels du fichier
    encodings = ['utf-8', 'windows-1250', 'windows-1252', 'ascii']

    fname = Ced.levelname.getText()
    if len(fname) > 0:
        filename = os.path.join(Config.path_app, 'levels', fname)
        for e in encodings:
            cl = 0
            try:
                RazLevel()
                Config.bossLevel = False
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
                            Ced.bsel_i       = 0
                            doBossLevel()
                            break
                        # analyse de la ligne (sans le cr de la fin)
                        for i, bn in enumerate(line.rstrip()):
                            if bn == '0' or bn == '.' or bn == ' ':
                                # brique vide (espace)
                                continue
                            Ced.lmap[cl][i][0] = int(bn, 16)
                            Ced.lmap[cl][i][1] = Ced.ico_br[int(bn, 16)][0]
                        # ligne suivante
                        cl += 1
                # on met à jour le niveau courant
                Config.level = int(re.findall(r'-(\d+)',fname)[0])
                if Config.level > Config.maxlevel:
                    Config.maxlevel = Config.level
            except UnicodeDecodeError:
                # mauvais encodage, on passe au suivant
                pass
            except IOError as message:
                print("Impossible de charger le niveau {0}: {1}".format(filename, message))
            else:
                # on a lu le fichier, on sort de la boucle
                break

# --------------------------------------------------------------------------------
# le menu
def EditorMenu():
    Config.screen.blit(Config.zinfo, (Config.bords.width, 0))
    # le titre
    Tools.MsgCenter("Briks!", 60, 0, "red", True)
    # le logo
    Config.screen.blit(Config.logo, (Config.bords.width, 70))
    Tools.MsgCenter("Editeur", 32, 150, "cyan", True)

    # le niveau courant
    font = pygame.font.Font(None, 32)
    cy = 200
    txt_lvl = font.render("Lvl: ", True, THECOLORS["red"])
    txt_nlv = font.render("{0:03d}/{1:03d}".format(Config.level, Config.maxlevel), True, THECOLORS["white"])
    pos_lvl = txt_lvl.get_rect()
    pos_nlv = txt_nlv.get_rect()
    # on centre
    ctx  = Config.bords.width + ((Config.screenWidth - Config.bords.width) // 2)
    ctx -= (pos_lvl.width + pos_nlv.width) // 2
    pos_lvl.x = ctx
    pos_lvl.y = cy
    Config.screen.blit(txt_lvl, pos_lvl)
    pos_nlv.x = pos_lvl.x + pos_lvl.width
    pos_nlv.y = cy
    Config.screen.blit(txt_nlv, pos_nlv)

    # les boutons prev/next
    if Ced.b_prev is None:
        Ced.b_prev = Gui.Button((pos_lvl.centerx - (pos_lvl.width // 2) - 12 - 10, pos_lvl.centery), 'prev.png', 'prev-clicked.png')
    Ced.b_prev.draw()
    if Ced.b_next is None:
        Ced.b_next = Gui.Button((pos_nlv.centerx + (pos_nlv.width // 2) + 12 + 11, pos_nlv.centery), 'next.png', 'next-clicked.png')
    Ced.b_next.draw()

    # les briques
    cx = Config.bords.width
    cy = 250
    for i in range(1, len(Ced.ico_br)):
        if Ced.ico_br[i][0] is None:
            # premier passage, chargement de l'image
            (Ced.ico_br[i][0], Ced.ico_br[i][1]) = Tools.load_png(Ced.ico_br[i][2])
        Tools.Msg("{0:2x}".format(i), 32, cx, cy, "white", False)
        Ced.ico_br[i][1].x = cx + 30
        Ced.ico_br[i][1].y = cy
        Config.screen.blit(Ced.ico_br[i][0], Ced.ico_br[i][1])
        cy += 30
        # on affiche sur 2 colonnes
        if i == (len(Ced.ico_br) // 2):
            cx = Config.bords.width + 115
            cy = 250

    # la brique pour les niveaux avec un boss
    cx = Config.bords.width + 115
    cy = 250 + (30 * ((len(Ced.ico_br) - 1) // 2))
    if Ced.boss_br[0] is None:
        # premier passage, chargement de l'image
        (Ced.boss_br[0], Ced.boss_br[1]) = Tools.load_png(Ced.boss_br[2])
    Ced.boss_br[1].x = cx + 30
    Ced.boss_br[1].y = cy
    Config.screen.blit(Ced.boss_br[0], Ced.boss_br[1])
    Tools.Msg(" X", 32, cx, cy, "white", False)

    # on dessine un rectangle autour de la brique sélectionnée
    if Ced.bsel_i > 0:
        rect       = Ced.ico_br[Ced.bsel_i][1]
        rect.x    -= 30
        rect.width = Config.brw + 30
        pygame.draw.rect(Config.screen, THECOLORS["white"], rect, 1)
    elif Config.bossLevel:
        rect       = Ced.boss_br[1]
        rect.x    -= 30
        rect.width = Config.brw + 30
        pygame.draw.rect(Config.screen, THECOLORS["white"], rect, 1)

    # les boutons
    cy = 450
    if Ced.b_save is None:
        Ced.b_save = Gui.Button((Config.bords.width + 24 + 5, cy + 24), 'save.png', 'save-clicked.png')
    Ced.b_save.draw()
    if Ced.b_load is None:
        Ced.b_load = Gui.Button((Config.bords.width + Config.zinfo.get_rect().width - 24 - 5, cy + 24), 'load.png', 'load-clicked.png')
    Ced.b_load.draw()
    # le reset centré entre les 2
    bspc = ((Ced.b_load.rect.x - (Ced.b_save.rect.x + Ced.b_save.rect.width)) - 48) // 2
    if Ced.b_raz is None:
        Ced.b_raz = Gui.Button((Config.bords.width + Ced.b_save.rect.width + 5 + bspc + 24, cy + 24), 'reset.png', 'reset-clicked.png')
    Ced.b_raz.draw()

    cy = 530
    if Ced.b_select is None:
        Ced.b_select = Gui.Button((Config.bords.width + 24 + 5, cy + 24), 'select.png', 'select-clicked.png')
    Ced.b_select.draw()
    if Ced.b_cut is None:
        Ced.b_cut = Gui.Button((Config.bords.width + Config.zinfo.get_rect().width - 24 - 5, cy + 24), 'cut.png', 'cut-clicked.png')
    Ced.b_cut.draw()
    # le copy centré entre les 2
    bspc = ((Ced.b_cut.rect.x - (Ced.b_select.rect.x + Ced.b_select.rect.width)) - 48) // 2
    if Ced.b_copy is None:
        Ced.b_copy = Gui.Button((Config.bords.width + Ced.b_select.rect.width + 5 + bspc + 24, cy + 24), 'copy.png', 'copy-clicked.png')
    Ced.b_copy.draw()

    cy = 600
    if Ced.b_paste is None:
        Ced.b_paste = Gui.Button((Config.bords.width + 24 + 5, cy + 24), 'paste.png', 'paste-clicked.png')
    Ced.b_paste.draw()
    if Ced.b_cancel is None:
        Ced.b_cancel = Gui.Button((Config.bords.width + Config.zinfo.get_rect().width - 24 - 5, cy + 24), 'cancel.png', 'cancel-clicked.png')
    Ced.b_cancel.draw()
    # le undo centré entre les 2
    bspc = ((Ced.b_cancel.rect.x - (Ced.b_paste.rect.x + Ced.b_paste.rect.width)) - 48) // 2
    if Ced.b_undo is None:
        Ced.b_undo = Gui.Button((Config.bords.width + Ced.b_paste.rect.width + 5 + bspc + 24, cy + 24), 'undo.png', 'undo-clicked.png')
    Ced.b_undo.draw()

    cy = 680
    if Ced.b_grid is None:
        Ced.b_grid = Gui.Button((Config.bords.width + 24 + 5, cy + 24), 'grid-off.png', 'grid-on.png')
        Ced.b_grid.setClicked(Ced.view_grid)
    Ced.b_grid.draw()
    if Ced.b_test is None:
        Ced.b_test = Gui.Button((Config.bords.width + Config.zinfo.get_rect().width - 24 - 5, cy + 24), 'test.png', 'test-clicked.png')
    Ced.b_test.draw()
    
    # les touches diverses
    cy = Config.screenHeight - 15
    Tools.MsgCenter("ESC: quitter", 18, cy, "white", False)

# --------------------------------------------------------------------------------
# renvoi True si le niveau courant est vide
def isLevelEmpty():
    for cl in range(Config.maxli):
        for i in range(Config.maxbr):
            if Ced.lmap[cl][i][0] > 0:
                if Ced.lmap[cl][i][0] == 10:
                    # une brique incassable
                    pass
                else:
                    # une brique normale, le niveau n'est pas vide
                    return False
    return True

# --------------------------------------------------------------------------------
# RàZ du niveau en cours
def RazLevel():
    # la marge
    marge = (Config.bords.rectT.w - (Config.maxbr * Config.brw)) // 2

    for cl in range(Config.maxli):
        for i in range(Config.maxbr):
            # on créé une brique vide
            image = pygame.Surface([Config.brw, Config.brh])
            rect  = image.get_rect()
            # position de la brique
            rect.x = (Config.bords.rectL.w + marge) + (i * Config.brw)
            rect.y = (Config.bords.rectT.h + 5) + (cl * Config.brh)
            Ced.lmap[cl][i] = [0, image, rect]

# --------------------------------------------------------------------------------
# affichage du niveau en cours
def DrawLevel():
    for cl in range(Config.maxli):
        for i in range(Config.maxbr):
            if Ced.lmap[cl][i][0] > 0:
                Config.screen.blit(Ced.lmap[cl][i][1],  Ced.lmap[cl][i][2])

# --------------------------------------------------------------------------------
# affichage de la grille
def DrawGrid():
    # la marge
    marge = (Config.bords.rectT.w - (Config.maxbr * Config.brw)) // 2

    for cl in range(Config.maxli):
        for i in range(Config.maxbr):
            # position de la brique
            x = (Config.bords.rectL.w + marge) + (i * Config.brw)
            y = (Config.bords.rectT.h + 5) + (cl * Config.brh)
            pygame.draw.rect(Config.screen, THECOLORS["white"], (x, y, Config.brw, Config.brh), 1)

# --------------------------------------------------------------------------------
# copie de la map dans le undos
def PushUndos():
    if len(Ced.undos) < Ced.maxundo:
        undo = [[0 for i in range(Config.maxbr)] for cl in range(Config.maxli)]
        for cl in range(Config.maxli):
            for i in range(Config.maxbr):
                undo[cl][i] = Ced.lmap[cl][i][0]
        Ced.undos.append(undo)

# --------------------------------------------------------------------------------
# restauration du dernier undo
def PopUndos():
    if len(Ced.undos) > 0:
        undo = Ced.undos.pop((len(Ced.undos)-1))
        for cl in range(Config.maxli):
            for i in range(Config.maxbr):
                Ced.lmap[cl][i][0] = undo[cl][i]
                Ced.lmap[cl][i][1] = Ced.ico_br[undo[cl][i]][0]

# --------------------------------------------------------------------------------
# le niveau courant est un niveau avec un boss
def doBossLevel():
    # on vide le niveau
    RazLevel()
    Ced.boss_sps = None
    Ced.boss_brL = None
    Ced.boss_brR = None
    # on place l'image du boss au centre
    # taille en briques: 3x8
    # la marge
    marge = (Config.bords.rectT.w - (Config.maxbr * Config.brw)) // 2
    row   = (Config.maxli - 8) // 2
    col   = (Config.maxbr - 3) // 2
    x     = (Config.bords.rectL.w + marge) + (col * Config.brw)
    y     = (Config.bords.rectT.h + 5) + (row * Config.brh)
    if Config.level > 34:
        # boss doh
        Ced.boss_sps = Spritesheet.SpriteSheet('boss-doh.png', 3, 1, (x, y), True)
        # on place les bras
        x           -= (Ced.boss_sps.rect.width - 44)
        y           += 27
        Ced.boss_brL = Spritesheet.SpriteSheet('boss-doh-bras-gauche.png', 6, 1, (x, y), True)
        x           += (Ced.boss_sps.rect.width + 56)
        Ced.boss_brR = Spritesheet.SpriteSheet('boss-doh-bras-droit.png', 6, 1, (x, y), True)
    else:
        # boss classique
        Ced.boss_sps = Spritesheet.SpriteSheet('boss.png', 4, 1, (x, y), True)
    Ced.boss_sps.draw()
    if Ced.boss_brL is not None:
        Ced.boss_brL.draw()
    if Ced.boss_brR is not None:
        Ced.boss_brR.draw()

# --------------------------------------------------------------------------------
# gestion des événements
def event_handler():
    for event in pygame.event.get():
        if event.type == QUIT:
            EditorExit()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                EditorExit()
            Ced.levelname.handle_event(event)
        elif event.type == MOUSEBUTTONDOWN:
            # prev ?
            if Ced.b_prev.handle_event(event):
                Ced.b_prev.setClicked(True)
                Config.level -= 1
                if Config.level < 1:
                    # on boucle
                    Config.level = Config.maxlevel
                Ced.levelname.setText('level-{0:03d}.txt'.format(Config.level))
            # next ?
            elif Ced.b_next.handle_event(event):
                Ced.b_next.setClicked(True)
                Config.level += 1
                if Config.level > Config.maxlevel:
                    # on boucle
                    Config.level = 1
                Ced.levelname.setText('level-{0:03d}.txt'.format(Config.level))
            # save ?
            elif Ced.b_save.handle_event(event):
                Ced.b_save.setClicked(True)
                SaveLevel()
            # load ?
            elif Ced.b_load.handle_event(event):
                Ced.b_load.setClicked(True)
                LoadLevel()
            # reset ?
            elif Ced.b_raz.handle_event(event):
                Ced.b_raz.setClicked(True)
                PushUndos()
                RazLevel()
                Config.bossLevel = False
                Ced.b_test.setClicked(False)
                Config.testMode  = False
            # select ?
            elif Ced.b_select.handle_event(event) and not Config.bossLevel:
                if Ced.in_select:
                    Ced.b_select.setClicked(False)
                    Ced.in_select = False
                else:
                    Ced.b_select.setClicked(True)
                    Ced.in_select = True
            # copy ?
            elif Ced.b_copy.handle_event(event) and Ced.z_select is not None and not Config.bossLevel:
                Ced.b_copy.setClicked(True)
                Ced.z_select.copySelect()
                Ced.in_copy = True
            # cut ?
            elif Ced.b_cut.handle_event(event) and Ced.z_select is not None and not Config.bossLevel:
                Ced.b_cut.setClicked(True)
                Ced.z_select.cutSelect()
                Ced.in_cut = True
            # paste ?
            elif Ced.b_paste.handle_event(event) and Ced.z_select is not None and (Ced.in_copy or Ced.in_cut) and not Config.bossLevel:
                if Ced.in_copy:
                    Ced.b_copy.setClicked(False)
                    Ced.in_copy  = False
                elif Ced.in_cut:
                    Ced.b_cut.setClicked(False)
                    Ced.in_cut   = False
                Ced.b_paste.setClicked(True)
                Ced.in_paste = True
            # undo ?
            elif Ced.b_undo.handle_event(event) and ((Ced.z_select is not None) or (len(Ced.undos) > 0)) and not Config.bossLevel:
                if Ced.z_select is not None:
                    Ced.b_undo.setClicked(True)
                    # on reset la sélection
                    Ced.z_select.undoSelect()
                    # fin de sélection
                    del Ced.z_select
                    Ced.z_select  = None
                    Ced.in_copy   = False
                    Ced.in_select = False
                    Ced.in_cut    = False
                    # reset des boutons
                    for btn in [ Ced.b_select, Ced.b_copy, Ced.b_cut, Ced.b_paste ]:
                        btn.setClicked(False)
                elif len(Ced.undos) > 0:
                    Ced.b_undo.setClicked(True)
                    PopUndos()
            # cancel ?
            elif Ced.b_cancel.handle_event(event) and Ced.z_select is not None and not Config.bossLevel:
                Ced.b_cancel.setClicked(True)
                # fin de sélection
                del Ced.z_select
                Ced.z_select  = None
                Ced.in_copy   = False
                Ced.in_select = False
                Ced.in_cut    = False
                # reset des boutons
                for btn in [ Ced.b_select, Ced.b_copy, Ced.b_cut, Ced.b_paste ]:
                    btn.setClicked(False)
            # view_grid ?
            elif Ced.b_grid.handle_event(event):
                Ced.view_grid = not Ced.view_grid
                Ced.b_grid.setClicked(Ced.view_grid)
            # test ?
            elif Ced.b_test.handle_event(event):
                fname = Ced.levelname.getText()
                if len(fname) > 0 and ((not isLevelEmpty()) or Config.bossLevel):
                    Ced.b_test.setClicked(True)
                    Ced.b_test.draw()
                    pygame.display.update()
                    pygame.event.pump()
                    # on sauve le niveau dans le répertoire tempo
                    Config.testMode = True
                    SaveLevel()
                    # on lance le programme pour tester le niveau
                    if platform.system() == 'Windows':
                        os.system('{0} {1} -t {2}'.format(sys.executable, os.path.join(Config.path_app, '', 'briks.py'), fname))
                    elif platform.system() == 'Linux':
                        os.system('{0} {1} -t {2}'.format(sys.executable, os.path.join(Config.path_app, '', 'briks.py'), fname))
                    # on supprime le niveau temporaire
                    try:
                        os.remove(os.path.join(os.path.abspath(os.sep), tempfile.gettempdir(), fname))
                    except:
                        pass
                    Ced.b_test.setClicked(False)
                    Config.testMode = False
            elif not Ced.in_paste:
                # une brique du menu ?
                if not Config.bossLevel:
                    for i in range(1, len(Ced.ico_br)):
                        if Ced.ico_br[i][1].collidepoint(event.pos):
                            # clic droit déselectionne
                            if event.button == 3 and Ced.bsel_i == i:
                                Ced.bsel_i = 0
                            elif event.button != 3:
                                Ced.bsel_i = i
                            break
                # la brique du bossLevel ?
                if Ced.boss_br[1].collidepoint(event.pos):
                    # clic droit déselectionne
                    if event.button == 3:
                        Config.bossLevel = False
                    elif event.button != 3:
                        Config.bossLevel = True
                        Ced.bsel_i       = 0
                        doBossLevel()
                # une brique du niveau ?
                if not Config.bossLevel:
                    for cl in range(Config.maxli):
                        for i in range(Config.maxbr):
                            if Ced.lmap[cl][i][2].collidepoint(event.pos):
                                if event.button == 1 and Ced.in_select:
                                    # clic gauche, début de sélection
                                    if Ced.z_select is None:
                                        Ced.z_select = Gui.SelectionRect((cl, i))
                                        Ced.z_select.draw()
                                else:
                                    PushUndos()
                                    if Ced.bsel_i > 0:
                                        # on met la brique sélectionnée
                                        Ced.lmap[cl][i][0] = Ced.bsel_i
                                        Ced.lmap[cl][i][1] = Ced.ico_br[Ced.bsel_i][0]
                                    elif Ced.lmap[cl][i][0] > 0:
                                        # clic sur une case pleine, on la vide
                                        Ced.lmap[cl][i][0] = 0
                                        Ced.lmap[cl][i][1] = pygame.Surface([Config.brw, Config.brh])
                Ced.levelname.handle_event(event)
        elif event.type == MOUSEMOTION:
            if event.buttons[0] == 1:
                # bouton gauche appuyé en mouvement
                for cl in range(Config.maxli):
                    for i in range(Config.maxbr):
                        if Ced.lmap[cl][i][2].collidepoint(event.pos):
                            if Ced.in_select and Ced.z_select is not None:
                                Ced.z_select.updateRect((cl, i))
                                Ced.z_select.draw()
                            else:
                                if Ced.bsel_i > 0:
                                    # on met la brique sélectionnée
                                    Ced.lmap[cl][i][0] = Ced.bsel_i
                                    Ced.lmap[cl][i][1] = Ced.ico_br[Ced.bsel_i][0]
                                elif Ced.lmap[cl][i][0] > 0:
                                    # clic sur une case pleine, on la vide
                                    Ced.lmap[cl][i][0] = 0
                                    Ced.lmap[cl][i][1] = pygame.Surface([Config.brw, Config.brh])
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1 and Ced.in_select and Ced.z_select is not None:
                # fin de sélection
                Ced.b_select.setClicked(False)
                Ced.in_select = False
                rect      = None
                # update final
                for cl in range(Config.maxli):
                    for i in range(Config.maxbr):
                        if Ced.lmap[cl][i][2].collidepoint(event.pos):
                            rect = Ced.z_select.updateRect((cl, i))
                            Ced.z_select.draw()
                            break
                    if rect is not None:
                        break
            elif event.button == 1 and Ced.in_paste:
                paste_finish = False
                for cl in range(Config.maxli):
                    for i in range(Config.maxbr):
                        if Ced.lmap[cl][i][2].collidepoint(event.pos):
                            # copie de la sélection
                            Ced.z_select.pasteSelect((cl, i))
                            Ced.in_paste = False
                            Ced.b_paste.setClicked(False)
                            paste_finish = True
                            break
                    if paste_finish:
                        break
            else:
                for btn in [ Ced.b_prev, Ced.b_next, Ced.b_save, Ced.b_load, Ced.b_raz, Ced.b_undo, Ced.b_cancel ]:
                    if btn.handle_event(event):
                        btn.setClicked(False)

# --------------------------------------------------------------------------------
def main(lfile):
    # Initialisation de la fenêtre d'affichage
    pygame.init()
    Config.screen = pygame.display.set_mode((Config.screenWidth, Config.screenHeight), HWSURFACE | DOUBLEBUF)
    pygame.display.set_caption(Config.titre+' ('+Config.name_app+')')
    # le logo d'hommage ^^
    Config.logo, Config.logo_r = Tools.load_png('logo.png')

    # les bords de la surface de jeu
    Config.bords = Border.Border()
    # le fond
    Config.bg, Config.bg_r = Tools.load_png('bg-editor.png')
    # on met à l'échelle le fond si besoin
    if (Config.bg_r.width, Config.bg_r.height) != (Config.bords.width, Config.bords.height):
        Config.bg = pygame.transform.scale(Config.bg, (Config.bords.width, Config.bords.height))

    # la zone d'info
    Config.zinfo = pygame.Surface([(Config.screenWidth - Config.bords.width), Config.screenHeight])
    Config.zinfo.fill(THECOLORS["black"])

    # zone de saisie/affichage du fichier (centrée dans la zone d'info)
    lvx = Config.bords.width + ((Config.screenWidth - Config.bords.width) // 2) - (Config.zinfo.get_rect().width // 2) + 3
    Ced.levelname = Gui.InputBox(lvx, Config.screenHeight - 55, Config.zinfo.get_rect().width - 10, 32, 'level-{0:03d}.txt'.format(Config.level))

    RazLevel()

    # Affichage
    Config.screen.blit(Config.bg, (0, 0))
    Config.bords.draw()
    if Ced.view_grid:
        DrawGrid()
    EditorMenu()
    DrawLevel()
    pygame.display.flip()

    if lfile is not None:
        # fichier à charger
        Ced.levelname.setText(lfile)
        LoadLevel()

    # Initialisation de l'horloge
    Config.clock = pygame.time.Clock()

    # Boucle d'évènements
    while True:
        event_handler()
        dt = Config.clock.tick(Config.FPS) / 1000

        # affichages
        Config.screen.blit(Config.bg, (0, 0))
        Config.bords.draw()
        if Ced.view_grid:
            DrawGrid()
        EditorMenu()
        DrawLevel()
        if Config.bossLevel:
            Ced.boss_sps.draw()
            if Ced.boss_brL is not None:
                Ced.boss_brL.draw()
            if Ced.boss_brR is not None:
                Ced.boss_brR.draw()
        Ced.levelname.draw()
        if Ced.z_select is not None:
            Ced.z_select.draw()
        pygame.display.flip()

# --------------------------------------------------------------------------------
if __name__ == '__main__':
    import argparse

    # les arguments éventuels
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-l", required=False, dest="levelfile", action="store")
    args = parser.parse_args()

    main(args.levelfile)
# eof
