'''DATA SCRAPPING BOT [FLIPKART] FOR RAWCULT TREND-ANALYSIS
~ SHIVAM RAJPUT '''

# SORTING DICTIONARY ACCORDING TO THE SOURCE URL
sort_dict = {
    'Popularity' : 'popularity',
    'Freshness' : 'recency_desc'
}

# IMPORTANT PARAMETERS
from runBot_TA import *
MAX_PRODUCT_FROM_EACH_CATEGORY = NO_OF_PRODUCTS_TO_SCRAPE['Flipkart']
URL_DICT = TO_SCRAPE_URL_DICT['Flipkart']
HEADLESS_BROWSER = False
scroll_pause_time = 1.5 # According to your Internet Speed
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
no_scrolls = int(MAX_PRODUCT_FROM_EACH_CATEGORY/40) # 40 products per scroll

if MAX_PRODUCT_FROM_EACH_CATEGORY==40: no_scrolls = 0

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

    for sort_type in sort_dict.keys():

        # ACCORDING TO THE SORTING , GOING TO THE WEBSITE PAGE TO SCRAPE
        driver.get(URL_DICT[SUB_CATEGORY] + '&sort=' + sort_dict[sort_type])

        # SETTING UP LOOP VARIABLE TO THE INITAL VALUES
        FINALDATA[SUB_CATEGORY][sort_type] = []
        sample = []
        productList = []

        print(f'[FLIPKART] >> {SUB_CATEGORY} >> {sort_type}\n')

        for page in range(0, no_scrolls+1):
            if page>0:
                driver.find_element(By.XPATH, '/html/body/div[1]/div/div[3]/div[1]/div[2]/div[12]/div/div/nav/a[11]').click()
                time.sleep(1)

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

            for i in range(1, 11):
                for j in range(1,5):

                    productelm = driver.find_element(By.XPATH, f'/html/body/div[1]/div/div[3]/div[1]/div[2]/div[{1+i}]/div/div[{j}]/div')
                    try:
                        linkelm = productelm.find_element(By.XPATH, 'a')
                        productList.append(linkelm.get_attribute('href'))
                    except:
                        print(f'Error in Product Link page {page+1} Product({i}, {j})')

        # -----------------------------------------------------------------------------------------

        index = 1
        for product in productList:
            if index>MAX_PRODUCT_FROM_EACH_CATEGORY: break
            driver.get(product)

            # IMAGE LINK *
            try:
                img_link = driver.find_element(By.CSS_SELECTOR, '._53J4C-.utBuJY').get_attribute('src')
            except:
                print(f'Image Link Error in {product}')
                continue

            # BRAND *
            try:
                brand = driver.find_element(By.CLASS_NAME, 'mEh187').text
            except:
                print(f'Brand Name error in: {product}')
                continue

            # TITLE *
            try:
                title = driver.find_element(By.CLASS_NAME, 'VU-ZEz').text
            except:
                print(f'Title error in: {product}')
                continue

            # CURRENT PRICE *
            try:
                price = driver.find_element(By.CSS_SELECTOR, '.Nx9bqj.CxhGGd').text

                # EXTRACTING
                price = price.replace('₹', '').replace(',', '')
                if price.replace('.', '').isnumeric(): price = int(float(price))
                else: price = price

            except:
                print(f'Price error in: {product}')
                price = None

            # DISCOUNT
            try:
                discount = driver.find_element(By.CSS_SELECTOR, '.UkUFwK.WW8yVX.dB67CR').text

                # EXTRACTING
                discount = int(discount.split('%')[0])
                original_price = int((int(price))/((100-discount)/100))

            except:
                discount = 0
                original_price = price

            # RATING INFO
            try:
                rating_info = driver.find_element(By.CLASS_NAME, 'Wphh3N').text

                # EXTRACTING REQUIRED DATA.
                ratings_count = rating_info.split('and')[0].split('ratings')[0].strip()
                if convert_to_number(ratings_count).replace(',', '').replace('.', '').isnumeric():
                    ratings_count = int(convert_to_number(ratings_count).replace(',', ''))
                else:
                    ratings_count = convert_to_number(ratings_count).replace(',', '')

                reviews_count = rating_info.split('and')[1].split('reviews')[0].strip()
                if convert_to_number(reviews_count).replace(',', '').replace('.', '').isnumeric():
                    reviews_count = int(convert_to_number(reviews_count).replace(',', ''))
                else:
                    reviews_count = convert_to_number(reviews_count).replace(',', '')

            except:
                ratings_count = None
                reviews_count = None

            # RATINGS NUMBER
            try:
                rating = driver.find_element(By.CSS_SELECTOR, '.XQDdHH._1Quie7').text

                # EXTRACTING
                if rating.replace('.', '').isnumeric(): rating = round(float(rating),1)
                else: rating = rating

            except:
                rating = None

            # CLICKING THE PRODUCT DETAILS BUTTON
            try:
                driver.find_element(By.CSS_SELECTOR, '#container > div > div._39kFie.N3De93.JxFEK3._48O0EI > div.DOjaWF.YJG4Cf > div.DOjaWF.gdgoEp.col-8-12 > div.DOjaWF.gdgoEp > div:nth-child(2) > div > div > div:nth-child(1) > div.col.col-1-12.cWwIYq > img').click()
            except:
                try:
                    driver.find_element(By.CSS_SELECTOR, '#container > div > div._39kFie.N3De93.JxFEK3._48O0EI > div.DOjaWF.YJG4Cf > div.DOjaWF.gdgoEp.col-8-12 > div.DOjaWF.gdgoEp > div > div > div:nth-child(2) > div > div > div:nth-child(1) > div.col.col-1-12.cWwIYq > img').click()
                except:
                    pass

            time.sleep(0.25)

            # PRODUCT DETAILS VALUES - ATTRIBUTES
            attributes = []
            try:
                for j in driver.find_elements(By.CSS_SELECTOR, 'div.col.col-9-12.-gXFvC'):
                    attributes.append(j.text)
            except:
                attributes = []

            # ATTRIBUTE FORMATTING
            attributes = [
                [word for word in line.lower().strip().split()]
                for line in attributes if line.strip()
            ]
            attributes = [attr for attr in attributes if attr]
            attributes = [" ".join(attr) for attr in attributes]

            # WRITTEN REVIEWS
            revwDict = {}
            try:
                for i,k in enumerate(driver.find_elements(By.CLASS_NAME, '_11pzQk')):
                    revwDict[i+1] = k.text
            except:
                revwDict = {}

            print(f"{index} !! {price} {ratings_count} {reviews_count} ")

            sample.append({
                'product_id': make_id(title, brand),
                'sorting_rank': index,
                'sorting': sort_type,
                'title': title,
                'brand': brand,
                'rating_outof5': rating,
                'ratings_count': ratings_count,
                'current_price': price,
                'original_price': original_price,
                'img_link': img_link,
                'product_link': product,
                'reviews_count': reviews_count,
                'reviews_detail': revwDict,
                'attributes': attributes,
                'category': SUB_CATEGORY,
                'platform': 'Flipkart',
                'dataDate': datetime.datetime.now().strftime("%d-%m-%Y || %H:%M")
            })

            index+= 1

        FINALDATA[SUB_CATEGORY][sort_type] = sample

for SUB_CATEGORY in URL_DICT.keys():
    smpdt = FINALDATA[SUB_CATEGORY]['Popularity']
    for dt in smpdt: dt['sorting'] = 'Recommended'
    FINALDATA[SUB_CATEGORY]['Recommended'] = smpdt

# MAKING THE JSON FILE FO THE FINAL DATA
with open(f'prodData_Flipkart.json', 'w', encoding="utf-8") as fl:
    fl.write(json.dumps(FINALDATA, indent=2, ensure_ascii=False))

driver.quit()
tm_end = time.time()
total_scrapped = MAX_PRODUCT_FROM_EACH_CATEGORY * len(URL_DICT.keys()) * len(sort_dict.keys())
try:
    print(f'\nTotal Products Scrapped: {total_scrapped}')
    print(f'Total Time Taken: {round((tm_end-tm_start)/60, 2)} Minutes')
    print(f'Time Taken per product: {round(((tm_end-tm_start))/total_scrapped, 2)} Seconds')
finally:
    print('SCRAPPED FLIPKART!\n')

quit()