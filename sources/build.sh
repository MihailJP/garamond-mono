#!/bin/sh

for i in *.sfd; do
	fontforge -lang=ff -script <<EOS
Open("$i")
Generate("../fonts/ttf/${i%sfd}ttf")
Generate("../fonts/otf/${i%sfd}otf")
Generate("../fonts/webfonts/${i%sfd}woff2")
Close()
EOS
done