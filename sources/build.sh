#!/bin/sh

for i in *.sfd; do
	fontforge -lang=py -script <<EOS
import fontforge
font = fontforge.open("$i")
font.generate("../fonts/ttf/${i%sfd}ttf")
font.generate("../fonts/otf/${i%sfd}otf")
font.generate("../fonts/webfonts/${i%sfd}woff2")
font.close()
EOS
done
