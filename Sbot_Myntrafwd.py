'''DATA SCRAPPING BOT [MYNTRA] FOR RAWCULT TREND-ANALYSIS
~ SHIVAM RAJPUT ''' #TODO: IMAGE AND NEXT BUTTON

# SORTING DICTIONARY ACCORDING TO THE SOURCE URL
sort_list = {
    'Recommended': 'recommended',
    'Feedback': 'Customer%20Rating',
    'Freshness': 'new',
    'Popularity': 'popularity',
}

# IMPORTANT PARAMETERS
from runBot_TA import *
MAX_PRODUCT_FROM_EACH_CATEGORY = NO_OF_PRODUCTS_TO_SCRAPE['Myntrafwd']
URL_DICT = TO_SCRAPE_URL_DICT['Myntrafwd']
HEADLESS_BROWSER = False
scroll_pause_time = 1 # According to your Internet Speed
IMPLICIT_WAIT = 0.5

#-------------------------------------------------------------------------------------------------------------

# ALL IMPORT IMPORTS
import time, json, ssl, datetime
tm_start = time.time()
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

# CONSTANTS
scroll_height_step = 1000
FINALDATA = {}
no_scrolls = int(MAX_PRODUCT_FROM_EACH_CATEGORY/50) # 50 products per scroll

if MAX_PRODUCT_FROM_EACH_CATEGORY==50: no_scrolls = 0

#-----------------------------------------------------------------------------------------------------------------------

# ALL CHROME OPTIONS FOR CHROME DRIVER

ssl_context = ssl.create_default_context()

prefs = {"profile.default_content_settings.popups": 0,
         "download.prompt_for_download": False,
         "directory_upgrade": True,
         "safebrowsing.enabled": False}

# SETTING UP CHROME OPTIONS AND THE KEY PARAMETERS
options = webdriver.ChromeOptions()
options.add_argument('--ignore-ssl-errors=yes')
options.add_argument('--ignore-certificate-errors')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

if True: # PREVENTS DETECTION OF AUTOMATION! ALL THREE ARE NECESSARY FOR BYPASSING BOT DETECTION
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option("prefs", prefs)
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--ignore-ssl-errors=yes')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--disable-blink-features=DisableBrownMouth")
    options.add_argument("--disable-web-plank")
    options.add_argument("--disable-web-plank-sandbox")
    options.add_argument("--disable-web-plank-feature")

if HEADLESS_BROWSER: # ENABLES SPEED BOOST WHEN USING HEADLESS MODE
    options.add_argument('--disable-gpu')
    options.add_argument('--headless=new')

if True: # INCREASES SCRAPING SPEED BY DISABLING THE UI
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-infobars')

if True: # REQUIRED ONLY FOR ENVIRONMENTS WITH LOWER MEMORY (E.G., DOCKER)
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')

if True: # MAY IMPROVE PERFORMANCE FOR CROSS-ORIGIN RESOURCE SHARING BUT CAN POSE SECURITY RISKS
    options.add_argument('--disable-web-security')

if True: # DISABLES IMAGE LOADING FOR FASTER PAGE RENDERING
    prefs["profile.managed_default_content_settings.images"] = 2
    options.add_experimental_option("prefs", prefs)

if True: # SETS UP FIXED WINDOW SIZE TO PREVENT VIEWPORT ERRORS
    options.add_argument("window-size=1920,1080")

if True: # DISABLES UNNECESSARY LOGGING PROCESSES
    options.add_argument('--log-level=3')
    options.add_argument('--silent')

if True: # INCREASES SIMULTANEOUS CONNECTIONS FOR FASTER LOADING
    options.add_argument('--max-connections-per-host=100')

if True: # DISABLES CACHING TO AVOID USING OLD DATA
    options.add_argument('--disk-cache-size=0')
    options.add_argument('--disable-cache')
    options.add_argument('--disable-application-cache')
    options.add_argument('--disable-background-timer-throttling')
    options.add_argument('--disable-background-networking')
    options.add_argument('--disable-renderer-backgrounding')
    options.add_argument('--disable-backgrounding-occluded-windows')
    options.add_argument('--disable-site-isolation-trials')
    options.add_argument('--metrics-recording-only')
    options.add_argument('--no-default-browser-check')
    options.add_argument('--disable-setuid-sandbox')
    options.add_argument('--no-first-run')
    options.add_argument('--homepage=about:blank')
    options.add_argument('--disable-hang-monitor')
    options.add_argument('--disable-prompt-on-repost')
    options.add_argument('--disable-sync')

#-----------------------------------------------------------------------------------------------------------------------

# SETTING UP CHROME DRIVER FOR CHROME SCRAPPING
driver = webdriver.Chrome(options=options)
driver.implicitly_wait(IMPLICIT_WAIT)

# MAIN URL LOOP FOR THE SCRAPPER !
for SUB_CATEGORY in URL_DICT.keys():

    FINALDATA[SUB_CATEGORY] = {}

    for sort_type in sort_list.keys():

        # ACCORDING TO THE SORTING , GOING TO THE WEBSITE PAGE TO SCRAPE
        driver.get(URL_DICT[SUB_CATEGORY] + '?sort=' + sort_list[sort_type])

        # SETTING UP LOOP VARIABLE TO THE INITAL VALUES
        FINALDATA[SUB_CATEGORY][sort_type] = []
        sample = []
        productList = []

        print(f'[MYNTRA] >> {SUB_CATEGORY} >> {sort_type}\n')

        for page in range(0, no_scrolls+1):
            index = 1
            if page>0:
                try:
                    driver.find_element(By.XPATH, '/html/body/div[2]/div/main/div[3]/div[2]/div/div[2]/section/div[2]/ul/li[4]').click()
                except:
                    continue

            # SCROLL TO LOAD THE PAGE UP TO 70% DYNAMICALLY
            total_height = driver.execute_script("return document.body.scrollHeight")
            max_scroll_height = int(total_height * 0.6)  # Calculate 70% of the page height

            current_scroll = 0  # Starting point of the scroll
            while current_scroll < max_scroll_height:
                # Scroll by a fixed step
                driver.execute_script(f"window.scrollTo(0, {current_scroll});")
                time.sleep(scroll_pause_time)

                # Update the scroll position
                current_scroll += scroll_height_step

                # Fetch the actual scroll position after the step
                actual_scroll = driver.execute_script("return window.pageYOffset")

                # Stop if the scroll position doesn't update or if we exceed 70% height
                if actual_scroll >= max_scroll_height or actual_scroll == current_scroll:
                    break

            # -----------------------------------------------------------------------------------------

            # SCRAPPING THE ONE BY ONE PRODUCT TILL MAX NUMBER OF PRODUCT SCRAPPPED FOR EACH CATEGORY
            for j, elm in enumerate(driver.find_elements(By.CLASS_NAME, 'product-base')):

                if (j + 1) > (MAX_PRODUCT_FROM_EACH_CATEGORY- page*50 ): break

                towards_img = elm.find_element(By.CLASS_NAME, 'product-imageSliderContainer').find_element(By.CLASS_NAME, 'product-sliderContainer')

                # ALL DIFFERENT WAYS TO GET THE IMG LINK
                try:
                    img_ele = towards_img.find_element(By.XPATH, 'div/picture/img')
                    img_link = img_ele.get_attribute('src')
                except:
                    try:
                        img_ele = towards_img.find_element(By.XPATH, 'div/div/picture/img')
                        img_link = img_ele.get_attribute('src')
                    except:
                        try:
                            img_ele = towards_img.find_element(By.XPATH, 'div/div/div/div/div/div/picture/img')
                            img_link = img_ele.get_attribute('src')
                        except:
                            img_link = None
                            print(f'Error in Scraping Image for {j+1}th product-> SKIPPED')
                            continue

                # EXTRACTING THE TEXT OF THE PRODUCT AND HANDLING IT ACCORDING TO THE DATA WE NEED
                try:
                    elm_textlist = (elm.text).split('\n')

                    if 'AD' in elm_textlist: elm_textlist.remove('AD')
                    if 'Only Few Left!' in elm_textlist: elm_textlist.remove('Only Few Left!')
                    if 'Only Few Left' in elm_textlist: elm_textlist.remove('Only Few Left')

                    if '|' not in elm_textlist and len(elm_textlist) == 5:
                        elm_textlist = ['NA', '', 'NA', elm_textlist[2], elm_textlist[3], elm_textlist[4]]

                    if '|' not in elm_textlist and len(elm_textlist) == 4:
                        elm_textlist = ['NA', '', 'NA', elm_textlist[1], elm_textlist[2], elm_textlist[3]]

                    if '|' not in elm_textlist and len(elm_textlist) == 3:
                        elm_textlist = ['NA', '', 'NA', elm_textlist[0], elm_textlist[1], elm_textlist[2]]

                except:
                    print(f'Error in Scraping Text for {j + 1}th product-> SKIPPED')
                    continue

                # SPLITTING THE PRICE TEXT! EXAMPLE >> Rs. 1727Rs. 3599(52% OFF) TO REQUIRED DATA SET
                priceLine = elm_textlist[5].split('Rs.')
                if len(priceLine) == 1: discounted_price, original_price = priceLine[0].strip() ,priceLine[0].strip()
                elif len(priceLine) == 2: discounted_price, original_price = priceLine[1].strip(), priceLine[1].strip()
                elif len(priceLine) >= 3: discounted_price, original_price = priceLine[1].strip(), (priceLine[2].strip().split('('))[0]

                # CONVERTING THOSE K FORMAT NUMBERS IN BIG FORM FOR CALCULATIONS AND THEN CONVERTION
                ratings_count = convert_to_number(elm_textlist[2])
                if ratings_count.isnumeric():
                    ratings_count = int(ratings_count)
                else:
                    ratings_count = None

                # CONVERTING 'NA' to None and STR-RATING TO FLOAT-PRICE
                if elm_textlist[0].replace('.', '').isnumeric():
                    rating = round(float(elm_textlist[0]),2)
                elif elm_textlist[0] == 'NA':
                    rating = None
                else:
                    rating = elm_textlist[0]

                # DISCOUNTED PRICE CONVERSION
                try: discounted_price = int(discounted_price)
                except: discounted_price = discounted_price

                # ORIGINAL PRICE CONVERSION
                try: original_price = int(original_price)
                except: original_price = original_price

                if not str(discounted_price).isnumeric(): continue

                productList.append(elm.find_element(By.XPATH, f'/html/body/div[2]/div/main/div[3]/div[2]/div/div[2]/section/ul/li[{j+1}]/a').get_attribute('href'))

                # ADDING THE DATA TO THE FINAL DATA
                sample.append({
                    'product_id': make_id(elm_textlist[4], elm_textlist[3]),
                    'sorting_rank': index,
                    'sorting': sort_type,
                    'title': elm_textlist[4],
                    'brand': elm_textlist[3],
                    'rating_outof5': rating,
                    'ratings_count': ratings_count,
                    'current_price': discounted_price,
                    'original_price': original_price,
                    'img_link': img_link
                })
                index+= 1

        # GOING TO EACH PRODUCT THROUGH THE LINK AND SCRAPPING THE DATA FROM THERE
        j = 0
        for product in productList:
            try:
                driver.get(product)
            except:
                continue

            # BOT IN THE PRODUCT PAGE RIGHT NOW FOR SCRAPPING OTHER DETAILS

            # REVIEWS COUNT ------------------------------------------------------------------------------
            try:
                reviews_count = driver.find_element(By.CSS_SELECTOR, '.detailed-reviews-headline').text
                reviews_count = int(reviews_count.replace('(', '').replace(')', '').split(' ')[2].strip())
            except:
                reviews_count = None


            # SCRAPPING REVIEWS TEXT -----------------------------------------------------------------------
            revwDict = {}
            try:
                revw_elm = driver.find_elements(By.CLASS_NAME, 'user-review-reviewTextWrapper')
                for i, revw in enumerate(revw_elm):
                    revwDict[i+1] = revw.text
            except:
                revwDictt = {}


            # SCRAPPING PRODUCT DETAILS AS AN ATTRIBUTRS OF THE PRODUCT --------------------------------------
            attributes: list
            try:
                attributes_box = driver.find_element(By.CLASS_NAME, 'pdp-productDescriptorsContainer').text
                attributes_line = attributes_box.split('\n')

                # ATTRIBUTE FORMATTING HAPPENING
                for i, line in enumerate(attributes_line):
                    attributes_line[i] = line.lower().strip()

                for i, line in enumerate(attributes_line):
                    attributes_line[i] = line.strip().split(' ')

                for i, line in enumerate(attributes_line):
                    attributes_line[i] = ' '.join(line)

                attributes = attributes_line
            except:
                attributes= []

            # ADDING TO THE MAIN DATA ------------------------------------------------------------------------
            sample[j]['product_link'] = product
            sample[j]['reviews_count'] = reviews_count
            sample[j]['reviews_detail'] = revwDict
            sample[j]['attributes'] = attributes + ['fwd', 'genz']
            sample[j]['category'] = SUB_CATEGORY
            sample[j]['platform']:str = "Myntra Fwd",
            sample[j]['dataDate'] = datetime.datetime.now().strftime("%d-%m-%Y || %H:%M")

            j += 1
            print(f"{j}: {reviews_count} ")

        # MAINTAING THE FINAL DATA SET WITH EACH LOOP
        FINALDATA[SUB_CATEGORY][sort_type] = sample


# MAKING THE JSON FILE FO THE FINAL DATA
with open(f'prodData_Myntrafwd.json', 'w', encoding="utf-8") as fl:
    fl.write(json.dumps(FINALDATA, indent=2, ensure_ascii=False))

driver.quit()
tm_end = time.time()
total_scrapped = MAX_PRODUCT_FROM_EACH_CATEGORY * len(URL_DICT.keys()) * len(sort_list.keys())

try:
    print(f'\nTotal Products Scrapped: {total_scrapped}')
    print(f'Total Time Taken: {round((tm_end-tm_start)/60, 2)} Minutes')
    print(f'Time Taken per product: {round(((tm_end-tm_start))/total_scrapped, 2)} Seconds')
finally:
    print('SCRAPPED MYNTRA!\n')

quit()