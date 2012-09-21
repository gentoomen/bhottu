#coding: utf-8

from api import *
import sys

def load():
	"""Converts to and from kana."""
	registerFunction('romanize %S', romanize, "romanize <kana>")
	registerFunction('kana %s %S', kanifier, "<kanatype> for <romaji>")
registerModule('Kana', load)

hiragana={
#https://gist.github.com/711089
u'あ':u'a',u'い':u'i',u'う':u'u',u'え':u'e',u'お':u'o',
u'か':u'ka',u'き':u'ki',u'く':u'ku',u'け':u'ke',u'こ':u'ko',
u'さ':u'sa',u'し':u'si',u'す':u'su',u'せ':u'se',u'そ':u'so',
u'た':u'ta',u'ち':u'chi',u'つ':u'tu',u'て':u'te',u'と':u'to',
u'な':u'na',u'に':u'ni',u'ぬ':u'nu',u'ね':u'ne',u'の':u'no',
u'は':u'ha',u'ひ':u'hi',u'ふ':u'hu',u'へ':u'he',u'ほ':u'ho',
u'ま':u'ma',u'み':u'mi',u'む':u'mu',u'め':u'me',u'も':u'mo',
u'や':u'ya',u'ゆ':u'yu',u'よ':u'yo',
u'ら':u'ra',u'り':u'ri',u'る':u'ru',u'れ':u're',u'ろ':u'ro',
u'わ':u'wa',u'を':u'wo',u'ん':u'n',

u'が':u'ga',u'ぎ':u'gi',u'ぐ':u'gu',u'げ':u'ge',u'ご':u'go',
u'ざ':u'za',u'じ':u'zi',u'ず':u'zu',u'ぜ':u'ze',u'ぞ':u'zo',
u'だ':u'da',u'ぢ':u'di',u'づ':u'du',u'で':u'de',u'ど':u'do',
u'ば':u'ba',u'び':u'bi',u'ぶ':u'bu',u'べ':u'be',u'ぼ':u'bo',
u'ぱ':u'pa',u'ぴ':u'pi',u'ぷ':u'pu',u'ぺ':u'pe',u'ぽ':u'po',

u'ぁ':u'xa',u'ぃ':u'xi',u'ぅ':u'xu',u'ぇ':u'xe',u'ぉ':u'xo',
#u'ゃ':u'ya',u'ゅ':u'yu',u'ょ':u'yo',
#u'ゎ':u'wa',

u'ゐ':u'wi',u'ゑ':u'we',
u'ー':u'',

u'っ':u'sokuon',

u'きゃ':u'kya',u'きゅ':u'kyu',u'きょ':u'kyo',
u'しゃ':u'sha',u'しゅ':u'shu',u'しょ':u'sho',
u'ちゃ':u'cha',u'ちゅ':u'chu',u'ちょ':u'cho',
u'にゃ':u'nya',u'にゅ':u'nyu',u'にょ':u'nyo',
u'ひゃ':u'hya',u'ひゅ':u'hyu',u'ひょ':u'hyo',
u'みゃ':u'mya',u'みゅ':u'myu',u'みょ':u'myo',
u'りゃ':u'rya',u'りゅ':u'ryu',u'りょ':u'ryo',
u'ぎゃ':u'gya',u'ぎゅ':u'gyu',u'ぎょ':u'gyo',
u'じゃ':u'ja',u'じゅ':u'ju',u'じょ':u'jo',
u'びゃ':u'bya',u'びゅ':u'byu',u'びょ':u'byo',
u'ぴゃ':u'pya',u'ぴゅ':u'pyu',u'ぴょ':u'pyo',
u'ゔ':u'vu'
}
alphanumerics={
u'０':u'0',u'１':u'1',u'２':u'2',u'３':u'3',u'４':u'4',
u'５':u'5',u'６':u'6',u'７':u'7',u'８':u'8',u'９':u'9',

u'Ａ':u'a',u'Ｂ':u'b',u'Ｃ':u'c',u'Ｄ':u'd',u'Ｅ':u'e',u'Ｆ':u'f',u'Ｇ':u'g',u'Ｈ':u'h',u'Ｉ':u'i',
u'Ｊ':u'j',u'Ｋ':u'k',u'Ｌ':u'l',u'Ｍ':u'm',u'Ｎ':u'n',u'Ｏ':u'o',u'Ｐ':u'p',u'Ｑ':u'q',u'Ｒ':u'r',
u'Ｓ':u's',u'Ｔ':u't',u'Ｕ':u'u',u'Ｖ':u'v',u'Ｗ':u'w',u'Ｘ':u'x',u'Ｙ':u'y',u'Ｚ':u'z',

u'ａ':u'a',u'ｂ':u'b',u'ｃ':u'c',u'ｄ':u'd',u'ｅ':u'e',u'ｆ':u'f',u'ｇ':u'g',u'ｈ':u'h',u'ｉ':u'i',
u'ｊ':u'j',u'ｋ':u'k',u'ｌ':u'l',u'ｍ':u'm',u'ｎ':u'n',u'ｏ':u'o',u'ｐ':u'p',u'ｑ':u'q',u'ｒ':u'r',
u'ｓ':u's',u'ｔ':u't',u'ｕ':u'u',u'ｖ':u'v',u'ｗ':u'w',u'ｘ':u'x',u'ｙ':u'y',u'ｚ':u'z',

u'！':u'!',u'＂':u'"',u'＃':u'#',u'＄':u'$',u'％':u'%',u'＆':u'&',u'＇':u"'",u'（':u'(',u'）':u')',u'＊':u'*',u'＋':u'+',u'，':u',',u'－':u'-',u'．':u'.',u'／':u'/'

}
katakana={

u'ア':u'a',u'イ':u'i',u'ウ':u'u',u'エ':u'e',u'オ':u'o',u'ン':u'n',

u'カ':u'ka',u'キ':u'ki',u'ク':u'ku',u'ケ':u'ke',u'コ':u'ko',
u'サ':u'sa',u'シ':u'si',u'ス':u'su',u'セ':u'se',u'ソ':u'so',
u'タ':u'ta',u'チ':u'ti',u'ツ':u'tu',u'テ':u'te',u'ト':u'to',
u'ナ':u'na',u'ニ':u'ni',u'ヌ':u'nu',u'ネ':u'ne',u'ノ':u'no',
u'ハ':u'ha',u'ヒ':u'hi',u'フ':u'fu',u'ヘ':u'he',u'ホ':u'ho',
u'マ':u'ma',u'ミ':u'mi',u'ム':u'mu',u'メ':u'me',u'モ':u'mo',
u'ヤ':u'ya',u'ユ':u'yu',u'ヨ':u'yo',
u'ラ':u'ra',u'リ':u'ri',u'ル':u'ru',u'レ':u're',u'ロ':u'ro',
u'ワ':u'wa',u'ヲ':u'wo',
u'ガ':u'ga',u'ギ':u'gi',u'グ':u'gu',u'ゲ':u'ge',u'ゴ':u'go',
u'ザ':u'za',u'ジ':u'zi',u'ズ':u'zu',u'ゼ':u'ze',u'ゾ':u'zo',
u'ダ':u'da',u'ヂ':u'di',u'ヅ':u'du',u'デ':u'de',u'ド':u'do',
u'バ':u'ba',u'ビ':u'bi',u'ブ':u'bu',u'ベ':u'be',u'ボ':u'bo',
u'パ':u'pa',u'ピ':u'pi',u'プ':u'pu',u'ペ':u'pe',u'ポ':u'po',
u'ジャ':u'ja',u'ju':u'ジュ',u'jo':u'ジョ',u'ジ':u'ji',
u'ヴィ':u'vi',


u'キャ':u'kya',u'キュ':u'kyu',u'キョ':u'kyo',
u'シャ':u'sha',u'シュ':u'shu',u'ショ':u'sho',u'シ':u'shi',u'ツ':u'tsu',
u'チャ':u'cha',u'チュ':u'chu',u'チョ':u'cho',u'チ':u'chi',
u'ニャ':u'nya',u'ニュ':u'nyu',u'ニョ':u'nyo',
u'ヒャ':u'hya',u'ヒュ':u'hyu',u'ヒョ':u'hyo',
u'ミャ':u'mya',u'ミュ':u'myu',u'ミョ':u'myo',
u'リャ':u'rya',u'リュ':u'ryu',u'リョ':u'ryo',
u'ギャ':u'gya',u'ギュ':u'gyu',u'ギョ':u'gyo',
u'ビャ':u'bya',u'ビュ':u'byu',u'ビョ':u'byo',
u'ピャ':u'pya',u'ピュ':u'pyu',u'ピョ':u'pyo',

u'ッ':u'sokuon'}
romanizeText = u''

hiraganaReversed = dict((v,k) for k,v in hiragana.iteritems())
katakanaReversed = dict((v,k) for k,v in katakana.iteritems())
alphanumericsReversed = dict((v,k) for k,v in alphanumerics.iteritems())
dictionaries = [hiragana, katakana, alphanumerics]


def romanizer(romanizeMe):
	global romanizeText
	romanizeMe = romanizeMe.decode('utf-8')
	for dictToUse in dictionaries:
		for char in romanizeMe: 
			try:
				value = dictToUse[char]
				romanizeMe = romanizeMe.replace(char, value)
			except KeyError, e:
				continue
	romanizeMe = romanizeMe.encode('utf-8')
	return romanizeMe
def romanize(channel, sender, message):
	sendMessage(channel, "%s" % romanizer(message))

"""
This function is a little hard to understand, but I'll do my best:
First, make kanifyMe into a list that can be iterated through. Then, act on each "char" in the list, as such:

* if the char is a vowel, skip to the end and switch it with its kana
* if the char is a consonant:
	*first, try to get the next character. If we're at the last character, obviously an IndexError will be raised, so we continue
		*if the next character is not a vowel, get the character after that. This is important because of things like "chi" and "pyu"
		*store it in temp, be it 2 or 3 characters
	*once we have our possibly valid kana, find it in the dictionary. Then, try to set the index in the list to it.
		*the function would go on to the next character next, which is bad because it will result in repetition (e.g. "はあ")
		*take the length of nextchar (it can be either 1 or 2) and remove that many chars from the next index in the list.
		*an IndexError may be raised if we're at the end and we try to remove two characters, so pass on that.
		*take advantage of index errors as well. if one is raised, and the character is an "n", we know it's a consonant n.
* once we finally have our value, try to find it in the dictionary if it is not an "n" character. If it were, it would replace the correct kana with just an n kana.

For instance, if the user typed "asdfgh", the program would parse it as
-a
-sdf
-gh
and return it as:
アsdfgh

"""
def kanify(kanifyMe, preference):
	kanifyMe = kanifyMe.decode('utf-8')
	kanifyMe = list(kanifyMe)
	if preference == "hiragana":
		reversedDictionaries = [hiraganaReversed, katakanaReversed, alphanumericsReversed]
	else:
		reversedDictionaries = [katakanaReversed, hiraganaReversed, alphanumericsReversed]
	for dictToUse in reversedDictionaries:
		specialchars = list(u'!@#$%^&*().,/;\'[]{}:<>?"\\|-=_+')
		vowels = list(u'aeiou')
		index = -1
		for char in kanifyMe:
			index += 1
			if char not in vowels:
				try:
					nextchar = kanifyMe[index + 1]
				except IndexError, e:
					#deal with single "n" at the end of a phrase
					if char == "n" and dictToUse is not alphanumericsReversed:
						value = dictToUse['n']
						kanifyMe[index] = value
					continue
				if nextchar == char and dictToUse is not alphanumericsReversed and char not in specialchars and ord(char) < 128:
					try:
						value = dictToUse['sokuon']
						kanifyMe[index] = value
					except KeyError, e:
						continue
					continue
				if nextchar not in vowels:
					try:
						nextchar += kanifyMe[index + 2]
					except IndexError, e:
						continue
				temp = char + nextchar
				try:
					value = dictToUse[temp]
					kanifyMe[index] = value
					try:
						for x in range(0,len(nextchar)):
							kanifyMe.remove(kanifyMe[index + 1])
					except IndexError, e:
						pass
				except KeyError, e:
					if char == "n" and dictToUse is not alphanumericsReversed:
						value = dictToUse['n']
						kanifyMe[index] = value
					continue
			if char != "n":
				try: 		
					value = dictToUse[char]
					kanifyMe[index] = value
				except KeyError, e:
					pass
	kanifyMe = ''.join(kanifyMe)
	return kanifyMe.encode('utf-8')

def kanifier(channel, sender, preference, message):
	sendMessage(channel, "%s" % kanify(message, preference))
