'''DATA SCRAPPING BOT [BONKERS CORNER] FOR RAWCULT TREND-ANALYSIS
~ SHIVAM RAJPUT [NOTE- WRITTEN REVIEWS ARE NOT THERE IN AJIO]'''

# THE SUB-CATEGORIZED LINK DICTIONARY YOU WANT TO SCRAPE! PUT THE LINKS HERE
URL_DICT = {
    'men-shirts': 'https://www.bonkerscorner.com/collections/oversized-t-shirt-men?sort_by=',
}

# SORTINGS DICTIONARY ACCORDING TO THE SOURCE URL
sort_dict = {
    'Recommended': 'manual',
    'Popularity': 'best-selling',
    'Freshness': 'created-descending'
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

if False: # DISABLES IMAGE LOADING FOR FASTER PAGE RENDERING
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
        driver.get(URL_DICT[SUB_CATEGORY] + sort_dict[sort_type])

        # SETTING UP LOOP VARIABLE TO THE INITAL VALUES
        FINALDATA[SUB_CATEGORY][sort_type] = []
        sample = []
        productList = []

        print(f'[THE BONKERS CORNER] >> {SUB_CATEGORY} >> {sort_type}\n')

        # SCROLL TILL WHAT NECESSARY
        step = 0
        current_scroll = 0
        while True:
            if current_scroll <= scroll_count:
                if current_scroll%2==0: time.sleep(0.7)
                driver.execute_script(f"window.scrollTo(0, {step});")
                time.sleep(scroll_pause_time)
                step += scroll_height_step
                current_scroll += 1
            else:
                break

        # -----------------------------------------------------------------------------------------

        for e, elm in enumerate(driver.find_elements(By.CSS_SELECTOR, '.product-featured-image.thb-hover')):
            if e+1> MAX_PRODUCT_FROM_EACH_CATEGORY: break
            try:
                productList.append(elm.find_element(By.XPATH, 'a').get_attribute('href'))
            except:
                continue


        # NOW SCRAPPING EACH PRODUCT
        index = 1
        print(productList)
        for product in productList:

            driver.get(product)

            # BRAND *
            brand = 'Bonkers Corner'

            # IMAGE
            try:
                img_link = driver.find_element(By.CSS_SELECTOR, '.lazyautosizes.ls-is-cached.lazyloaded').get_attribute('src')
            except:
                print('Error in image: '.format(product))
                continue

            # TITLE *
            try:
                title = driver.find_element(By.CSS_SELECTOR, '.product-title.uppercase--true').text
            except:
                print(f'Title error in: {product}')
                continue

            # CURRENT PRICE *
            try:
                price = driver.find_element(By.CSS_SELECTOR, '.amount').text.split(' ')
                print(price)
                # price = price.replace('Rs.', '').replace('MRP', '').replace(',', '').strip()
                # if price.replace('.', '').isnumeric():
                #     price = round(float(price),2)
                # else:
                #     price = price
            except:
                print(f'Price error in: {product}')
                continue

            # ORIGINAL PRICE:
            # try:
            #     original_price =

            # RATING & RATING DETAILS AND REVIEWS ALL ARE NOT AVAILABLE IN MOST OF THE PRODUCTS IN SOULED STORE
            rating, ratings_count, reviews_count, revwDict = None, None, None, {}

            driver.execute_script(f"window.scrollTo(0, 300);")
            time.sleep(0.25)

            # try:
            #     driver.find_element(By.ID, 'headingOne').click()
            # except:
            #     print('descrption error in ' + product)

            # PRODUCT DETAILS VALUES - ATTRIBUTES
            attributes = []
            try:
                info = driver.find_element(By.CLASS_NAME, '.collapsible__content.accordion__content.rte').text.split('\n')
                attributes = info
            except:
                attributes = []
                print(f'Attributes error in: {product}')

            # ATTRIBUTE FORMATTING
            attributes = [
                [word for word in line.lower().strip().split()]
                for line in attributes if line.strip()
            ]
            attributes = [attr for attr in attributes if attr]
            attributes = [" ".join(attr) for attr in attributes]


            sample.append({
                'product_id': make_id(title, brand),
                'sorting_rank': index,
                'sorting': sort_type,
                'title': title,
                'brand': brand,
                'rating_outof5': rating,
                'ratings_count': ratings_count,
                'current_price': price,
                'original_price': price,
                'img_link': img_link,
                'product_link': product,
                'reviews_count': reviews_count,
                'reviews_detail': revwDict,
                'attributes': attributes,
                'category': SUB_CATEGORY,
                'platform': 'Bonkers'
            }
            )

            index += 1

        FINALDATA[SUB_CATEGORY][sort_type] = sample

# MAKING THE JSON FILE FO THE FINAL DATA
with open(f'prodData_Bonkers.json', 'w', encoding="utf-8") as fl:
    fl.write(json.dumps(FINALDATA, indent=2, ensure_ascii=False))

driver.quit()
tm_end = time.time()
total_scrapped = MAX_PRODUCT_FROM_EACH_CATEGORY * len(URL_DICT.keys()) * len(sort_dict.keys())
try:
    print(f'\nTotal Products Scrapped: {total_scrapped}')
    print(f'Total Time Taken: {round((tm_end - tm_start) / 60, 2)} Minutes')
    print(f'Time Taken per product: {round(((tm_end - tm_start)) / total_scrapped, 2)} Seconds')
finally:
    print('SCRAPPED THE BONKERS CORNER!\n')

quit()
