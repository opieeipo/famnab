import subprocess
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import sys
import os
import argparse
import pypandoc
import pandoc
import tqdm

parser=argparse.ArgumentParser()

parser.add_argument("--doc_dir", help="Provide the name of the directory where you want to store the docs")
parser.add_argument("--famurl", help="Provide the url for the fam fah")
parser.add_argument("--dssrurl", help="Provide the url for most recent the DSSR doc")
parser.add_argument("-c",action="store_true",help="flag to consolidate FAM/FAH files into FAM.txt and FAH.txt")


args=parser.parse_args()

#Set the variables from the command line arguments
doc_folder_path=args.doc_dir
origurl = args.famurl
dssrurl = args.dssrurl
consolidated = args.c

if doc_folder_path is None or origurl is None or dssrurl is None:
 parser.print_help()
else:
  if not os.path.exists(doc_folder_path):
    os.mkdir(doc_folder_path)
  
  op = webdriver.ChromeOptions()
  op.add_argument('--headless')
  driver = webdriver.Chrome(options=op)


  def getQuickSoup(url):
    soup = BeautifulSoup(subprocess.check_output(['curl',url,'-s']),"html.parser")
    return soup

  def getSoup(url): 
    driver.get(url)
    time.sleep(5)
    html = driver.page_source
    soup = BeautifulSoup(html,"html.parser") 
    return soup

  def GetThirdLevelDetails(thirdlevelurl):
    thirdLevelSoup=getQuickSoup(thirdlevelurl)
    if not consolidated:
      fname = os.path.join(doc_folder_path,thirdlevelurl.split("/")[len(thirdlevelurl.split("/"))-1]+".txt")
      fs = open (fname, "w", encoding="utf-8")
      fs.writelines(thirdLevelSoup.get_text())
      fs.close
    else:
      f = open(soupbowl,"a",encoding="utf-8")
      f.writelines(thirdLevelSoup.get_text())
      f.close

  def GetSecondLevelDetails(secondlevelurl):
    secondLevelSoup=getSoup(secondlevelurl)
    if consolidated:
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
    objs = len(ilinks)
    ts = secondlevelurl.split("/")
    tn = ts[(len(ts)-1)]
    print(f"Getting Chapters for {tn} | {objs} chapters found" )
    gsdpbar = tqdm.tqdm(ilinks,colour='green')
    
    for i in gsdpbar:
      fs = i.split("/")
      fn = fs[(len(fs)-1)]
      gsdpbar.set_description(f"Getting  {fn}")
      GetThirdLevelDetails(i)

  def GetFirstLevelDetails(url):    
    firstLevelSoup=getQuickSoup(url) 
    
    if consolidated:        
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

    objs= len(ilinks)
    print (f"Getting 1st Level FAM Details for {url} | {objs} sections found")
    for i in ilinks:
  
      GetSecondLevelDetails(i)
  
  def GetFirstLevelFAHDetails(url):    
    firstLevelSoup=getQuickSoup(url) 
    if consolidated:
      f = open(soupbowl,"a",encoding="utf-8")
      f.writelines(firstLevelSoup.get_text())
      f.close
    bodycontent=firstLevelSoup.find_all("div",{"class":"dropdown-menu"})
    links = bodycontent[1].find_all('a', href=True) 
    ilinks=[]
    for b in links:
      a=b['href']  
      if "FAH" in a:
        alink = origurl + a
        ilinks.append(alink) 
    objs= len(ilinks)
    print (f"Getting 1st Level FAH Details for {url} | {objs} sections found")
    ffahpbar = tqdm.tqdm(ilinks)
    for i in ffahpbar:
      ffahpbar.set_description(f"Getting 2nd Level Details for {i}")
      GetSecondLevelDetails(i)

  def getDSSR(url):    
    subprocess.check_output(['curl',url,'-o','dssr.docx'])
    op = os.path.join(doc_folder_path,"DSSR.txt")
    pypandoc.convert_file('dssr.docx','plain',outputfile=op)
    os.remove("dssr.docx")

  #Create FAM.txt File
  if consolidated:
    soupbowl = os.path.join(doc_folder_path,"FAM.txt")
    f = open(soupbowl,"w",encoding="utf-8")
    f.writelines(soupbowl)
    f.close()

  GetFirstLevelDetails(origurl)
  
  #Create FAH.txt file
  if consolidated:
    soupbowl = os.path.join(doc_folder_path,"FAH.txt")
    f = open(soupbowl,"w",encoding="utf-8")
    f.writelines(soupbowl)
    f.close()

  GetFirstLevelFAHDetails(origurl)
  getDSSR(dssrurl)
  driver.close()
  driver.quit()

