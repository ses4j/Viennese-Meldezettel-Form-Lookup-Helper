#!/usr/bin/python
# -*- coding: utf-8 -*-

on_website = False
if on_website:
    SCRIPT_DIR = '.' # enter absolute filepath to directory where melde.py is
else:
    SCRIPT_DIR = '.'
    
import cgi,sys,os,time

print "Content-Type: text/html"     # HTML is following
print                               # blank line, end of headers

print """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml">
<head>

<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<title>Viennese Meldezettel Form Lookup Helper</title>
</head>
<body>
<h1>Viennese Meldezettel Form Lookup Helper</h1>
"""

sys.path.append(SCRIPT_DIR)
import melde

def ucgiprint(inline='', unbuff=False, encoding='UTF-8'):
     """Print to the stdout.
     Includes keywords to define the output encoding
     (UTF-8 default, set to None to switch off encoding)
     and also whether we should flush the output buffer
     after every write (default not).
     """
     line_end = '\r\n'
     if encoding:
         inline = inline.encode(encoding)
         # prob. not necessary as line endings will be the
         # same in most encodings
         line_end = line_end.encode(encoding)
     sys.stdout.write(inline)
     sys.stdout.write(line_end)
     if unbuff:
         sys.stdout.flush()

def formatCode(s):
    res = u''
    for section in s:
        res += "<sub>" + ",".join([str(c) for c in section[:-1]]) + "</sub>"
        #~ for c in :
            #~ res += str(c)
        #~ res += "</sub>"
        res += str(section[-1]) + " "
    return res

def printTable(meldename, database, header = "Unnamed header"):
    results = melde.findPossibleFilms(meldename, database)
    ucgiprint(u"<h2>%s</h2>" % header)
    ucgiprint(u"<table width='750px'> <tr><th width='50px'>Score</th><th width='250px'>1<sup>st</sup> surname on film</th><th width='250px'>(index) film number</th><th width='200px'>code</th></tr>")
    for (score, meldename, index) in sorted(results, reverse=True):
        ucgiprint(u"<tr><td>%.1f%%</td><td>%s</td><td>(%d) %s</td><td>%s</td></tr>" % (score, meldename.name, index, meldename.film, formatCode(meldename.code)))
    ucgiprint(u"</table>")

form=cgi.FieldStorage()

if on_website:
    searchName = form.getfirst("name", None)
else:
    searchName = form.getfirst("name", u"Schächter")  # test code
encoding = form.getfirst("_charset_", "UTF-8")
if searchName:
    searchName = searchName.decode(encoding)

print """
<p>Please type in the surname you're hoping to find records of in the Meldezettel (m\xc3\xa4nnliche und weibliche Personen), 1850-1928</p>

<p>According to the microfilm listing, the Meldezettel are POPULATION REGISTERS for individual residents of the city of Vienna, Austria.
The cards include name, birth date and place,
marital status, old and new places of residence, dates of arrival and departure. Occasionally the name of spouse and children
are listed. Most records range from 1890 to 1925. The beginning name on each microfilm is shown. The same name may also appear
on the preceeding microfilm. All male (m\xc3\xa4nnliche) names are filed first, followed by all female (weibliche) names in a separate sequence.</p>

<p>The form will return a list of suggested FHL form numbers you can try and order
from any Family History Library branch or from the Salt Lake HQ.</p>

<hr />
<p>
If you have suggestions for improvements, examples or counterexamples of the results, or
just want to say hi, contact me at
<img style="vertical-align: bottom;" src="http://www.scopiebreskford.com/tng/email.png" alt="&lt;email address image&gt;" />.</p>

<hr/>
<div>
<form action="meldezettel.cgi" method="get">
<label for="name">Surname:</label> <input type="text" name="name" id="name" />
<input name="" value="Search" type="submit" />
<input type="hidden" name="_charset_" />
</form>
</div>
"""

if searchName is not None:
    from melde import Meldename
    meldename = melde.Meldename(searchName)

    logline = " ".join([
        time.strftime("%x %X %Z", time.localtime()),
        os.environ['REMOTE_ADDR'], 
        searchName, 
        os.environ['HTTP_ACCEPT_LANGUAGE']
    ])
    open('meldezettel.log', 'a').write(logline + '\n')
    #~ print "<h2>Search Results for: </h2><ul><li>Name: %s</li><li>Code: %s</li></ul>" % (meldename.name, formatCode(meldename.code))
    #~ if not on_website:
    # print "name type" , type(meldename.name)
    # print type( formatCode(meldename.code))
    title = u"<h2>Search Results for: %s (code %s) </h2>" % (meldename.name, formatCode(meldename.code))
    ucgiprint(title)

    mann_database = melde.readFromDatabase(SCRIPT_DIR + '/melde_mann.html')
    printTable(meldename, mann_database, "Mannliche (male) Forms")

    weib_database = melde.readFromDatabase(SCRIPT_DIR + '/melde_weib.html')
    printTable(meldename, weib_database, "Weibliche (female) Forms")

print """<h2>Description of Organization of Meldezettel Films</h2>
The Meldezettel forms are in a distinctly non-trivial order.  I don't know if it was
intended to challenge future genealogists or if the organizer enjoyed brainteasers or what,
but it's a hassle.  It's "explained" on the film like this (exceprted from the <a href="http://www.familysearch.org/Eng/Library/fhlcatalog/supermainframeset.asp?display=titledetails&amp;columns=*%2C0%2C0&amp;titleno=176296&amp;disp=Meldezettel+(m%C3%A4nnliche+und+weibli++">FHL catalog</a>):
<blockquote>PHONETIC FILING ORDER OF NAMES: An unusually complex system was used for filing surnames. This system
files letters of the alphabet in a different sequence than usual. The following instructions are recommended to
help locate the surname you are seeking in these files. Here are described the values of the letters of the
alphabet, and their unusual filing orders. THE ALPHABET: (A), (Au), (E, \xc3\x84, \xc3\x96), (Ei, Eu, Ej, Ey, Ai, Aj, Ay),
(I, Ie, J, \xc3\x9c, Y), (O, Ou), (U), (B, P), (C, G, K, Q, X, Ch, Ck, Cs, Cz, Ks), (D, T, Th), (F, V, W), (H), (L), (M),
(N, Nck, Ng, Nk), (R), (S, Sch, Sz, Cz, Tsch, Tz, Z). Note that all vowels are filed before the consonants,
rather than in their normal alphabetic sequence. Letters or combinations of letters within the same parenthesis
are used interchangeably and thus not regarded as different in filing. Each of the letters or combination of
letters occupy one space in the filing sequence. Names beginning with vowels are filed by the first vowel sound,
and then by the next vowel sound if present, and then by the first consonant sound. They are then filed by the
second consonant sound grouped in order first by the vowels preceding the second consonant. Names with no vowels
preceding the second consonant are filed following those that have vowels between the first and second consonants.
This pattern continues until the end of the word, filing by each consonant, first running through all the vowels
preceding that consonant. Names beginning with consonants are filed together with their sound-alike group. After
the first consonant sound, names are filed by the second consonant sound grouped in order first by all of the
vowels preceding the second consonant. Names with no vowel preceding the second consonant are filed following
those that have vowels between the consonants. This pattern continues for the entire name.</blockquote>

<h2>Internal Index Table</h2>
<div>The above character listing has been expanded experimentally to the
following list.  The number to the left of each character set is used
as a "representative" for the codes above.  Vowel codes are subscripted to indicate
their grouping with the subsequent consonant.</div>

<ol>
"""

for i,char_row in enumerate(melde.chars[:-1]):
    if i == 7:
        print "<li>(placeholder appended to vowels without a following consonant)</li>"
    else:
        print "<li>%s</li>"% (char_row)
print """
</ol>

<h2>Other Meldezettel Links</h2>
<ul>
<li>
<a href="http://freepages.genealogy.rootsweb.ancestry.com/~pnlowe/meldezettel.htm">Peter Lowe's excellent description of the Meldezettel</a></li>
</ul>
</p>

<hr />
<p align='center'>Return to <a href="/tng">Stafford Genealogy Home</a>.</p>
<hr />
<p align='center'>(C) Scott Stafford 2008-2011</p>
<div align='center'>
<a href="http://validator.w3.org/check?uri=referer"><img
src="http://www.w3.org/Icons/valid-xhtml10-blue"
        alt="Valid XHTML 1.0 Transitional" height="31" width="88" /></a>
</div>

<script type="text/javascript">
var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
document.write(unescape("%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'%3E%3C/script%3E"));
</script>
<script type="text/javascript">
var pageTracker = _gat._getTracker("UA-144058-2");
pageTracker._initData();
pageTracker._trackPageview();
</script>

</body>
</html>
"""
