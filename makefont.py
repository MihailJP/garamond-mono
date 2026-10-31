#!/usr/bin/env python3

import fontforge
from sys import argv, stderr
import fontforge_refsel

font = fontforge.open(argv[2])
fontforge_refsel.decomposeNestedRefs(font, True)
if not argv[1].endswith(".ufo"):
	font.buildOrReplaceAALTFeatures()

if argv[1].endswith(".sfd"):
	font.save(argv[1])
else:
	try:
		flags = ['no-mac-names', 'opentype', 'no-FFTM-table', 'no-special-null-cr']
		font.generate(argv[1], flags=tuple(flags))  # pyright: ignore[reportArgumentType]
	except ValueError:
		stderr.write("This version of Fontforge does not support 'no-special-null-cr' flag.\n")
		stderr.write("Dangling glyphs '.null' and 'nonmarkingreturn' will be present.\n")
		flags.pop()
		font.generate(argv[1], flags=tuple(flags))  # pyright: ignore[reportArgumentType]

font.close()
