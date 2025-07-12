'''DATA SCRAPPING BOT [BOMBAY SHIRT COMPANY] FOR RAWCULT TREND-ANALYSIS
~ SHIVAM RAJPUT '''

# SORTING DICTIONARY ACCORDING TO THE SOURCE URL
sort_dict = {
    'Recommended': '',
    'Freshness': '?sort=created-descending',
    'Popularity': '?sort=best-selling'
}

# IMPORTANT PARAMETERS
from runBot_TA import *
MAX_PRODUCT_FROM_EACH_CATEGORY = NO_OF_PRODUCTS_TO_SCRAPE['BombayShirtCompany']
URL_DICT = TO_SCRAPE_URL_DICT['BombayShirtCompany']
HEADLESS_BROWSER = False
scroll_pause_time = 1.5 # According to your Internet Speed
IMPLICIT_WAIT = 0.5

#-------------------------------------------------------------------------------------------------------------

# ALL IMPORTANTS IMPORTS
import time, json, ssl, datetime
tm_start = time.time()
from selenium import webdriver
from selenium.webdriver.common.by import By

# CONSTANTS
scroll_height_step = 1000
FINALDATA = {}
scroll_count = int(MAX_PRODUCT_FROM_EACH_CATEGORY / 6) + 1  # Set the maximum number of scrolls

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
        driver.get(URL_DICT[SUB_CATEGORY] + sort_dict[sort_type])

        # SETTING UP LOOP VARIABLE TO THE INITAL VALUES
        FINALDATA[SUB_CATEGORY][sort_type] = []
        sample = []
        productList = []

        print(f'[BOMBAY SHIRT COMPANY] >> {SUB_CATEGORY} >> {sort_type}\n')

        # SCROLL TILL WHAT NECESSARY
        step = 0
        current_scroll = 0
        while True:
            if current_scroll <= scroll_count:
                if current_scroll % 3 == 0: time.sleep(0.7)
                driver.execute_script(f"window.scrollTo(0, {step});")
                time.sleep(scroll_pause_time)
                step += scroll_height_step
                current_scroll += 1
            else:
                break

        # GOING TO EACH PRODUCT TO SCRAPE THE PRODUCT LINK IN GRID STRUCTURE
        for j, elm in enumerate(driver.find_elements(By.CSS_SELECTOR, '.ProductItem__Wrapper')):

            if (j+1) > MAX_PRODUCT_FROM_EACH_CATEGORY: break

            try:
                productList.append(elm.find_element(By.XPATH, 'a').get_attribute('href'))
            except:
                try:
                    productList.append(elm.find_element(By.XPATH, 'a').get_attribute('href'))
                except:
                    continue

        # NOW SCRAPPING EACH PRODUCT
        index = 1
        for product in productList:
            driver.get(product)

            # IMAGE LINK *
            try:
                img_link = driver.find_element(By.CSS_SELECTOR, ".Product__Wrapper").find_element(By.TAG_NAME, "img").get_attribute('src')
            except Exception as e:
                print(e)
                print(f'Image Link Error in {product}')
                continue

            # BRAND *
            try:
                brand = "Bombay Shirt Company"
            except:
                print(f'Brand Name error in: {product}')
                continue

            # TITLE *
            try:
                title = driver.find_element(By.CSS_SELECTOR, '.ProductMeta__Title.Heading.u-h2.r-ls').text
            except:
                print(f'Title error in: {product}')
                continue

            # CURRENT PRICE *
            try:
                price = driver.find_element(By.CSS_SELECTOR, '.money').text

                # EXTRACTING
                price = price.replace('₹', '').replace(',', '').replace('MRP', '').strip()
                if '\n' in str(price): price = price.split('\n')[1].strip().split(' ')[0].strip()
                if price.replace('.', '').isnumeric():
                    price = int(float(price))
                else:
                    price = price

            except:
                print(f'Price error in: {product}')
                price = None

            # ORIGINAL PRICE
            oprice = price

            # RATING OUT OF 5
            try:
                rating = driver.find_element(By.CSS_SELECTOR, '.jdgm-prev-badge__text').text.strip()

                # EXTRACTING REQUIRED DATA.
                rating = rating.split('\n')[0].strip()

                try:
                    rating = round(float(rating),1)
                except:
                    rating = rating
                    if rating == "":
                        rating = None

            except:
                rating = None

            # RATING AND REVIEW NUMBER
            try:
                rating_info = driver.find_element(By.CSS_SELECTOR, '.jdgm-rev-widg__summary-text').text.strip().split(' ')[0]
                try:
                    ratings_count = int(convert_to_number(rating_info))
                    reviews_count = ratings_count
                except:
                    ratings_count = convert_to_number(rating_info)
                    reviews_count = ratings_count
                    if ratings_count == "": ratings_count, reviews_count = None, None


            except:
                ratings_count = None
                reviews_count = None

            driver.execute_script(f"window.scrollTo(0, 2500);")
            time.sleep(0.7)

            # REVIEWS DICT FINDING
            revwDict = {}
            try:
                for i,rev_div in enumerate(driver.find_elements(By.CSS_SELECTOR, ".jdgm-rev__body")):
                    if i==3: break
                    revwDict[i+1] = rev_div.text

            except:
                revwDict = None

            # PRODUCT DETAILS VALUES - ATTRIBUTES
            attributes = []
            try:
                for j in driver.find_elements(By.CSS_SELECTOR, '.pro-accordion-content-inner'):
                    attributes.extend(j.text.split(' '))
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

            print(f'{index}')

            sample.append({
                'product_id': make_id(title, brand),
                'sorting_rank': index,
                'sorting': sort_type,
                'title': title,
                'brand': brand,
                'rating_outof5': rating,
                'ratings_count': ratings_count,
                'current_price': price,
                'original_price': oprice,
                'img_link': img_link,
                'product_link': product,
                'reviews_count': reviews_count,
                'reviews_detail': revwDict,
                'attributes': attributes,
                'category': SUB_CATEGORY,
                'platform': 'BombayShirtCompany',
                'dataDate': datetime.datetime.now().strftime("%d-%m-%Y || %H:%M")
                }
            )

            index += 1

        FINALDATA[SUB_CATEGORY][sort_type] = sample


# MAKING THE JSON FILE FO THE FINAL DATA
with open(f'prodData_BombaySC.json', 'w', encoding="utf-8") as fl:
    fl.write(json.dumps(FINALDATA, indent=1, ensure_ascii=False))

driver.quit()
tm_end = time.time()
total_scrapped = MAX_PRODUCT_FROM_EACH_CATEGORY * len(URL_DICT.keys()) * len(sort_dict.keys())

try:
    print(f'\nTotal Products Scrapped: {total_scrapped}')
    print(f'Total Time Taken: {round((tm_end-tm_start)/60, 2)} Minutes')
    print(f'Time Taken per product: {round(((tm_end-tm_start))/total_scrapped, 2)} Seconds')
finally:
    print('SCRAPPED BOMBAY SHIRT COMPANY!\n')

quit()
