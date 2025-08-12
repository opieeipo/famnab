import subprocess
from bs4 import BeautifulSoup
import time
import os
import argparse
import pypandoc
import tqdm
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException, SessionNotCreatedException, TimeoutException

driver = None

# A global variable to hold the path for consolidated file writing.
# This is a better approach than reassigning a variable in the main script body.
consolidated_file_path = None

parser = argparse.ArgumentParser()
parser.add_argument("--doc_dir", help="Provide the name of the directory where you want to store the docs")
parser.add_argument("--famurl", help="Provide the url for the fam fah")
parser.add_argument("--dssrurl", help="Provide the url for most recent the DSSR doc")
parser.add_argument("-c", action="store_true", help="flag to consolidate FAM/FAH files into FAM.txt and FAH.txt")
args = parser.parse_args()

doc_folder_path = args.doc_dir
origurl = args.famurl
dssrurl = args.dssrurl
consolidated = args.c


def get_webdriver_instance():
    """
    Creates and returns a new WebDriver instance.
    """
    global driver
    if driver is None:
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            try:
                # This is the modern way to initialize the driver
                driver = webdriver.Chrome(options=options)
            except Exception:
                # Fallback to the old way if an error occurs.
                # This assumes chromedriver is in the system PATH.
                driver = webdriver.Chrome(options=options)

            print("New WebDriver instance created.")
        except SessionNotCreatedException as e:
            print(f"Error creating WebDriver session: {e}")
            driver = None
    return driver


def getQuickSoup(url):
    try:
         soup = BeautifulSoup(subprocess.check_output(
            ['curl', url, '--silent', '--retry', '25', '--retry-delay', '2', '--retry-max-time', '600']
        ), "html.parser")
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        soup = None  # Return None on failure
    return soup


def getSoup(url, max_retries=5):
    """
    Attempts to get a webpage's source using a persistent driver.
    Restarts the driver only if an error occurs.
    """
    global driver

    for retry_count in range(max_retries + 1):
        try:
            # Get or create the driver instance
            if driver is None:
                driver = get_webdriver_instance()
                if driver is None:
                    raise WebDriverException("Failed to create initial driver.")

            # The core logic
            driver.get(url)
            # We wait for the 'body-content' div to be present.
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, "body-content"))
            )
            time.sleep(5)
            html = driver.page_source
            return html

        except (WebDriverException, TimeoutException) as e:
            print(f"Attempt {retry_count + 1}: WebDriver failed with an error: {e}")
            if retry_count < max_retries:
                print("Quitting the old driver and restarting a new one...")
                if driver:
                    driver.quit()
                    driver = None  # Reset the global variable
                continue
            else:
                print("Max retries reached. Giving up.")
                if driver:
                    driver.quit()
                    driver = None
                return None
    return None


def GetThirdLevelDetails(thirdlevelurl):
    thirdLevelSoup = getQuickSoup(thirdlevelurl)
    if thirdLevelSoup is None:
        return

    if not consolidated:
        fname = os.path.join(doc_folder_path, thirdlevelurl.split("/")[-1] + ".txt")
        with open(fname, "w", encoding="utf-8") as fs:
            fs.write(thirdLevelSoup.get_text())
    else:
        # 7. FIX: Use the global consolidated_file_path and proper context manager
        global consolidated_file_path
        with open(consolidated_file_path, "a", encoding="utf-8") as f:
            f.write(thirdLevelSoup.get_text())


def GetSecondLevelDetails(secondlevelurl):
    # 8. We need to handle the case where `getSoup` returns None
    secondLevelSource = getSoup(secondlevelurl)
    if secondLevelSource is None:
        print(f"Skipping {secondlevelurl} due to failure.")
        return

    secondLevelSoup = BeautifulSoup(secondLevelSource, "html.parser")

    if consolidated:
        global consolidated_file_path
        with open(consolidated_file_path, "a", encoding="utf-8") as f:
            f.write(secondLevelSoup.get_text())

    treeview = secondLevelSoup.find("div", {"id": "treeview"})
    if treeview is None:
        print(f"Could not find treeview on {secondlevelurl}")
        return
    links = treeview.find_all('a', href=True)

    ilinks = []
    for b in links:
        a = b['href']
        alink = origurl + a
        ilinks.append(alink)

    objs = len(ilinks)
    ts = secondlevelurl.split("/")
    tn = ts[(len(ts) - 1)]
    print(f"Getting Chapters for {tn} | {objs} chapters found")
    gsdpbar = tqdm.tqdm(ilinks, colour='green')

    for i in gsdpbar:
        fs = i.split("/")
        fn = fs[(len(fs) - 1)]
        gsdpbar.set_description(f"Getting  {fn}")
        GetThirdLevelDetails(i)


def GetFirstLevelDetails(url):
    firstLevelSoup = getQuickSoup(url)
    if firstLevelSoup is None:
        return

    if consolidated:
        global consolidated_file_path
        with open(consolidated_file_path, "a", encoding="utf-8") as f:
            f.writelines(firstLevelSoup.get_text())

    bodycontent = firstLevelSoup.find("div", {"class": "body-content"})
    if bodycontent is None:
        print(f"Could not find body-content on {url}")
        return

    links = bodycontent.find_all('a', href=True)
    ilinks = []
    for b in links:
        a = b['href']
        if "Details" in a:
            alink = origurl + a
            ilinks.append(alink)

    objs = len(ilinks)
    print(f"Getting 1st Level FAM Details for {url} | {objs} sections found")
    for i in ilinks:
        GetSecondLevelDetails(i)


def GetFirstLevelFAHDetails(url):
    firstLevelSoup = getQuickSoup(url)
    if firstLevelSoup is None:
        return

    if consolidated:
        global consolidated_file_path
        with open(consolidated_file_path, "a", encoding="utf-8") as f:
            f.write(firstLevelSoup.get_text())

    bodycontent = firstLevelSoup.find_all("div", {"class": "dropdown-menu"})
    if len(bodycontent) < 2:
        print(f"Could not find dropdown menu on {url}")
        return

    links = bodycontent[1].find_all('a', href=True)
    ilinks = []
    for b in links:
        a = b['href']
        if "FAH" in a:
            alink = origurl + a
            ilinks.append(alink)

    objs = len(ilinks)
    print(f"Getting 1st Level FAH Details for {url} | {objs} sections found")
    ffahpbar = tqdm.tqdm(ilinks)
    for i in ffahpbar:
        ffahpbar.set_description(f"Getting 2nd Level Details for {i}")
        GetSecondLevelDetails(i)


def getDSSR(url):
    try:
        subprocess.check_output(['curl', url, '--output', 'dssr.docx'])
        op = os.path.join(doc_folder_path, "DSSR.txt")
        # Ensure pandoc is installed and in your system PATH
        pypandoc.convert_file('dssr.docx', 'plain', outputfile=op)
        os.remove("dssr.docx")
    except subprocess.CalledProcessError as e:
        print(f"Curl failed to download DSSR.docx with exit code {e.returncode}")
    except RuntimeError as e:
        print(f"Pandoc conversion failed: {e}")
        print("Please ensure pandoc is installed and in your system's PATH.")


# --- Main Script Logic ---

if doc_folder_path is None or origurl is None or dssrurl is None:
    parser.print_help()
else:
    if not os.path.exists(doc_folder_path):
        os.mkdir(doc_folder_path)

    # 10. We initialize the driver here once, to be used by all functions that need it.
    # The get_webdriver_instance function will return a valid driver or None.
    driver = get_webdriver_instance()
    if driver is None:
        print("Could not initialize the WebDriver. Exiting.")
        sys.exit(1)

    if consolidated:
        consolidated_file_path = os.path.join(doc_folder_path, "FAM.txt")
        # 11. Using a `with` statement to ensure the file is properly closed.
        with open(consolidated_file_path, "w", encoding="utf-8") as f:
            f.write("FAM Content\n")  # Write a header
        GetFirstLevelDetails(origurl)

        consolidated_file_path = os.path.join(doc_folder_path, "FAH.txt")
        with open(consolidated_file_path, "w", encoding="utf-8") as f:
            f.write("FAH Content\n")  # Write a header
        GetFirstLevelFAHDetails(origurl)
    else:
        GetFirstLevelDetails(origurl)
        GetFirstLevelFAHDetails(origurl)

    getDSSR(dssrurl)

    driver.quit()

