# Makefile for Garamond Mono font

FONTS=GaramondMono.ttf \
      GaramondMono-Bold.ttf \
      GaramondMono-Italic.ttf \
      GaramondMono-BoldItalic.ttf
OTFONTS=${FONTS:.ttf=.otf}
DOCUMENTS=README.md OFL.txt
PKGS=GaramondMono.tar.xz GaramondMono-OT.tar.xz
FFCMD=for i in $?;do fontforge -lang=py -c "font=fontforge.open('$$i'); font.generate('$@', flags=('opentype','no-mac-names')); font.close()";done
TTFPKGCMD=rm -rf $*; mkdir $*; cp ${FONTS} ${DOCUMENTS} $*
OTFPKGCMD=rm -rf $*; mkdir $*; cp ${OTFONTS} ${DOCUMENTS} $*

.PHONY: all
all: ttf otf

.SUFFIXES: .sfd .ttf .otf

.sfd.ttf:
	${FFCMD}
.sfd.otf:
	${FFCMD}

.PHONY: ttf otf
ttf: ${FONTS}
otf: ${OTFONTS}

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

.PHONY: clean
clean:
	-rm -f ${FONTS} ${OTFONTS}
	-rm -rf ${PKGS} ${PKGS:.tar.xz=} ${PKGS:.tar.xz=.tar.bz2} \
	${PKGS:.tar.xz=.tar.gz} ${PKGS:.tar.xz=.zip}
