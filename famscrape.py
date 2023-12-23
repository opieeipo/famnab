import subprocess
from subprocess import check_output
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import sys
import os
import argparse

parser=argparse.ArgumentParser()

parser.add_argument("--doc_dir", help="Provide the name of the directory where you want to store the docs")

args=parser.parse_args()

#Set the variables from the command line arguments
doc_folder_path=args.doc_dir
if doc_folder_path is None:
 parser.print_help()
else:
  if not os.path.exists(doc_folder_path):
    os.mkdir(doc_folder_path)
  
  op = webdriver.ChromeOptions()
  op.add_argument('--headless')
  driver = webdriver.Chrome(options=op)

  origurl = 'https://fam.state.gov'

  soupbowl = os.path.join(doc_folder_path,"fam.state.gov.txt")
  f = open(soupbowl,"w",encoding="utf-8")
  f.writelines(soupbowl)
  f.close()

  def getQuickSoup(url):
    soup = BeautifulSoup(subprocess.check_output(['curl',url]))
    return soup

  def getSoup(url): 
    driver.get(url)
    time.sleep(5)
    html = driver.page_source
    soup = BeautifulSoup(html) 
    return soup

  def GetThirdLevelDetails(thirdlevelurl):
    thirdLevelSoup=getQuickSoup(thirdlevelurl)
    
    fname = os.path.join(doc_folder_path,thirdlevelurl.split("/")[len(thirdlevelurl.split("/"))-1]+".txt")
    fs = open (fname, "w", encoding="utf-8")
    fs.writelines(thirdLevelSoup.get_text())
    fs.close
    f = open(soupbowl,"a",encoding="utf-8")
    f.writelines(thirdLevelSoup.get_text())
    f.close

  def GetSecondLevelDetails(secondlevelurl):
    secondLevelSoup=getSoup(secondlevelurl) 
    f = open(soupbowl,"a",encoding="utf-8")
    f.writelines(secondLevelSoup.get_text())
    f.close
    treeview = secondLevelSoup.find("div",{"id":"treeview"})
    links = treeview.find_all('a', href=True) 
    ilinks=[]
    for b in links:
      a=b['href']  
      alink = origurl + a
      ilinks.append(alink)
    for i in ilinks:
      print (i)   
    for i in ilinks:
      print ("getting Third Level Details for "+i)
      GetThirdLevelDetails(i)

  def GetFirstLevelDetails(url):
    print ("Getting First Level Details for "+url)
    firstLevelSoup=getQuickSoup(url) 
    f = open(soupbowl,"a",encoding="utf-8")
    f.writelines(firstLevelSoup.get_text())
    f.close
    bodycontent=firstLevelSoup.find("div",{"class":"body-content"})
    links = bodycontent.find_all('a', href=True) 
    ilinks=[]
    for b in links:
      a=b['href']  
      if "Details" in a:
        alink = origurl + a
        ilinks.append(alink)
    for i in ilinks:
      print (i)
    for i in ilinks:
      print ("getting Second Level Details for "+i)
      GetSecondLevelDetails(i)

  GetFirstLevelDetails(origurl)
  driver.close()
  driver.quit()

