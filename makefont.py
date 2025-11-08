#!/usr/bin/env fontforge

import fontforge, psMat
from sys import argv

def decomposeNestedRefs(font):
	while True:
		nestedRefsFound = False
		for glyph in font.glyphs():
			decomposedRef = []
			for ref in glyph.references:
				(srcglyph, matrix, _) = ref
				if len(font[srcglyph].references) > 0:
					print("Glyph " + glyph.glyphname + " has a nested reference to " + srcglyph)
					for srcref in font[srcglyph].references:
						decomposedRef += [(srcref[0], psMat.compose(srcref[1], matrix), False)]
					nestedRefsFound = True
				else:
					decomposedRef += [ref]
			glyph.references = tuple(decomposedRef)
		if not nestedRefsFound:
			break

font = fontforge.open(argv[2])
decomposeNestedRefs(font)
font.buildOrReplaceAALTFeatures()

if argv[1].endswith(".sfd"):
	font.save(argv[1])
else:
	font.generate(argv[1], flags=('no-mac-names','opentype'))

font.close()
