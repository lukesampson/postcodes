import json, os, parse, re, requests, util

def parseinfo(text):
	items = parse.parse(text)
	infos = [i for i in items if i[0] == 'template' and i[1].startswith('Infobox')]
	if len(infos) == 0:
		return None, None

	_, name, data = infos[0]
	name = re.sub('^Infobox ', '', name)

	return name, data

def parsesubcats(text):
	j = json.loads(text)
	if 'error' in j:
		raise Exception(j['error']['info'])
	cm = j['query']['categorymembers']#
	return [(p['title'], p['pageid']) for p in cm]

def geturl(url):
	headers = { 'User-Agent': 'SuburbBot/0.1 (+https://github.com/lukesampson/suburbs)' }
	return requests.get(url, headers=headers).text

def qs(vars):
	return '?' + '&'.join(['{0}={1}'.format(key, value) for key, value in vars.items()])

def apiurl(vars):
	return 'http://en.wikipedia.org/w/api.php' + qs(vars)

def subcats(name):
	vars = { 'cmtitle': 'Category:' + name.replace(' ', '_'), 'action': 'query', 'list': 'categorymembers', 'cmlimit': 500, 'cmtype': 'subcat', 'format': 'json'}
	url = apiurl(vars)
	try:
		return parsesubcats(geturl(url))
	except Exception as err:
		raise Exception("error loading {}".format(url))

def catpages(pageid):
	vars = { 'cmpageid': pageid, 'action': 'query', 'list': 'categorymembers', 'cmlimit': 500, 'cmtype': 'page', 'format': 'json'}
	url = apiurl(vars)
	return parsesubcats(geturl(url))

def pagetext_from_json(jsontext, pageid):
	j = json.loads(jsontext)
	return j['query']['pages'][str(pageid)]['revisions'][0]['*']

def cached_pagetext(pageid):
	return util.readtext('scratch', 'cache', str(pageid) + '.txt')

def cache_pagetext(pageid, text):
	util.writetext(text, 'scratch', 'cache', str(pageid) + '.txt')

def pagetext(pageid):
	cached = cached_pagetext(pageid)
	if cached is not None:
		return cached

	vars = { 'pageids': pageid, 'action': 'query', 'prop':'revisions', 'rvprop': 'content', 'format': 'json'}
	url = apiurl(vars)
	text = pagetext_from_json(geturl(url), pageid)
	cache_pagetext(pageid, text)
	return text

def striptags(text):
	if not text: return text

	return re.sub(r'(?s)<(\w+).*?((?:</\1>)|$)', '', text)

def linksub(match):
	if match.group(2):
		piped = match.group(2)[1:]
		if piped: return piped
	return match.group(1)

def striplinks(text):
	if not text: return text
	return re.sub(r'\[\[(.*?)(\|.*?)?\]\]', linksub, text)

def extractdata(data):
	name = data.get('name')
	city = striplinks(data.get('city'))
	state = striplinks(data.get('state'))
	postcode = striplinks(striptags(data.get('postcode')))

	return name, city, state, postcode




