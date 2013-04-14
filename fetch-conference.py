import os
import csv
import time
import datetime
# import urllib
# import urllib2
# import httplib
import pycurl
import xpath
import re
import string 

class Fetcher:

  def start(self, conferenceName):
    print "Fetching data for Conference: " + conferenceName
    self.iter = csv.reader(open("./conf-stats/"+ conferenceName + "-stats.csv", "rb"),delimiter=',', quotechar='"')
    
    # let's create a directory for the conference if none exists
    if not os.path.exists(conferenceName):
        os.makedirs(conferenceName)
    
    self.fetchYearlyConferencePage(conferenceName)

  def fetchYearlyConferencePage(self, conferenceName):
    for conference in self.iter:
      link = conference[6]
      if (len(link)>10):
        # values = self.parseValues(link)
        url = "http://dl.acm.org/" + link + "&preflayout=flat"
        print url
        filePath = conferenceName+ "/"+conference[0].strip()+".html"
        Mycurl().curl_limit_rate(url, filePath, 10000)
        # time.sleep(3)

class ConferenceProcessor:
  def process(self, conferenceName, conferenceYear, fromDOI):
    conferenceFile = os.path.join(conferenceName, conferenceName + "\'"+ conferenceYear + ".html")
    print conferenceFile
    self.getConferencePapersDOIfromFile(conferenceFile, conferenceName, conferenceYear, fromDOI)
  
  def getConferencePapersDOIfromFile(self,filePath, conferenceName, conferenceYear, fromDOI):
    f = open(filePath)
    filetext = f.read()
    f.close()
    
    paperList = [["conference", "year", "doi", "title", "citationCount", "download6weeks", "download12months", "downloadAll", "keywords", "pageNumber", "authors"]]

    start = 'doi&gt;<a href="'
    end = '" title'
    doiList = re.findall(re.escape(start)+"(.*)"+re.escape(end),filetext)

    if "" == fromDOI:
      startDownload = True
    else:
      startDownload = False

    folder = filePath.split(".")[0]
    # let's create a directory for the conference if none exists
    if not os.path.exists(folder):
      os.makedirs(folder)

    for doi in doiList:
      paper = string.lstrip(doi,"http://dx.doi.org/10.1145/")
      print paper, fromDOI
      if startDownload:
        url = "http://dl.acm.org/citation.cfm?doid="+paper #+"&preflayout=flat"
        bckFile = folder+"/"+paper+".html"
        print url
        Mycurl().curl_limit_rate(url, bckFile, 3000)      
        paperDescription = self.processPaper(folder+"/"+paper+".html", conferenceName, conferenceYear)
        paperList.append(paperDescription)
      else:
        if paper == fromDOI:
          startDownload = True
      
    out = csv.writer(open(conferenceName + conferenceYear + ".csv","w"), delimiter=',',quoting=csv.QUOTE_ALL)
    for p in paperList:
      out.writerow(p)

  def processConference(self, conferenceName, conferenceYear):
    folder = os.path.join(conferenceName, conferenceName + "\'"+ conferenceYear)

    paperList = [["conference", "year", "doi", "title", "citationCount", "download6weeks", "download12months", "downloadAll", "keywords", "pageNumber", "authors"]]

    i = 0
    if os.path.exists(folder):
      for filename in os.listdir(folder): 
        if filename != ".DS_Store" and not os.path.isdir(os.path.join(conferenceName,filename)):
          paperDescription = self.processPaper(os.path.join(folder, filename), conferenceName, conferenceYear)
          paperList.append(paperDescription)
          i = i+1
    
    print i
    out = csv.writer(open(conferenceName + conferenceYear + ".csv","w"), delimiter=',',quoting=csv.QUOTE_ALL)
    for p in paperList:
      out.writerow(p)
  
  def processPaper(self, filePath, conferenceName, conferenceYear):
    f = open(filePath)
    filetext = f.read()
    f.close()
        
    ## 
    ## Checking if this is really a paper
    ##
    doi = self.getFirstOccurence('doi&gt;<a href="', '" target="_self"', filetext)
    title = self.getFirstOccurence('<h1 class="mediumb-text" style="margin-top:0px; margin-bottom:0px;"><strong>', '</strong></h1>', filetext)
    citationCount = self.getFirstOccurence("Citation Count: ", "\r\n", filetext)
    download6weeks = self.getFirstOccurence("Downloads (6 Weeks): ", "<br />", filetext)
    download12months = self.getFirstOccurence("Downloads (12 Months): ", "<br />", filetext)
    downloadAll = self.getFirstOccurence("Downloads (cumulative): ", "<br />", filetext)
    keywords = '; '.join( self.getData('<span class="small-text" style="padding-right: 0px; color:#356b20">', '</span></a>', filetext) ) 
    pageNumber = self.getPageNumber(filetext)
    if pageNumber == "":
      return []
    authors = self.getAuthors(filetext)
  
    # print conferenceName, conferenceYear, doi, title, citationCount, download6weeks, download12months, downloadAll, keywords, pageNumber, authors
  
    paperDescription = [conferenceName, conferenceYear, doi, title, citationCount, download6weeks, download12months, downloadAll, keywords, pageNumber, authors]
    
    print paperDescription
    # TODO: 
    # - article image
    # - abstract
    
    
    return paperDescription
    
    
  def getFirstOccurence(self, start, end, filetext):
    data = self.getData(start, end, filetext)
    if data:
      return data[0]
    else:
      return None
  
  def getData(self, start, end, filetext):
    data = re.findall(re.escape(start)+"(.*)"+re.escape(end),filetext)
    return data

  def getPageNumber(self, filetext):
    pages = self.getFirstOccurence('Pages  ', ' \r\n', filetext)
    try: 
      pp = string.split(pages, "-")
      pageNumber = int(pp[1]) - int(pp[0]) + 1
    except :
        return ""
    return str(pageNumber)

  def getAuthors(self, filetext):
    # ATTENTION
    # this is also catching the conference chairs!
    authors = re.findall(re.escape('title="Author Profile Page" target="_self">')+"(.*)"+re.escape("</a>"), filetext)
    affiliations = re.findall(re.escape('title="Institutional Profile Page"><small>')+"(.*)"+re.escape("</small></a>"), filetext)
#   for author in authors:
#   author = string.replace(author,'<td valign="bottom">',"")
#   author = string.replace(author,'<td  valign="top" nowrap="nowrap">',"")
#   author = string.replace(author,"</td>","")
#   author = string.replace(author,"<tr>","")
#   author = string.replace(author,"</tr>","")
#   print authors

    print authors
    print affiliations
    result = ''
    for i in range(len(affiliations)-1):
      result = result + authors[i] + ", " +  affiliations[i]
      if i != len(affiliations)-2:
        result = result + "; "
    return result
    
    
class Mycurl:
  def curl_limit_rate(self, url, filename, rate_limit):
    print url, filename, rate_limit
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.MAX_RECV_SPEED_LARGE, rate_limit)
#   if os.path.exists(filename):
#       print "exists", filename
#       file_id = open(filename, "ab")
#       c.setopt(c.RESUME_FROM, os.path.getsize(filename))
#   else:
#       print "doesnt exists"
    file_id = open(filename, "wb")

    c.setopt(c.WRITEDATA, file_id)
    # c.setopt(c.NOPROGRESS, 0)
    # c.setopt(c.PROGRESSFUNCTION, self.curl_progress)
    c.perform()

  def curl_progress(self, total, existing, upload_t, upload_d):
      try:
          frac = float(existing)/float(total)
      except:
          frac = 0
      print "Downloaded %d/%d (%0.2f%%)" % (existing, total, frac)

confProc = ConferenceProcessor()
confProc.process("CHI","02","")
#confProc.processPaper("CHI/CHI'12/2207676.2207678.html", "CHI","12")
#confProc.processConference("CHI","12")
