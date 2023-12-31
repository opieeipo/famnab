# Foreign Affairs Manual NABber (FAMNAB)
A simple python scraper to grab the text from the Foreign Affairs Manual, Handbook, and DSSR for offline use.

**Prerequisites**

If you don't already have it, get curl:

https://curl.se/download/curl-8.5.0.zip

Chrome.  To make this work, you will need Chrome as it's required for use with the selenium library:

Selenium:

https://www.selenium.dev/documentation/webdriver/getting_started/

Universal Document Converter Extraordnaire:
PanDoc:

https://github.com/jgm/pandoc/releases/latest

https://github.com/jgm/pandoc/releases/download/3.1.11/pandoc-3.1.11-windows-x86_64.msi


**Windows**

>To setup the python environment(s) use the following

*pywinsetup.cmd*

*command usage:*
```
usage: famscrape.py [-h] [--doc_dir DOC_DIR] [--famurl FAMURL] [--dssrurl DSSRURL] [-c]

options:
  -h, --help         show this help message and exit
  --doc_dir DOC_DIR  Provide the name of the directory where you want to store the docs
  --famurl FAMURL    Provide the url for the fam fah
  --dssrurl DSSRURL  Provide the url for most recent the DSSR doc
  -c                 flag to consolidate FAM/FAH files into FAM.txt and FAH.txt
```
`
