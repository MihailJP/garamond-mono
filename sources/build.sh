#!/bin/sh

rm -rf ../build
for i in ../fonts/ttf/*; do
	rm -rf $i
done
mkdir ../build

for i in *.sfd; do
	ufo=../build/${i%sfd}ufo
	ttf=../fonts/ttf/${i%sfd}ttf
	otf=../fonts/otf/${i%sfd}otf
	sfd2ufo $i $ufo

	sed -i~ -f - <<EOS $ufo/fontinfo.plist
/<key>versionMinor<\/key>/ {
n
n
s/^/<key>openTypeNameVersion<\/key>\n\
  <string>$(grep "^Version: " $i | sed -e "s/^Version: //")<\/string>\n\
  <key>postscriptIsFixedPitch<\/key>\n\
  <true\/>/
}
EOS

	fontmake -u $ufo -o ttf -f --output-path $ttf
	fontmake -u $ufo -o otf -f --output-path $otf
	woff2_compress $ttf && mv ${ttf%ttf}woff2 ../fonts/webfonts
done

rm -rf ../build
