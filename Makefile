# Makefile for Garamond Mono font

FONTS=GaramondMono.ttf \
      GaramondMono-Bold.ttf \
      GaramondMono-Italic.ttf \
      GaramondMono-BoldItalic.ttf
VARIABLEFONTS=GaramondMono-VF.ttf \
              GaramondMono-Italic-VF.ttf
CSS=GaramondMono.css
VFCSS=GaramondMono-VF.css
OTFONTS=${FONTS:.ttf=.otf}
WOFFFONTS=${FONTS:.ttf=.woff}
WOFF2FONTS=${FONTS:.ttf=.woff2}
VFWOFF2FONTS=${VARIABLEFONTS:.ttf=.woff2}
DOCUMENTS=README.md OFL.txt
PKGS=GaramondMono.tar.xz GaramondMono-OT.tar.xz GaramondMono-WOFF2.tar.xz GaramondMono-VF.tar.xz GaramondMono-WOFF2-VF.tar.xz
PKGCMD=rm -rf $*; mkdir $*; rsync -R $^ $*

.PHONY: all
all: ttf otf woff2 vf vf-woff2

.SUFFIXES: .sfd .ttf .otf .woff .woff2 .ufo

.sfd.ttf .sfd.otf .sfd.woff .sfd.woff2 .sfd.ufo:
	for i in $?; do ./makefont.py $@ $$i; done

GaramondMono-VF.ttf: GaramondMono-VF.designspace GaramondMono.ufo GaramondMono-Bold.ufo
	fontmake -m $< -o variable --output-path $@

GaramondMono-Italic-VF.ttf: GaramondMono-Italic-VF.designspace GaramondMono-Italic.ufo GaramondMono-BoldItalic.ufo
	fontmake -m $< -o variable --output-path $@

${VFWOFF2FONTS}: %.woff2: %.ttf
	woff2_compress $<

.DELETE_ON_ERROR: ${VFCSS}
${VFCSS}: GaramondMono-VF.css.patch ${CSS}
	patch -o $@ --no-backup-if-mismatch < $<

.PHONY: ttf otf woff woff2 vf vf-woff2
ttf: ${FONTS}
otf: ${OTFONTS}
woff: ${WOFFFONTS}
woff2: ${WOFF2FONTS}
vf: ${VARIABLEFONTS}
vf-woff2: ${VFWOFF2FONTS} ${VFCSS}

.SUFFIXES: .tar.xz .tar.gz .tar.bz2 .zip
.PHONY: dist
dist: ${PKGS}

GaramondMono.tar.xz: ${FONTS} ${DOCUMENTS}
	${PKGCMD}; tar cfvJ $@ $*
GaramondMono.tar.gz: ${FONTS} ${DOCUMENTS}
	${PKGCMD}; tar cfvz $@ $*
GaramondMono.tar.bz2: ${FONTS} ${DOCUMENTS}
	${PKGCMD}; tar cfvj $@ $*
GaramondMono.zip: ${FONTS} ${DOCUMENTS}
	${PKGCMD}; zip -9r $@ $*

GaramondMono-OT.tar.xz: ${OTFONTS} ${DOCUMENTS}
	${PKGCMD}; tar cfvJ $@ $*
GaramondMono-OT.tar.gz: ${OTFONTS} ${DOCUMENTS}
	${PKGCMD}; tar cfvz $@ $*
GaramondMono-OT.tar.bz2: ${OTFONTS} ${DOCUMENTS}
	${PKGCMD}; tar cfvj $@ $*
GaramondMono-OT.zip: ${OTFONTS} ${DOCUMENTS}
	${PKGCMD}; zip -9r $@ $*

GaramondMono-WOFF2.tar.xz: ${WOFF2FONTS} ${CSS} ${DOCUMENTS}
	${PKGCMD}; tar cfvJ $@ $*
GaramondMono-WOFF2.tar.gz: ${WOFF2FONTS} ${CSS} ${DOCUMENTS}
	${PKGCMD}; tar cfvz $@ $*
GaramondMono-WOFF2.tar.bz2: ${WOFF2FONTS} ${CSS} ${DOCUMENTS}
	${PKGCMD}; tar cfvj $@ $*
GaramondMono-WOFF2.zip: ${WOFF2FONTS} ${CSS} ${DOCUMENTS}
	${PKGCMD}; zip -9r $@ $*

GaramondMono-VF.tar.xz: ${VARIABLEFONTS} ${DOCUMENTS}
	${PKGCMD}; tar cfvJ $@ $*
GaramondMono-VF.tar.gz: ${VARIABLEFONTS} ${DOCUMENTS}
	${PKGCMD}; tar cfvz $@ $*
GaramondMono-VF.tar.bz2: ${VARIABLEFONTS} ${DOCUMENTS}
	${PKGCMD}; tar cfvj $@ $*
GaramondMono-VF.zip: ${VARIABLEFONTS} ${DOCUMENTS}
	${PKGCMD}; zip -9r $@ $*

GaramondMono-WOFF2-VF.tar.xz: ${VFWOFF2FONTS} ${VFCSS} ${DOCUMENTS}
	${PKGCMD}; tar cfvJ $@ $*
GaramondMono-WOFF2-VF.tar.gz: ${VFWOFF2FONTS} ${VFCSS} ${DOCUMENTS}
	${PKGCMD}; tar cfvz $@ $*
GaramondMono-WOFF2-VF.tar.bz2: ${VFWOFF2FONTS} ${VFCSS} ${DOCUMENTS}
	${PKGCMD}; tar cfvj $@ $*
GaramondMono-WOFF2-VF.zip: ${VFWOFF2FONTS} ${VFCSS} ${DOCUMENTS}
	${PKGCMD}; zip -9r $@ $*

.PHONY: clean
clean:
	-rm -f ${FONTS} ${OTFONTS} ${WOFFFONTS} ${WOFF2FONTS} ${VARIABLEFONTS} ${VFWOFF2FONTS}
	-rm -f ${VFCSS}
	-rm -rf ${FONTS:.ttf=.ufo}
	-rm -rf ${PKGS} ${PKGS:.tar.xz=} ${PKGS:.tar.xz=.tar.bz2} \
	${PKGS:.tar.xz=.tar.gz} ${PKGS:.tar.xz=.zip}
