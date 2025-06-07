'''DATA SCRAPPING BOT [THE SNITCH] FOR RAWCULT TREND-ANALYSIS
~ SHIVAM RAJPUT '''
''' WRITTEN REVIEWS AND COUNTS ARE NOT AVAILABLE MOSTLY WITH RATING TOO''' #TODO: ATTRIBUTES ERROR

# THE SUB-CATEGORIZED LINK DICTIONARY YOU WANT TO SCRAPE! PUT THE LINKS HERE
URL_DICT = {
    'men-tshirts': 'https://www.snitch.co.in/collections/T-Shirts',
    # 'men-shirts': 'https://www.snitch.co.in/collections/shirts',
}
# SORTING DICTIONARY ACCORDING TO THE SOURCE URL
sort_dict = {
    'Recommended': 'manual',
    'Freshness': 'created-descending',
}

# IMPORTANT PARAMETERS
from runBot_TA import *
MAX_PRODUCT_FROM_EACH_CATEGORY = NO_OF_PRODUCTS_TO_SCRAPE
HEADLESS_BROWSER = False
scroll_pause_time = 1.5 # According to your Internet Speed
IMPLICIT_WAIT = 0.5

#-------------------------------------------------------------------------------------------------------------

# ALL IMPORT IMPORTS
import time, json, ssl
tm_start = time.time()
from selenium import webdriver
from selenium.webdriver.common.by import By

# CONSTANTS
scroll_height_step = 1000
FINALDATA = {}
scroll_count = int(MAX_PRODUCT_FROM_EACH_CATEGORY / 8) + 1  # Set the maximum number of scrolls

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
for SUB_CATEGORY in URL_DICT:

    FINALDATA[SUB_CATEGORY] = {}

    for sort_type in sort_dict.keys():

        # ACCORDING TO THE SORTING , GOING TO THE WEBSITE PAGE TO SCRAPE
        driver.get(URL_DICT[SUB_CATEGORY] + '?sort=' + sort_dict[sort_type])

        # SETTING UP LOOP VARIABLE TO THE INITAL VALUES
        FINALDATA[SUB_CATEGORY][sort_type] = []
        sample = []
        productList = []

        print(f'[SNITCH] >> {SUB_CATEGORY} >> {sort_type}\n')

        # SCROLL TILL WHAT NECESSARY
        step = 0
        current_scroll = 0
        while True:
            if current_scroll <= scroll_count:
                if current_scroll%3==0: time.sleep(0.7)
                driver.execute_script(f"window.scrollTo(0, {step});")
                time.sleep(scroll_pause_time)
                step += scroll_height_step
                current_scroll += 1
            else:
                break

        # -----------------------------------------------------------------------------------------

        for e, elm in enumerate(driver.find_elements(By.CSS_SELECTOR, '.boost-sd__product-item.boost-sd__product-item--no-border.boost-sd__product-item-grid-view-layout')):
            if e+1> MAX_PRODUCT_FROM_EACH_CATEGORY: break

            try:
                productList.append(elm.find_element(By.CLASS_NAME, 'boost-sd__product-link').get_attribute('href'))
            except:
                continue

        index = 1
        for product in productList:
            driver.get(product)

            # IMAGE LINK *
            try:
                img_link = driver.find_element(By.CSS_SELECTOR, '.photoswipe__image.image-element').get_attribute('src')
            except:
                print('image error in product: ' + product)
                continue

            # BRAND *
            brand = 'Snitch'

            # TITLE *
            try:
                title = driver.find_element(By.CSS_SELECTOR, '.h2.product-single__title').text
            except:
                print(f'Title error in: {product}')
                continue

            # CURRENT PRICE *
            try:
                price = driver.find_element(By.CSS_SELECTOR, '.product__price').text

                # EXTRACTING
                price = price.replace('INR', '').replace(',', '').strip()
                if price.replace('.', '').isnumeric():
                    price = int(float(price))
                else:
                    price = price
            except:
                try:
                    price = driver.find_element(By.CSS_SELECTOR, '.product__price.on-sale').text

                    # EXTRACTING
                    price = price.replace('INR', '').replace(',', '').strip()
                    if price.replace('.', '').isnumeric():
                        price = int(float(price))
                    else:
                        price = price
                except:
                    print(f'Price error in: {product}')
                    continue

            # ORIGINAL PRICE
            original_price = price

            driver.execute_script(f"window.scrollTo(0, 500);")
            time.sleep(0.4)

            # SCROLLING AND THEN CLICKING THE BUTTON FOR SPECIFICATION
            try:
                driver.find_element(By.XPATH,
                                    '/html/body/div[2]/div/main/div[1]/div[2]/div/div/div/div[2]/div/div[2]/div[8]/div/button').click()
            except:
                try:
                    driver.find_element(By.CSS_SELECTOR,
                                        '#ProductSection-template--17015322280098__main-7355196211362 > div > div > div > div:nth-child(2) > div > div:nth-child(2) > div:nth-child(8) > div > button').click()
                except:
                    print('could not click attribute button for: ' + product)
            time.sleep(0.25)

            # PRODUCT DETAILS VALUES - ATTRIBUTES
            attributes = []
            try:
                descpfull = driver.find_element(By.ID,'Product-content-description7355196211362').text.split('\n')
            except:
                try:
                    descpfull = driver.find_element(By.XPATH, '/html/body/div[1]/div/main/div[1]/div[2]/div/div/div/div[2]/div/div[2]/div[8]/div/div/div').text.split('\n')
                except:
                    descpfull = []
                    print(f'Attributes error in: {product}')

            attributes = descpfull

            # ATTRIBUTE FORMATTING
            attributes = [
                [word for word in line.lower().strip().split() if word not in details_crap]
                for line in attributes if line.strip()
            ]
            attributes = [attr for attr in attributes if attr]
            attributes = [" ".join(attr) for attr in attributes]

            driver.execute_script(f"window.scrollTo(0, 3500);")
            time.sleep(1.0)

            # RATING
            try:
                rating = (driver.find_element(By.CLASS_NAME, 'jdgm-rev-widg__summary-text').text)
                rating = rating.replace('out', '').replace('of', '').replace('5', '').strip()

                # EXTRACTING
                if rating.replace('.', '').isnumeric():
                    rating = round(float(rating), 2)
                else:
                    rating = rating
            except:
                rating = None

            if rating=="": rating = None


            # RATING NUMBER
            try:
                rating_info = driver.find_element(By.CLASS_NAME, 'jdgm-rev-widg__summary-average').text
                ratings_count = rating_info.replace('Based', '').replace('reviews', '').replace('on', '').replace('review', '').strip()

                if ratings_count.isnumeric():
                    ratings_count = int(ratings_count)
            except:
                ratings_count = None

            # WRITTEN REVIEWS
            reviews_count = None
            revwDict = {}

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
                'platform': 'Snitch'
                }
            )

            index += 1

        FINALDATA[SUB_CATEGORY][sort_type] = sample

# MAKING THE JSON FILE FO THE FINAL DATA
with open(f'prodData_Snitch.json', 'w', encoding="utf-8") as fl:
    fl.write(json.dumps(FINALDATA, indent=2, ensure_ascii=False))

driver.quit()
tm_end = time.time()
total_scrapped = MAX_PRODUCT_FROM_EACH_CATEGORY * len(URL_DICT.keys()) * len(sort_dict.keys())

try:
    print(f'\nTotal Products Scrapped: {total_scrapped}')
    print(f'Total Time Taken: {round((tm_end-tm_start)/60, 2)} Minutes')
    print(f'Time Taken per product: {round(((tm_end-tm_start))/total_scrapped, 2)} Seconds')
finally:
    print('SCRAPPED SNITCH\n')

quit()