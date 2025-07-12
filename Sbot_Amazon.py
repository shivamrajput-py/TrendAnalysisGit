'''DATA SCRAPPING BOT [AMAZON] FOR RAWCULT TREND-ANALYSIS
~ SHIVAM RAJPUT [REVIEWS COUNT IS NOT VISIBLE TILL YOU LOGIN]'''

# SORTINGS DICTIONARY ACCORDING TO THE SOURCE URL
sort_dict = {
    'Recommended': 'Featured',
    'Popularity' : 'Best Sellers',
    'Freshness' : 'Newest Arrivals',
    'Feedback': 'Avg. Customer Review'
}

# IMPORTANT PARAMETERS
from runBot_TA import *
MAX_PRODUCT_FROM_EACH_CATEGORY = NO_OF_PRODUCTS_TO_SCRAPE['Amazon']
URL_DICT = TO_SCRAPE_URL_DICT['Amazon']
HEADLESS_BROWSER = False
scroll_pause_time = 1.8 # According to your Internet Speed
IMPLICIT_WAIT = 0.5

#-------------------------------------------------------------------------------------------------------------

# ALL IMPORT IMPORTS
import time, json, ssl, datetime
tm_start = time.time()
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# CONSTANTS
scroll_height_step = 1000
FINALDATA = {}
no_scrolls = int(MAX_PRODUCT_FROM_EACH_CATEGORY/51) # 40 products per scroll

if MAX_PRODUCT_FROM_EACH_CATEGORY==51: no_scrolls = 0

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

# MAIN URL LOOP FOR THE BOT !
for SUB_CATEGORY in URL_DICT.keys():

    FINALDATA[SUB_CATEGORY] = {}

    for sort_type in sort_dict.keys():

        # ACCORDING TO THE SORTING , GOING TO THE WEBSITE PAGE TO SCRAPE
        driver.get(URL_DICT[SUB_CATEGORY])
        try:
            driver.find_element(By.ID, 'a-autoid-0-announce').click()
            # driver.find_element(By.XPATH, f'//*[@id="a-popover-2"]/div/div/ul/li[3]').click()
            driver.find_element(By.LINK_TEXT, f'{sort_dict[sort_type]}').click()
            time.sleep(0.5)
        except Exception as e:
            print(f'Some error in Scrapping {sort_type} | AMAZON \n{e}')
            continue

        # SETTING UP LOOP VARIABLE TO THE INITAL VALUES
        FINALDATA[SUB_CATEGORY][sort_type] = []
        sample = []
        productList = []

        print(f'[AMAZON] >> {SUB_CATEGORY} >> {sort_type}\n')

        for page in range(0, no_scrolls+1):
            if page>0:
                driver.find_element(By.LINK_TEXT, 'Next').click()
                time.sleep(0.7)

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

            for q,elm in enumerate(driver.find_elements(By.CSS_SELECTOR, '.a-link-normal.s-no-outline')):
                if q>MAX_PRODUCT_FROM_EACH_CATEGORY: break
                try:
                    productList.append(elm.get_attribute('href'))
                except:
                    continue

        # -----------------------------------------------------------------------------------------

        index = 1
        for product in productList:

            driver.get(product)

            # Wait for the button to be clickable and click it
            try:
                # Most common selectors for Amazon's continue shopping buttons:
                continue_button = WebDriverWait(driver, 1).until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@value='Continue shopping']"))
                )
                continue_button.click()
            except:
                # Alternative selectors to try:
                selectors = [
                    "//button[contains(text(), 'Continue')]",
                    "//a[contains(text(), 'Continue')]",
                    "//input[contains(@value, 'Continue')]",
                    "[data-action='continue-shopping']",
                    ".continue-shopping-button",
                    "#continue-shopping"
                ]

                for selector in selectors:
                    try:
                        if selector.startswith("//"):
                            element = driver.find_element(By.XPATH, selector)
                        else:
                            element = driver.find_element(By.CSS_SELECTOR, selector)
                        element.click()
                        break
                    except:
                        continue

            # IMAGE LINK *
            try:
                img_link = driver.find_element(By.CSS_SELECTOR, '#landingImage').get_attribute('src')
            except:
                print(f'Image Link Error in {product}')
                continue

            # TITLE *
            try:
                title = driver.find_element(By.ID, 'productTitle').text
            except:
                print(f'Title error in: {product}')
                continue

            # BRAND NAME
            brand= ''
            try:
                for k,wrd in enumerate(title.split(' ')):
                    if k<1: brand += wrd + ' '
                brand = brand.strip()
            except:
                brand = None

            # CURRENT PRICE *
            try:
                price = driver.find_element(By.CSS_SELECTOR, '.a-price-whole').text

                # EXTRACTING
                price = price.replace('₹', '').replace(',', '')
                if price.replace('.', '').isnumeric(): price = int(float(price))
                else: price = price

            except:
                print(f'Price error in: {product}')
                price = None

            # ORIGINAL PRICE
            try:
                original_price = driver.find_element(By.CSS_SELECTOR, '.a-price.a-text-price').text
                original_price = original_price.replace('M.R.P.:', '').replace('₹', '').replace(',', '')

                if original_price.replace('.', '').isnumeric():
                    original_price = int(float(original_price))
            except:
                original_price = price

            # RATING INFO
            try:
                rating_info = driver.find_element(By.XPATH, '//*[@id="acrCustomerReviewText"]').text
                # EXTRACTING REQUIRED DATA.
                try:
                    ratings_count = rating_info.replace('ratings', '').replace('rating', '').replace(',', '').strip()
                    ratings_count = int(ratings_count)
                except:
                    ratings_count = rating_info.replace('ratings', '').replace('rating', '').replace(',', '').strip()
            except:
                ratings_count = None


            # RATINGS NUMBER
            try:
                rating = driver.find_element(By.XPATH, '//*[@id="acrPopover"]/span[1]/a/span').text.strip()

                # EXTRACTING
                if rating.replace('.', '').isnumeric(): rating = round(float(rating),1)
                else: rating = rating

            except:
                rating = None

            driver.execute_script(f"window.scrollTo(0, 1000);")
            time.sleep(0.25)

            # PRODUCT DETAILS VALUES - ATTRIBUTES
            attributes = []
            try:
                for j in driver.find_element(By.XPATH, '//*[@id="productFactsDesktopExpander"]').text.split('\n'):
                    attributes.append(j.strip())
            except:
                attributes = []

            # ATTRIBUTE FORMATTING
            attributes = [
                [word for word in line.lower().strip().split()]
                for line in attributes if line.strip()
            ]
            attributes = [attr for attr in attributes if attr]
            attributes = [" ".join(attr) for attr in attributes]

            driver.execute_script(f"window.scrollTo(0, 3000);")
            time.sleep(0.7)

            # WRITTEN REVIEWS
            revwDict = {}
            try:
                for i,k in enumerate(driver.find_elements(By.CSS_SELECTOR, '.a-row.a-spacing-small.review-data')):
                    if i==3: break
                    revwDict[i+1] = k.text.strip()
            except:
                revwDict = {}

            reviews_count = None

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
                'platform': 'Amazon',
                'dataDate': datetime.datetime.now().strftime("%d-%m-%Y || %H:%M"),
            }
            )

            index+= 1

        FINALDATA[SUB_CATEGORY][sort_type] = sample

# MAKING THE JSON FILE FO THE FINAL DATA
with open(f'prodData_Amazon.json', 'w', encoding="utf-8") as fl:
    fl.write(json.dumps(FINALDATA, indent=1, ensure_ascii=False))

driver.quit()
tm_end = time.time()
total_scrapped = MAX_PRODUCT_FROM_EACH_CATEGORY * len(URL_DICT.keys()) * len(sort_dict.keys())

try:
    print(f'\nTotal Products Scrapped: {total_scrapped}')
    print(f'Total Time Taken: {round((tm_end-tm_start)/60, 2)} Minutes')
    print(f'Time Taken per product: {round(((tm_end-tm_start))/total_scrapped, 2)} Seconds')
finally:
    print('SCRAPPED AMAZON!\n')

quit()