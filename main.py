import os
import requests
from time  import sleep
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd

def progress_bar(progress, total):
    percent=100*(progress/float(total))
    bar='█'*int(percent)+'-'*(100-int(percent))
    print(f"\r|{bar}| {percent:.2f}%",end='\r')

this_weekend='eyJmaWx0ZXJfZXZlbnRzX2RhdGVfcmFuZ2U6MCI6IntcIm5hbWVcIjpcImZpbHRlcl9ldmVudHNfZGF0ZVwiLFwiYXJnc1wiOlwiMjAyMy0wOS0yM34yMDIzLTA5LTI0XCJ9In0%3D'

loc=input("Enter the city (or filters): ")
x=input("Enable This Weekend Only filter?(Y/N): ")
if ' ' in loc:
    loc_link=loc.replace(" ","+")
else:
    loc_link=loc
if x=='Y' or x=='y':
    url=f'https://www.facebook.com/events/search/?q={loc_link}&filters={this_weekend}'
else:
    url=f'https://www.facebook.com/events/search/?q={loc_link}'

chrome_options = ChromeOptions()

# Disable notifications and updates
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=chrome_options)

print('Navigating to the page..\n')
driver.get(url)
# not the best or faster way to manage page loading time
# but solve most problems.
delay=5
driver.implicitly_wait(delay / 2)

try:
    WebDriverWait(
        driver, delay).until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[@role="article"]')))
except Exception:
    print("Time out on page: {}".format(url))
    

# Scroll down multiple time to more than 6 events on long event page
# Could be improved with a break when "no_upcoming_events_card" is 
# visible.

# Customise the range using formula: 
# value of range=int((Approx. No. of Events you want to scrap)/10)

# Get the initial scroll position
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    # Scroll to the bottom of the page
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    print('still fetching..\n')

    # Wait for some time to allow new content to load (you can adjust the time)
    sleep(delay/2)  # 2 seconds, adjust as needed

    # Get the new scroll position
    new_height = driver.execute_script("return document.body.scrollHeight")

    # Check if the scroll position has not changed (i.e., reached the end of the page)
    if new_height == last_height:
        break

    # Update the last scroll position
    last_height = new_height


# Once the full page is loaded, we can start to scrap links inside

elements = driver.find_elements(By.XPATH,'//div[@role="article"]')

# Loop through each element and extract text data

# Task: To Put Image Extraction in try except
EVENT_DETAILS=[]
count=0
for element in elements:
    count+=1
    progress_bar(count,len(elements))
    try:
        img_element=element.find_element(By.CSS_SELECTOR,'img')
        img_src = img_element.get_attribute('src')

    except:
        img_src = 'N/A'

# To Extract event links

    # Find the <a> element within the <div>
    links = element.find_elements(By.XPATH,'//div/descendant::a')
    links = [
    link for link in links if "facebook.com/events" in link.get_attribute("href")]
    links = [link.get_attribute("href") for link in links ]
    # On Observation, 1st link is unecessary
    # links=links[1:]
    # for link in links:
    #     print(link+'\n')
    n_events=len(links)-1

    if(count==1):
        print(f"Number of events collected = {n_events}\n")

# For saving Images of events

    if img_src!='N/A':

        # Send an HTTP GET request to the image URL
        response = requests.get(img_src)
        
        if x=='Y' or x=='y':
            folderpath=f'C://Users//adulm//Desktop//fb_event_scraper//events-scrapper//{loc}-This weekend'
        else:
            folderpath=f'C://Users//adulm//Desktop//fb_event_scraper//events-scrapper//{loc}'

        if not os.path.exists(folderpath):
            os.makedirs(folderpath)

        with open(f'{folderpath}/{count}.jpg', 'wb') as file:
        # Write the content of the response (image) to the file
            file.write(response.content)
            print(f'Image for event ({count}) downloaded successfully.\n')
    
    data = element.text
    lines=data.splitlines()
    title=lines[1]
    link=links[count]
    where=lines[2]
    try:
        day=lines[0].split(',')[0]
        time=lines[0].split(',')[1]
    except:
        day="Today"
        time="Happening Now"


    # print(count,')\n'+data+'\n'+img_src+'\n'+href_attribute+'\n')
    print(count,')\n'+data+'\n'+img_src+'\n'+link+'\n')

    dictionary={
        "Title": title,
        "Link": link,
        "Day": day,
        "Time": time,
        "Where": where,
        "Image link":img_src
    }

    EVENT_DETAILS.append(dictionary)
print('\nNow writing to a csv...')
df=pd.DataFrame(EVENT_DETAILS)
df = df.drop_duplicates(subset=['Title'])
print(df)
df.to_csv(f'{loc} events.csv')
print(f'\nfile: {loc} events.csv saved successfully.\n')

# this weekend filter:
# eyJmaWx0ZXJfZXZlbnRzX2RhdGVfcmFuZ2U6MCI6IntcIm5hbWVcIjpcImZpbHRlcl9ldmVudHNfZGF0ZVwiLFwiYXJnc1wiOlwiMjAyMy0wOS0wOX4yMDIzLTA5LTEwXCJ9In0%3D