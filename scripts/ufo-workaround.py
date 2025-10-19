#!/usr/bin/env python3

from sys import argv
from fontTools import ufoLib
import re

class FontInfo:
    def __init__(self):
        for key in ufoLib.fontInfoAttributesVersion2:
            self.__dict__[key] = None

(_, ufoPath, sfdPath) = argv

with open(sfdPath, 'r') as file:
    sfd = file.read()
ufo = ufoLib.UFOReaderWriter(ufoPath)

# Workaround for fontinfo.plist

m = re.search(r"^Version:\s*(.*?)$", sfd, re.M)
versionStr = None
if m:
    versionStr = m.group(1)

fontInfo = FontInfo()
ufo.readInfo(fontInfo)
if versionStr and not fontInfo.openTypeNameVersion:
    fontInfo.openTypeNameVersion = "Version " + versionStr
fontInfo.postscriptIsFixedPitch = True
ufo.writeInfo(fontInfo)

# Workaround for features.fea

features = ufo.readFeatures()

# Name ss?? features
def getOtfFeatNames(sfd, tag):
    result = {}
    p = re.compile(r"^OtfFeatName:\s*'" + tag + r"'\s+(\S+)\s+\"(.*?)\"$", re.M)
    pos = 0
    while True:
        m = p.search(sfd, pos)
        if not m:
            break
        result[int(m.group(1))] = m.group(2) # TODO: UTF-7 parser
        pos = m.start() + 1
    return result
for i in range(1, 21):
    tag = "ss" + str(i).zfill(2)
    featurePattern = re.compile(r"\bfeature\s+" + tag + r"\s*\{.*\}\s*" + tag + r"\s*;", re.S)
    m = featurePattern.search(features)
    if m:
        featureCode = m.group(0)
        n = re.search(r"\bfeatureNames\s*\{.*\}\s*;", featureCode)
        if not n:
            featureNames = getOtfFeatNames(sfd, tag)
            featureNamesCode = "    featureNames {\n"
            for lang, name in featureNames.items():
                featureNamesCode = featureNamesCode + "        name 3 1 " + hex(lang) + " \"" + name + "\";\n"
            featureNamesCode = featureNamesCode + "    };\n"
            featureCode = re.sub(r"\bfeature\s+" + tag + r"\s*\{", r"\g<0>\n" + featureNamesCode, featureCode)
            features = featurePattern.sub(featureCode, features)

ufo.writeFeatures(features)
