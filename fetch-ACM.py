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
  def process(self, conferenceName):
    if os.path.exists(conferenceName):
      for filename in os.listdir(conferenceName): 
        if filename != ".DS_Store" and not os.path.isdir(os.path.join(conferenceName,filename)):
          basename, extension = filename.split('.')
          if extension == "html":
            print basename + ", " + \
              self.getConferenceStatsFromFile(conferenceName + "/" + filename)[0] + ", " + \
              self.getConferencePapersDOIfromFile(conferenceName + "/" + filename)      
    else: 
      return
  
  def getConferenceStatsFromFile(self,filePath):
    f = open(filePath)
    filetext = f.read()
    f.close()
    
    start = '&nbsp;Citation Count: '
    end = ' '
    return re.findall(re.escape(start)+"(.*)"+re.escape(end),filetext)
    
    
  ##
  ## This counting method is not precise
  ## It counts the number of bullets in the page rather than the number of true papers
  ##
  def getConferencePapersDOIfromFile(self,filePath):
    f = open(filePath)
    filetext = f.read()
    f.close()
    
    start = 'doi&gt;<a href="'
    end = '" title'
    doiList = re.findall(re.escape(start)+"(.*)"+re.escape(end),filetext)
    return str(len(doiList))
    # for doi in doiList:
    #   folder = filePath.split(".")[0]
    #   # let's create a directory for the conference if none exists
    #   if not os.path.exists(folder):
    #     os.makedirs(folder)
    #     os.makedirs(folder+"/10.1145")
    #   paper = string.lstrip(doi,"http://dx.doi.org/")
    #   Mycurl().curl_limit_rate(doi, folder+"/"+paper+".html", 10000)
    
    
class Mycurl:
  def curl_limit_rate(self, url, filename, rate_limit):
    print url, filename, rate_limit
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.MAX_RECV_SPEED_LARGE, rate_limit)
    if os.path.exists(filename):
        file_id = open(filename, "ab")
        c.setopt(c.RESUME_FROM, os.path.getsize(filename))
    else:
        file_id = open(filename, "wb")

    c.setopt(c.WRITEDATA, file_id)
    # c.setopt(c.NOPROGRESS, 0)
    #    c.setopt(c.PROGRESSFUNCTION, self.curl_progress)
    c.perform()

  def curl_progress(self, total, existing, upload_t, upload_d):
      try:
          frac = float(existing)/float(total)
      except:
          frac = 0
      print "Downloaded %d/%d (%0.2f%%)" % (existing, total, frac)

fetcher = Fetcher()
fetcher.start("TEI")

confProc = ConferenceProcessor()
confProc.process("TEI")
