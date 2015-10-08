#coding: utf-8

import urllib2
from BeautifulSoup import *
from urlparse import urljoin
from sqlite3 import dbapi2 as sqlite

#����һ�������б���Щ���ʽ�������
ignorewords = set(['the', 'of', 'to', 'and', 'a', 'is', 'it'])


class crawler:
	#��ʼ��
	def __init__(self, dbname):
		self.con = sqlite.connect(dbname)
	
	def __del__(self):
		self.con.close()
		
	def dbcommit(self):
		self.con.commit()
	
	#��������,��ȡ��Ŀ��id����������ڴ���Ŀ���ͽ���������ݿ���
	def getentryid(self, table, field, value, createnew = True):
		cur = self.con.execute("select rowid from %s where %s='%s'" % (table, field, value))
		res = cur.fetchone()
		if res == None:
			cur = self.con.execute(
			"insert into %s (%s) values ('%s')" % (table, field, value))
			return cur.lastrowid
		else:
			return res[0]
	
	#Ϊ������ҳ��������
	def addtoindex(self, url, soup):
		if self.isindexed(url): return
		print 'Indexing '+ url
		
		#��ȡÿ������
		text = self.gettextonly(soup)
		words = self.separatewords(text)
		
		#�õ�URL��id
		urlid = self.getentryid('urllist','url',url)
		
		#��ÿ��������� url ����
		for i in range(len(words)):
			word = words[i]
			if word in ignorewords: continue
			wordid = self.getentryid('wordlist', 'word', word)
			self.con.execute("insert into wordlocation(urlid,wordid,location) values (%d, %d, %d)" % (urlid, wordid, i)) 
	
	#��һ��HTML ��ҳ����ȡ���֣�������ǩ��
	def gettextonly(self, soup):
		v = soup.string
		if v == None:
			c = soup.contents
			resulttext = ''
			for t in c:
				subtext = self.gettextonly(t)
				resulttext += subtext+'\n'
			return resulttext
		else:
			return v.strip()
		
	#�����Ͽɷǿհ��ַ����зִʴ���
	def separatewords(self, text):
		splitter = re.compile('\\W*')
		return [s.lower() for s in splitter.split(text) if s!='']
	
	#���url�Ѿ������������򷵻�true
	def isindexed(self, url):
		u = self.con.execute \
		("select rowid from urllist where url='%s'" % url).fetchone()
		if u != None:
			#������Ƿ񱻼�������
			v = self.con.execute(
			"select * from wordlocation where urlid=%d" % u[0]).fetchone()
			if v != None: return True
		return False
	
	#���һ������������ҳ������
	def addlinkref(self, urlFrom, urlTo, linkText):
		pass
	
	#��һС����ҳ��ʼ���й������������ֱ��һ������ȣ�
	#�ڼ�Ϊ��ҳ��������
	def crawl(self, pages, depth = 2):
		for i in range(depth):
			newpages = set()
			for page in pages:
				try:
				 c = urllib2.urlopen(page)
				except:
				 print "Could not open %s" % page
				 continue
				soup = BeautifulSoup(c.read())
				self.addtoindex(page, soup)
				
				links = soup('a')
				for link in links:
					if ('href' in dict(link.attrs)):
						url = urljoin(page, link['href'])
						if url.find("'") != -1: continue
						url = url.split('#')[0] #ȥ��λ�ò���
						if url[0:4] == 'http' and not self.isindexed(url):
							newpages.add(url)
						linkText = self.gettextonly(link)
						self.addlinkref(page, url, linkText)
				
				self.dbcommit()
			pages = newpages
	
	#�������ݿ��
	def createindextables(self):
		self.con.execute('create table urllist(url)')
		self.con.execute('create table wordlist(word)')
		self.con.execute('create table wordlocation(urlid,wordid,location)')
		self.con.execute('create table link(fromid integer,toid integer)')
		self.con.execute('create index wordidx on wordlist(word)')
		self.con.execute('create index urlidx on urllist(url)')
		self.con.execute('create index wordurlidx on wordlocation(wordid)')
		self.con.execute('create index urltoidx on link(toid)')
		self.con.execute('create index urlfromidx on link(fromid)')
		self.dbcommit()

		
class searcher:
	def __init__(self, dbname):
		self.con = sqlite.connect(dbname)
	
	def __del__(self):
		self.con.close()
	
	def getmatchchrows(self, q):
		#�����ѯ���ַ���
		fieldlist = 'w0.urlid'
		tablelist = ''
		clauselist = ''
		wordids = []
		
		#���ݿո��ֵ���
		words = q.sqlit(' ')
		tablenumber = 0
		
		for word in words:
			#��ȡ���ʵ�ID
			wordrow = self.con.execute(
			 "select rowid from wordlist where word='%s'" % word).fetchone()
			if wordrow != None:
				wordid = wordrow[0]
				wordids.append(wordid)
				if tablenumber > 0:
					tablelist += ','
					clauselist += ' and '
					clauselist +='w%d.urlid=w%d.urlid and '% (tablenumber -1, tablenumber)
				fieldlist += ',w%d.location' % tablenumber
				tablerlist += 'wordlocation w%d' % tablenumber
				clauselist += 'w%d.wordid=%d' % (tablenumber,wordid)
				tablenumber += 1
		
		#���ݸ�����֣�������ѯ
		fullquery = 'select %s from $s where %s' % (fieldlist, tablelist, clauselist)
		cur = self.con.execute(fullquery)
		rows = [row for row in cur]
		
		return rows, wordids