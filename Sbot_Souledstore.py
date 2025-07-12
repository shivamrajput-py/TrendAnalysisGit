# SCRAPPING THE SOULED STORE FOR RAW CULT TREND ANALYSIS AND FORECASTING PROJECT !!

''' RATING, RATING NO. , REVIEWS ,  NO. REVIEWS NOT AVAILABLE ''' #TODO: ATTRIBUTES ERROR

# ALL IMPORT IMPORTS
import time, json, datetime
tm_start = time.time()
from selenium import webdriver
from selenium.webdriver.common.by import By
from runBot_TA import *

# THE SUB CATOGORIES OF MYNTRA YOU WANT TO SCRAPE! PUT THE LINKS HERE
URL_DICT = TO_SCRAPE_URL_DICT['TheSouledStore']
MAX_PRODUCT_FROM_EACH_CATEGORY = NO_OF_PRODUCTS_TO_SCRAPE['TheSouledStore']
HEADLESS_BROWSER = False
scroll_pause_time = 1.5 # According to your Internet Speed
IMPLICIT_WAIT = 0.5

# SORTINGS
sort_dict = {
    'Recommended': 'DEFAULT',
    'Popularity': 'POPULARITY',
    'Freshness': 'LATEST'
}

# CONSTANTS
scroll_height_step = 1000
FINALDATA = {}
scroll_count = int(MAX_PRODUCT_FROM_EACH_CATEGORY / 8) + 1  # Set the maximum number of scrolls

# TSS: DETAILS CRAP BOX FOR ATTRIBUTES CLEANING
details_crap = []

# CHROME OPTIONS FOR SCRAPING SELENIUM
options = webdriver.ChromeOptions()
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument("--start-maximized")
if HEADLESS_BROWSER: options.add_argument('--headless=new')

# SETTING UP CHROME DRIVER FOR CHROME SCRAPPING
driver = webdriver.Chrome(options=options)
driver.implicitly_wait(IMPLICIT_WAIT)

# MAIN URL LOOP FOR THE SCRAPPER !
for SUB_CATEGORY in URL_DICT:

    FINALDATA[SUB_CATEGORY] = {}

    for sort_type in sort_dict.keys():

        # ACCORDING TO THE SORTING , GOING TO THE WEBSITE PAGE TO SCRAPE
        driver.get(URL_DICT[SUB_CATEGORY] + f'?page={scroll_count}&filters=sort%7C%7C' + sort_dict[sort_type])

        # SETTING UP LOOP VARIABLE TO THE INITAL VALUES
        FINALDATA[SUB_CATEGORY][sort_type] = []
        sample = []
        productList = []

        print(f'[The Souled Store] >> {SUB_CATEGORY} >> {sort_type}\n')

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

        for e, elm in enumerate(driver.find_elements(By.CSS_SELECTOR, '.col-lg-3.col-md-6.col-6.animate-card')):
            if e+1> MAX_PRODUCT_FROM_EACH_CATEGORY: break
            try:
                productList.append([elm.find_element(By.XPATH, 'div/a').get_attribute('href'),
                                    elm.find_element(By.XPATH, 'div/a/div/img').get_attribute('src')])
            except:
                continue

        # NOW SCRAPPING EACH PRODUCT
        index = 1
        for product in productList:
            img_link = product[1]
            product = product[0]
            driver.get(product)

            # BRAND *
            brand = 'TheSouledStore'

            # TITLE *
            try:
                title = driver.find_element(By.CSS_SELECTOR, '.fbold.mb-0.title-size').text
            except:
                print(f'Title error in: {product}')
                continue

            # CURRENT PRICE *
            try:
                price_line = driver.find_element(By.CSS_SELECTOR, '.leftPrice.pull-right').text
                price_line = price_line.split(' ')
                # print(price_line)

                if len(price_line) == 2:
                    price = int(convert_to_number(price_line[1]))
                    original_price = int(convert_to_number(price_line[1]))

                if len(price_line) >= 4:
                    price = int(convert_to_number(price_line[1]))
                    original_price = int(convert_to_number(price_line[3]))

            except Exception as e:
                print(f'Price error in: {product}')
                continue

            # RATING & RATING DETAILS AND REVIEWS ALL ARE NOT AVAILABLE IN MOST OF THE PRODUCTS IN SOULED STORE
            rating, ratings_count, reviews_count, revwDict = None, None, None, {}

            driver.execute_script(f"window.scrollTo(0, 600);")
            time.sleep(0.25)

            try:
                driver.find_element(By.ID, 'headingOne').click()
            except:
                pass

            # PRODUCT DETAILS VALUES - ATTRIBUTES
            attributes = []
            try:
                info = driver.find_element(By.ID, 'collapseOne').text
                attributes = info.split('\n\n')[0].replace('\n', ' ').split(' ')
                print(attributes)
            except:
                attributes = []
                print(f'Attributes error in: {product}')

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
                'platform': 'TheSouledStore',
                'dataDate': datetime.datetime.now().strftime("%d-%m-%Y || %H:%M")

            })

            index += 1

        FINALDATA[SUB_CATEGORY][sort_type] = sample

# MAKING THE JSON FILE FO THE FINAL DATA
with open(f'prodData_Souledstore.json', 'w', encoding="utf-8") as fl:
    fl.write(json.dumps(FINALDATA, indent=2, ensure_ascii=False))

driver.quit()
tm_end = time.time()
total_scrapped = MAX_PRODUCT_FROM_EACH_CATEGORY * len(URL_DICT.keys()) * len(sort_dict.keys())
try:
    print(f'\nTotal Products Scrapped: {total_scrapped}')
    print(f'Total Time Taken: {round((tm_end - tm_start) / 60, 2)} Minutes')
    print(f'Time Taken per product: {round(((tm_end - tm_start)) / total_scrapped, 2)} Seconds')
finally:
    print('SCRAPPED THE SOULED STORE!\n')

quit()
