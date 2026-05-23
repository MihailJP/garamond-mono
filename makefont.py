#!/usr/bin/env python3

import fontforge
from sys import argv
import fontforge_refsel

font = fontforge.open(argv[2])
fontforge_refsel.decomposeNestedRefs(font, True)
font.buildOrReplaceAALTFeatures()

if argv[1].endswith(".sfd"):
	font.save(argv[1])
else:
	font.generate(argv[1], flags=('no-mac-names','opentype','no-FFTM-table'))

font.close()
