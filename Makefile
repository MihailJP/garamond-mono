# Makefile for Garamond Mono font

FONTS=GaramondMono.ttf \
      GaramondMono-Bold.ttf \
      GaramondMono-Italic.ttf \
      GaramondMono-BoldItalic.ttf
CSS=GaramondMono.css
OTFONTS=${FONTS:.ttf=.otf}
WOFFFONTS=${FONTS:.ttf=.woff}
WOFF2FONTS=${FONTS:.ttf=.woff2}
DOCUMENTS=README.md OFL.txt
PKGS=GaramondMono.tar.xz GaramondMono-OT.tar.xz GaramondMono-WOFF2.tar.xz
FFCMD=for i in $?;do fontforge -lang=py -c "font=fontforge.open('$$i'); font.generate('$@', flags=('opentype','no-mac-names')); font.close()";done
TTFPKGCMD=rm -rf $*; mkdir $*; rsync -R ${FONTS} ${DOCUMENTS} $*
OTFPKGCMD=rm -rf $*; mkdir $*; rsync -R ${OTFONTS} ${DOCUMENTS} $*
WOFF2PKGCMD=rm -rf $*; mkdir $*; rsync -R ${WOFF2FONTS} ${CSS} ${DOCUMENTS} $*

.PHONY: all
all: ttf otf woff2

.SUFFIXES: .sfd .ttf .otf .woff .woff2

.sfd.ttf .sfd.otf .sfd.woff .sfd.woff2:
	${FFCMD}

.PHONY: ttf otf
ttf: ${FONTS}
otf: ${OTFONTS}
woff: ${WOFFFONTS}
woff2: ${WOFF2FONTS}

.SUFFIXES: .tar.xz .tar.gz .tar.bz2 .zip
.PHONY: dist
dist: ${PKGS}

GaramondMono.tar.xz: ${FONTS} ${DOCUMENTS}
	${TTFPKGCMD}; tar cfvJ $@ $*
GaramondMono.tar.gz: ${FONTS} ${DOCUMENTS}
	${TTFPKGCMD}; tar cfvz $@ $*
GaramondMono.tar.bz2: ${FONTS} ${DOCUMENTS}
	${TTFPKGCMD}; tar cfvj $@ $*
GaramondMono.zip: ${FONTS} ${DOCUMENTS}
	${TTFPKGCMD}; zip -9r $@ $*

GaramondMono-OT.tar.xz: ${OTFONTS} ${DOCUMENTS}
	${OTFPKGCMD}; tar cfvJ $@ $*
GaramondMono-OT.tar.gz: ${OTFONTS} ${DOCUMENTS}
	${OTFPKGCMD}; tar cfvz $@ $*
GaramondMono-OT.tar.bz2: ${OTFONTS} ${DOCUMENTS}
	${OTFPKGCMD}; tar cfvj $@ $*
GaramondMono-OT.zip: ${OTFONTS} ${DOCUMENTS}
	${OTFPKGCMD}; zip -9r $@ $*

GaramondMono-WOFF2.tar.xz: ${WOFF2FONTS} ${DOCUMENTS}
	${WOFF2PKGCMD}; tar cfvJ $@ $*
GaramondMono-WOFF2.tar.gz: ${WOFF2FONTS} ${DOCUMENTS}
	${WOFF2PKGCMD}; tar cfvz $@ $*
GaramondMono-WOFF2.tar.bz2: ${WOFF2FONTS} ${DOCUMENTS}
	${WOFF2PKGCMD}; tar cfvj $@ $*
GaramondMono-WOFF2.zip: ${WOFF2FONTS} ${DOCUMENTS}
	${WOFF2PKGCMD}; zip -9r $@ $*

.PHONY: clean
clean:
	-rm -f ${FONTS} ${OTFONTS} ${WOFFFONTS} ${WOFF2FONTS}
	-rm -rf ${PKGS} ${PKGS:.tar.xz=} ${PKGS:.tar.xz=.tar.bz2} \
	${PKGS:.tar.xz=.tar.gz} ${PKGS:.tar.xz=.zip}
