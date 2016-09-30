# -*- coding: utf-8 -*-

""" melde.py contains library methods for comparing and sorting Viennese Meldezettel-sorted words. """

import sys
import os
import math

"""
NOTE: Replace silent letters like 'h' with 'b'  Like Schuh is Schup.
Replace soft 's' sounds like the c in Soucek (and apparently in Syckovo) with 's', not 'c'.

TODO: Fix index.  Some obvious issues:
Sachari should be Pachari or something.
"""

import re

# verbose can be set to True for debug/testing printouts
verbose = False

# 'chars' contains a tuple of strings, where each element is a space-delimited collection
# of "identical" characters as far as the sorting algorithm is concerned.
chars = (
    'A a \xc3\xa1 \xc3\x81 \xc3\xa0 \xc7\x8e \xc3\xa3',  # á
    'Au au',
    'E \xc3\x84 \xc3\x96 e ee aye aie \xc3\xa4 \xc3\xb6 \xc4\x9a \xc4\x9b \xc3\xa9 \xc3\xaa',  # e
    'Ei Eu Ej Ey Ai Aj Ay ei ey eu ej ai aj ay',
    'i ie j y \xc3\xbc \xc3\x9c \xc3\xad \xc3\xbd',
    'o oe ou \xc3\xb3 \xc5\x91',  # ő
    'u \xc3\xba \xc5\xad \xc5\xb1',  # c5 b0 ű
    '',  # placeholder for ALLVOWELS
    '',
    'I Ie J Y',
    'O Oe Ou',
    'U',
    'B P b p pp',  # added pp
    'C G K Q X Ch Ck Cs Cz Ks Chs c g k q x ch ck cs cz ks chs \xc4\x86 \xc4\x87 \xc4\x8d \xc4\x8c',  # added chs, \xc4\x87
    'D Dh T Th d dh t th dt Tsch',
    'Ph F V W f v w',
    'H h',
    'L l hl',
    'M m',
    'N Nck Ng Nk n nck ng nk nn Å„',
    'R r hr \xc5\x99',
    'S Sh Sch Sz Tz s sch sz tsch tz \xc3\x9f \xc5\xbd \xc5\xbe \xc5\xa0 \xc5\xa1 \xc5\x9b \xc5\xba st ss',  # \xc3\x9f (sharp s) ž
    'St',
    'Z z dz ds',
    ', ( ) ! \xca\xb9 \' \xcc\xae ^ \xef\xb8\xa1 : - .'  # ???
)

char_map = {}
for i, charline in enumerate(chars):
    for c in charline.split():
        char_map[c.decode('utf8')] = i + 1

if verbose:
    print char_map

keys_by_length = {}
for k, v in char_map.iteritems():
    try:
        keys_by_length[len(k)].append((k, v),)
    except KeyError:
        keys_by_length[len(k)] = [(k, v)]

if verbose:
    print keys_by_length

superverbose = False


def codify(name):
    """ Accept a unicode string and return a list of ints representing each 
    character in the "meldezettel canonical" way. 
    """
    #~ ### a hack because starting Cz's seem to be soft, not hard.
    #~ if n.startswith("Cz"):
    #~ print "did something",n
    #~ n = "S" + n[2:]
    #~ print n

    assert(type(name) == unicode)

    # print "[codify]", name.encode('latin-1', 'replace')
    for key in sorted(keys_by_length.keys(), reverse=True):
        for k, v in keys_by_length[key]:
            if superverbose and name != name.replace(k, " %d " % v):
                #~ print "key",key
                print "key", k.encode('latin-1', 'replace'), "value", v, "name", name.encode('latin-1', 'replace'), type(k), type(v), type(name)
            name = name.replace(k, " %d " % v)
    try:
        simplified = [int(x) for x in name.split()]
    except (UnicodeEncodeError, ValueError):
        print "bad name:",
        for c in name:
            print ord(c),
        print "len", len(name)
        print "in latin-1:", name.encode('latin-1', 'replace')
        print "in utf-8:", name.encode('utf-8', 'replace')
        raise
    final = []
    accum = []
    for s in simplified:
        accum.append(s)
        if not vowel(s):
            final.append(accum)
            accum = []

    if len(accum) > 0 and len(final) == 0:
        # this is a hack, for "Aue" or other no-vowels.
        # make it the lowest-possible consonant.
        final.append(accum + [8])
        accum = []
    return final


def vowel(c):
    """ Return true if the input character 'c' is a Meldezettel vowel. """
    return c <= 7


class Meldename:
    """ An object representing one Meldezettel name that can be compared/sorted
    with others of its kind. """

    def __init__(self, name, film=None):
        self.name = name.capitalize()
        self.code = codify(self.name)
        self.film = str(film)

    def __cmp__(self, other):
        # <0 if self < other
        # 0 if ==
        # >0 if self > other
        #~ verbose = True
        if verbose:
            print "comparing self<other", self, other, " = "

        self_starting_vowels = self.code[0][:-1]
        other_starting_vowels = other.code[0][:-1]

        if len(self_starting_vowels) > 0 and len(other_starting_vowels) == 0:
            if verbose:
                print "left starts with vowels", -1
            return -1
        elif len(self_starting_vowels) == 0 and len(other_starting_vowels) > 0:
            if verbose:
                print "right starts with vowels:", 1
            return 1
        elif len(self_starting_vowels) > 0 and len(other_starting_vowels) > 0:
            # this is harder... ?
            if verbose:
                print "both start with vowels"
            for i, j in zip(self_starting_vowels, other_starting_vowels):
                cmp = i.__cmp__(j)
                if cmp != 0:
                    if verbose:
                        print "but", i, "and", j, "compared", cmp
                    return cmp
            cmp = len(self_starting_vowels).__cmp__(len(other_starting_vowels))
            if cmp != 0:
                if verbose:
                    print "but are different lengths:", cmp
                return cmp
            cmp = self.code[0][-1].__cmp__(other.code[0][-1])
            if cmp != 0:
                if verbose:
                    print "but have different consonants:", cmp
                return cmp

            #~ for ctr,i in enumerate(self.code[0][:min(len(self_starting_vowels), len(other_starting_vowels))]): # if it starts with vowels, iterate thru the vowels..

                #~ if verbose: print "...",self.code[0][:-1]
                #~ if verbose: print ctr,i,self.code[0][ctr]
                #~ cmp = i.__cmp__(other.code[0][ctr])
                #~ if cmp != 0:
                #~ if verbose: print "by initial vowels,",cmp
                #~ return cmp
            #~ # if I'm here, all
            #~ return

        for i, j in zip(self.code, other.code):
            if verbose:
                print i, j
            cmp = i[-1].__cmp__(j[-1])
            if cmp != 0:
                if verbose:
                    print "by consonants,", cmp
                return cmp

            if i < j:
                if verbose:
                    print self.name
                return -1
            elif i > j:
                if verbose:
                    print other.name
                return 1

        cmp = len(self.code).__cmp__(len(other.code))
        if cmp != 0:
            if verbose:
                print "Identical beginnings, but one is longer: ", cmp
        #~ print "almost same...",cmp
        return cmp

    def __str__(self):
        return "%15s/<%s>" % (self.name.encode('latin-1', 'replace'), " ".join(["-".join([str(a) for a in x]) for x in self.code]))


def userSpecifiedList(m="Schechter Scheschter Schatz Schitsch Schisscher Schuster Schuts Scheis"):
    M = [Meldename(a) for a in m.split()]
    #~ print M
    M.sort()
    #~ print M
    print "-----"
    for i, a in enumerate(M):
        for j, b in enumerate(M[i + 1:]):
            assert a <= b
    print "-----NOW!!!"
    print m
    return "\n".join([str(a) for a in M])


def testOrderedSetForConsistency(meldeinput):
    testCorrect = 0
    testCount = 0
    for i, a in enumerate(meldeinput):
        for b in meldeinput[i + 1:]:
            testCount += 1
            try:
                if not (a < b):
                    if verbose:
                        print "ERROR!!", a, "should be < than", b
                else:
                    testCorrect += 1
                    #~ raise AssertionError
            except ValueError:
                print a, b
                #~ print "Goo!!",a.encode('utf-8'),b.encode('utf-8')

                raise
    #~ print "correct",testCorrect
    print "incorrect %d / %d (%f correct)" % (testCount - testCorrect, testCount, float(testCorrect) / testCount)

#~ assert Meldename('Adlerblum') < Meldename('Borhowski')
#~ assert Meldename('Achs') < Meldename('Ebhart')
#~ print Meldename('Aue')# < Meldename('Appelt')
#~ print Meldename('Appelt')# < Meldename('Appelt')
#~ sys.exit(0)

import cPickle
regex = "<TR VALIGN=\'TOP\'\>.+?SIZE='2'>\s*([^<]*)\s*</FONT>.+?SIZE='2'>\s*(.+?)\s*</FONT>"


def writeToDatabase(filename):
    source = unicode(open(filename).read(), 'utf8')
    input = re.findall(regex, source, re.DOTALL | re.UNICODE)
    input = [(i.strip(), j.replace('<BR>\n', '')) for (i, j) in input]
    meldeinput = [Meldename(a[0], a[1]) for a in input]
    cPickle.dump(meldeinput, open(filename + '.p', 'wb'), 2)


def writeToDatabaseFromJson(filename):
    def cleanName(n):
        return n.split(',')[0]

    def add(names, n, location):
        if n == '????':
            return
        names.append(Meldename(cleanName(n), location))

    # source = unicode(open(filename).read(), 'utf8')
    # input = re.findall(regex, source, re.DOTALL | re.UNICODE)
    import json

    source = json.load(open(filename))
    # input = [(i.strip(), j.replace('<BR>\n', '')) for (i, j) in input]

    meldeinput = []
    for item in source['film_note']:
        filmno = item['filmno'][0]
        geo_collection = item['geo_collection'][0]
        shelf = item['shelf'][0]
        location = item['location'][0]
        text = item['text'][0]

        if text.lower().startswith("meldezettel"):
            print "SKIPPED", text.encode('utf8', 'replace')
            continue
        name = text
        location = "{}, {} {} {}".format(location, geo_collection, shelf, filmno)
        # print name.encode('utf8', 'replace'), "---", location.encode('utf8', 'replace')
        if ' - ' in name:
            names = name.split(' - ')
            assert len(names) == 2 or names[0].startswith('Huper') or names[0].startswith('Horasch')

            add(meldeinput, names[0], location)
            add(meldeinput, names[1], location)
        else:
            add(meldeinput, name, location)

    cPickle.dump(meldeinput, open(filename + '.p', 'wb'), 2)


def readFromDatabase(filename):
    return cPickle.load(open(filename + '.p', 'rb'))


def findPossibleFilms(newName, database, verbose=False):
    results = []
    if not isinstance(newName, Meldename):
        newMeldename = Meldename(newName)
    else:
        newMeldename = newName

    if verbose:
        print "You should look for"
    if verbose:
        print newMeldename
    if verbose:
        print "in these files...."

    lessThans = []
    for i, row in enumerate(database[:-1]):
        lessThans.append(int(row <= newMeldename))

    def mean(seq):
        return float(sum(seq)) / len(seq)

    POINT_VALUES = (2.0, 2.0, 3.0, 4.0, 10.0), (5.0, 4.0, 3.0, 2.0, 2.0)
    POINT_VALUE_MAX = sum(POINT_VALUES[0]) + sum(POINT_VALUES[1])
    for i in range(len(lessThans)):
        lessRange = lessThans[max(0, i - len(POINT_VALUES[0]) + 1):i + 1]
        greaterRange = lessThans[i + 1:i + len(POINT_VALUES[1]) + 1]
        if verbose:
            print i, lessThans[i], lessRange, greaterRange, database[i], mean(lessRange)

        if len(greaterRange) == 0:
            # assume there's one more at the end of the list that's > than me
            greaterRange = [0]
        if len(lessRange) == 0:
            lessRange = [1]  # assume one at the beginning that's < than me.
        if mean(lessRange) > 0.0 and mean(greaterRange) < 1.0:
            score = 0.0
            score += sum([lessRange[v] * POINT_VALUES[0][len(POINT_VALUES[0]
                                                             ) - len(lessRange) + v] for v in range(len(lessRange))])
            if verbose:
                print score,
            score += sum([(1 - greaterRange[v]) * POINT_VALUES[1][v]
                          for v in range(len(greaterRange))])
            score = score * 100.0 / POINT_VALUE_MAX
            if verbose:
                print score,
            results.append((score, database[i], i))
            if verbose:
                print "Score: %.1f" % score, "Between", database[i], "and", database[i + 1]

    return results


def testEquivalenceOfEachPair(database):
    for i, row in enumerate(database[:-1]):
        for row2 in database[i + 1:]:
            if (row < row2) == (row2 < row):
                if row.code == row2.code:
                    print row, row2, "actually identical"
                else:
                    print row, row2, "are both", (row < row2)
                    sys.exit(1)


def scoreComparisonAlgorithm(database):
    db2 = []
    for i, row in enumerate(database):
        db2.append((row, i))
    db2.sort()

    distance = []
    for i, row in enumerate(db2):
        distance.append(i - row[1])

    scoresum = sum([math.fabs(d) for d in distance])
    scoreavg = scoresum / len(distance)
    scoremax = max([math.fabs(d) for d in distance])
    scoremedian = sorted([math.fabs(d) for d in distance])[len(distance) / 2]
    return "sum", scoresum, "avg", scoreavg, "max", scoremax, "median", scoremedian


def findProblemAreas(database, threshold=20):
    db2 = []
    for i, row in enumerate(database):
        db2.append((row, i))

    db2.sort()

    db3 = []
    for sorted_idx, (row, original_idx) in enumerate(db2):
        db3.append((original_idx, sorted_idx, row))
    db3.sort()

    problems = []
    for (original_idx, sorted_idx, meldename) in db3:
        # iterate in the original order.
        distance = math.fabs(original_idx - sorted_idx)
        if distance > threshold:
            problems.append((original_idx, sorted_idx, meldename))
            for (original_idx2, sorted_idx2, meldename2) in db3[original_idx - 2:original_idx + 3]:
                print "%5d %5d %s" % (original_idx2, sorted_idx2 - original_idx2, meldename2)
            print "----"

            #~ print "%5d %5d %s" % (i,row[1],row[0])
    print "num over threshold (%d): %d" % (threshold, len(problems))
    return problems

if __name__ == '__main__':
    """ Everything in here is just messy code trying out various tests. """
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

    #~ print scoreComparisonAlgorithm([1.0, 2.0, 3.0, 2.9])
    #~ print scoreComparisonAlgorithm([1.0, 2.0, 3.0, 2.9, 6.0])
    #~ print scoreComparisonAlgorithm([1.0, 3.0, 2.0, 4.0, 0.1])
    #~ sys.exit(1)
    #~ print "Weiblich"
    #~ changeAlgo = True
    changeAlgo = False

    if changeAlgo:
        writeToDatabaseFromJson(SCRIPT_DIR + '/melde_1930.json')
        # writeToDatabase(SCRIPT_DIR + '/melde_weib.html')
        # writeToDatabase(SCRIPT_DIR + '/melde_mann.html')

    m1930_database = readFromDatabase(SCRIPT_DIR + '/melde_1930.json')
    weib_database = readFromDatabase(SCRIPT_DIR + '/melde_weib.html')
    mann_database = readFromDatabase(SCRIPT_DIR + '/melde_mann.html')
    if changeAlgo:
        #~ weib: ('sum', 30698.0, 'avg', 22.891871737509323, 'max', 1161.0, 'median', 10.0)
        #~ mann: ('sum', 31232.0, 'avg', 16.737406216505896, 'max', 1291.0, 'median', 5.0)        #~ incorrect 19377 / 898470 (0.978433 correct)
        #~ incorrect 22459 / 1740045 (0.987093 correct)
        #~ print "weib:",scoreComparisonAlgorithm(weib_database)
        print "1930:",
        print scoreComparisonAlgorithm(m1930_database)
        print "mann:",
        print scoreComparisonAlgorithm(mann_database)
        print "weib:",
        print scoreComparisonAlgorithm(weib_database)
        #~ testOrderedSetForConsistency(weib_database)
        #~ testOrderedSetForConsistency(mann_database)
        sys.exit(0)
    elif 0:
        for row in sorted(mann_database, reverse=True):
            lastFilm = row.film
            print row.film, row.name.encode('utf8', 'replace')

    #~ f = open('aliases.txt','w')
    #~ for problem in findProblemAreas(mann_database):
        #~ f.write( (unicode(problem[0]) + ',' + problem[2].name + ',\n').encode('utf8') )
    #~ print Meldename('Schicho') < Meldename('Schick')
    #~ sys.exit(0)
    #~ print Meldename('Adler') #< Meldename('Zlatack')
    #~ print Meldename('Adlerblum') #< Meldename('Zlatack')

    #~ testEquivalenceOfEachPair(weib_database)

    #~ for r in res:
        #~ print r[0], r[1].name.encode('utf8', 'xmlcharrefreplace'), r[1].code

    #~ print "Mannlich"

    #~ name = "Schechter"
    #~ res = findPossibleFilms(name, weib_database)

    def printPossibleFilms(res):
        print "\n".join(["%.2f %s     %s " % (r[0], r[1], r[1].film) for r in sorted(res, reverse=True)])

    def possibles(name, db, verbose=False):
        print " --- ", name, " --- "
        res = findPossibleFilms(name, db, verbose)
        printPossibleFilms(res)
        print Meldename(name)

    possibles(u"Zudtssch", m1930_database, verbose=False)

    sys.exit(0)
    #~ print userSpecifiedList('Schester Schreiber Schreiner Schrott Sruba Sautschek Schestorad Susskind')
    #~ print userSpecifiedList('Schechter Sobetka Schober Schubk Schubacz Schubert')
    #~ print userSpecifiedList('Schechter Sporer Springinsfeld Sachs Shachien Sauka Sekanina Secher Schicho')
    #~ print userSpecifiedList('Schechter Sagina Schachinger Szekely Nordenheim Siokola')
    sys.exit(0)
    print "Weib"
    name = sys.argv[1]
    res = findPossibleFilms(name, weib_database)
    for r in res:
        print r[0], r[1].name.encode('utf8', 'xmlcharrefreplace'), r[1].code

    print
    print "Mann"
    res = findPossibleFilms(name, mann_database)
    for r in res:
        print r[0], r[1].name.encode('utf8', 'xmlcharrefreplace'), r[1].code
