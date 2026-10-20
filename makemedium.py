#!/usr/bin/env python3
"""Derive Garamond Mono Medium (weight 500) from a built Regular or Italic.

Usage: makemedium.py OUTPUT INPUT

INPUT is GaramondMono or GaramondMono-Italic in any built format (.ttf, .otf,
.woff, .woff2); OUTPUT is written in the same format.

The Regular and Bold outlines are not point-compatible, so the Medium cannot be
interpolated. Instead each Regular stem is thickened horizontally by OFFSET
units on each side (70 -> 88 units; Bold is 131). Widening only sideways keeps
the baseline, x-height, cap height and advance widths exact, and leaves the
hairlines thin.

A glyph whose separate parts would touch at that offset, such as an accent
and its dots, is thickened by the largest offset that keeps them apart.

The thickened outline is the union of the glyph swept from -OFFSET to +OFFSET.
Skia path operations do this for most glyphs and booleanOperations for the
rest. Each result is rasterised and compared against the original raster
dilated by the same amount; a glyph is accepted only when the two agree to
within a pixel at every edge, and the
script fails rather than write a font with a glyph it could not verify.
Composite glyphs are kept as composites of thickened components unless
their components would touch; then they are decomposed and treated alike.
"""

from sys import argv, exit, stderr

import numpy as np
import pathops
from booleanOperations.booleanGlyph import BooleanGlyph
from fontTools.pens.areaPen import AreaPen
from fontTools.pens.basePen import BasePen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.freetypePen import FreeTypePen
from fontTools.pens.recordingPen import DecomposingRecordingPen, RecordingPen
from fontTools.pens.reverseContourPen import ReverseContourPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import ttProgram

OFFSET = 9
FAMILY = "Garamond Mono"
WEIGHT_CLASS = 500
PANOSE_MEDIUM = 6


class CubicPen(BasePen):
	"""Pass outlines on with quadratic curves raised exactly to cubics.

	booleanOperations rejects quadratic segments; BasePen does the conversion.
	"""

	def __init__(self, other):
		super().__init__(None)
		self.other = other

	def _moveTo(self, pt):
		self.other.moveTo(pt)

	def _lineTo(self, pt):
		self.other.lineTo(pt)

	def _curveToOne(self, pt1, pt2, pt3):
		self.other.curveTo(pt1, pt2, pt3)

	def _closePath(self):
		self.other.closePath()

	def _endPath(self):
		self.other.endPath()


def shifted(glyph, pen, dx):
	glyph.draw(CubicPen(TransformPen(pen, (1, 0, 0, 1, dx, 0))))


def raster(draw, box):
	x0, y0, x1, y1 = box
	pen = FreeTypePen(None)
	draw(pen)
	return pen.array(width=x1 - x0, height=y1 - y0, transform=(1, 0, 0, 1, -x0, -y0)) > 0.5


def dilate(coverage, radius):
	out = coverage.copy()
	for step in range(1, radius + 1):
		out[:, step:] |= coverage[:, :-step]
		out[:, :-step] |= coverage[:, step:]
	return out


def agrees(got, expected):
	"""True when each raster lies within one pixel of the other.

	Antialiasing can flip a one-pixel sliver along a long diagonal edge; anything
	wider, such as a filled counter or a lost stroke, is a real error.
	"""

	def grow(a):
		out = a.copy()
		out[1:, :] |= a[:-1, :]
		out[:-1, :] |= a[1:, :]
		wide = out.copy()
		wide[:, 1:] |= out[:, :-1]
		wide[:, :-1] |= out[:, 1:]
		return wide

	return not np.any(got & ~grow(expected)) and not np.any(expected & ~grow(got))


def sweep_pathops(glyph, offset):
	acc = pathops.Path()
	shifted(glyph, acc.getPen(), -offset)
	acc.simplify(fix_winding=True)
	for dx in range(-offset + 1, offset + 1):
		copy = pathops.Path()
		shifted(glyph, copy.getPen(), dx)
		acc = pathops.op(acc, copy, pathops.PathOp.UNION, fix_winding=True)
	return acc


def sweep_booleanops(glyph, offset):
	shape = BooleanGlyph()
	for dx in range(-offset, offset + 1):
		shifted(glyph, shape.getPen(), dx)
	return shape.removeOverlap()


def swept(glyph, offset, box):
	"""Return the glyph thickened by offset, verified against its raster, or None."""

	expected = dilate(raster(glyph.draw, box), offset)
	for method in (sweep_pathops, sweep_booleanops):
		try:
			shape = method(glyph, offset)
		except Exception:  # either library can give up on a glyph; try the next
			continue
		if agrees(raster(shape.draw, box), expected):
			return shape
	return None


def parts(shape):
	"""Count the separate filled parts (outer contours) of an overlap-free shape."""

	recording = RecordingPen()
	shape.draw(recording)
	areas, current = [], RecordingPen()
	for op, args in recording.value:
		getattr(current, op)(*args)
		if op in ("closePath", "endPath"):
			area = AreaPen()
			current.replay(area)
			areas.append(area.value)
			current = RecordingPen()
	if not areas:
		return 0
	outer = max(areas, key=abs) > 0
	return sum(1 for a in areas if (a > 0) == outer)


def oriented(shape, pen, clockwise):
	"""Draw shape into pen with outer contours in the direction the format expects."""

	area = AreaPen()
	shape.draw(area)
	if (area.value < 0) != clockwise:
		pen = ReverseContourPen(pen)
	shape.draw(pen)


def thicken(font, source):
	"""Thicken font's glyphs, reading the original outlines from source."""

	glyphs = source.getGlyphSet()
	is_cff = "CFF " in font
	if is_cff:
		cff = font["CFF "].cff
		top = cff[cff.fontNames[0]]
	else:
		glyf = font["glyf"]
	head = font["head"]
	box = (head.xMin - OFFSET - 20, head.yMin - 20, head.xMax + OFFSET + 20, head.yMax + 20)
	failed = []
	narrowed = []
	for name in font.getGlyphOrder():
		glyph = DecomposingRecordingPen(glyphs)
		glyphs[name].draw(glyph)
		if not glyph.value:
			continue
		glyph.draw = glyph.replay
		# Thickening must not join separate parts, such as an accent and its
		# dots. Where the full offset would, use the largest that does not.
		outline = swept(glyph, 0, box)
		shape = swept(glyph, OFFSET, box)
		if outline is None or shape is None:
			failed.append(name)
			continue
		if parts(shape) == parts(outline):
			if not is_cff and glyf[name].isComposite():
				continue  # its thickened components already draw this shape
		else:
			for offset in range(OFFSET - 1, 0, -1):
				candidate = swept(glyph, offset, box)
				if candidate is not None and parts(candidate) == parts(outline):
					narrowed.append(f"{name} ({offset})")
					shape = candidate
					break
		if is_cff:
			pen = T2CharStringPen(glyphs[name].width, glyphs)
			oriented(shape, pen, clockwise=False)
			top.CharStrings[name] = pen.getCharString(private=top.Private, globalSubrs=cff.GlobalSubrs)
		else:
			pen = TTGlyphPen(None)
			oriented(shape, Cu2QuPen(pen, max_err=1.0, reverse_direction=False), clockwise=True)
			new = pen.glyph()
			new.program = ttProgram.Program()
			new.program.fromBytecode(b"")
			glyf[name] = new
	if narrowed:
		print(f"{argv[2]}: thickened less to keep parts apart: {', '.join(narrowed)}")
	return failed


def rename(font):
	italic = font["name"].getDebugName(2) == "Italic"
	style = "Italic" if italic else "Regular"
	medium_style = "Medium Italic" if italic else "Medium"
	postscript = "GaramondMono-MediumItalic" if italic else "GaramondMono-Medium"
	version = font["name"].getDebugName(5)
	names = {
		1: f"{FAMILY} Medium",
		2: style,
		3: f"{version.removeprefix('Version ')};{postscript}",
		4: f"{FAMILY} {medium_style}",
		6: postscript,
		16: FAMILY,
		17: medium_style,
	}
	table = font["name"]
	for name_id in names:
		table.removeNames(nameID=name_id)
	for name_id, value in names.items():
		table.setName(value, name_id, 3, 1, 0x409)

	os2 = font["OS/2"]
	os2.usWeightClass = WEIGHT_CLASS
	os2.panose.bWeight = PANOSE_MEDIUM
	os2.fsSelection &= ~((1 << 5) | (1 << 6))  # clear BOLD and REGULAR
	if not italic:
		os2.fsSelection |= 1 << 6
	font["head"].macStyle &= ~1  # not bold

	if "CFF " in font:
		cff = font["CFF "].cff
		top = cff[cff.fontNames[0]]
		cff.fontNames[0] = postscript
		top.FullName = names[4]
		top.FamilyName = names[1]
		top.Weight = "Medium"


def fix_side_bearings(font):
	glyphs = font.getGlyphSet()
	hmtx = font["hmtx"]
	for name in font.getGlyphOrder():
		pen = BoundsPen(glyphs)
		glyphs[name].draw(pen)
		width, _ = hmtx[name]
		hmtx[name] = (width, round(pen.bounds[0]) if pen.bounds else 0)


if len(argv) != 3:
	print(__doc__.split("\n\n")[1], file=stderr)
	exit(2)

font = TTFont(argv[2])
failed = thicken(font, TTFont(argv[2]))
if failed:
	print(f"{argv[2]}: could not thicken {', '.join(failed)}", file=stderr)
	exit(1)
rename(font)
fix_side_bearings(font)
font.save(argv[1])
