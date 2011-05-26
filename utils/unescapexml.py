#!/usr/bin/env python
""" Removes HTML or XML character references and entities from a text string."""
import re
import htmlentitydefs

def unescapeXml(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] == "-h" or sys.argv[1] == "--help":
        print "Usage: %s <string to escape>" % sys.argv[0]
        sys.exit(0)
    string = sys.argv[1]
    print unescapeXml(string)
