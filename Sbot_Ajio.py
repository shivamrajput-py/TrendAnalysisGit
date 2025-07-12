'''DATA SCRAPPING BOT [AJIO] FOR RAWCULT TREND-ANALYSIS
~ SHIVAM RAJPUT [NOTE- WRITTEN REVIEWS ARE NOT THERE IN AJIO]'''

# SORTINGS DICTIONARY ACCORDING TO THE SOURCE URL
sort_dict = {
    'Recommended': 'relevance',
    'Freshness': 'newn',
    'Feedback': 'rating'
}

# IMPORTANT PARAMETERS
from runBot_TA import *
MAX_PRODUCT_FROM_EACH_CATEGORY = NO_OF_PRODUCTS_TO_SCRAPE['Ajio']
URL_DICT = TO_SCRAPE_URL_DICT['Ajio']
HEADLESS_BROWSER = False
scroll_pause_time = 1.5 # According to your Internet Speed
IMPLICIT_WAIT = 0.5

#-------------------------------------------------------------------------------------------------------------

# ALL IMPORTANTS IMPORTS
import time, json, ssl
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

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.ajio.com/"
}

# SETTING UP CHROME OPTIONS AND THE KEY PARAMETERS
import undetected_chromedriver as uc

options = uc.ChromeOptions()
options.add_argument('--ignore-ssl-errors=yes')
options.add_argument('--ignore-certificate-errors')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")

#-----------------------------------------------------------------------------------------------------------------------

# SETTING UP CHROME DRIVER FOR CHROME SCRAPPING
driver = uc.Chrome(options=options)
driver.implicitly_wait(IMPLICIT_WAIT)

# MAIN URL LOOP FOR THE SCRAPPER !
for SUB_CATEGORY in URL_DICT:

    FINALDATA[SUB_CATEGORY] = {}

    for sort_type in sort_dict.keys():

        # ACCORDING TO THE SORTING , GOING TO THE WEBSITE PAGE TO SCRAPE
        driver.get(URL_DICT[SUB_CATEGORY] + f'?query=%3A{sort_dict[sort_type]}&gridColumns=3')

        # SETTING UP LOOP VARIABLE TO THE INITAL VALUES
        FINALDATA[SUB_CATEGORY][sort_type] = []
        sample = []
        productList = []

        print(f'[AJIO] >> {SUB_CATEGORY} >> {sort_type}\n')

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
        for i in range(0, (MAX_PRODUCT_FROM_EACH_CATEGORY//3 + 1)):
            for j, elm in enumerate(driver.find_elements(By.ID, f'{i}')):

                if i == (MAX_PRODUCT_FROM_EACH_CATEGORY//3):
                    if j == (MAX_PRODUCT_FROM_EACH_CATEGORY%3): break

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
                img_link = driver.find_element(By.CSS_SELECTOR, '.img-container').find_element(By.TAG_NAME, 'img').get_attribute('src')
            except:
                print(f'Image Link Error in {product}')
                continue

            # BRAND *
            try:
                brand = driver.find_element(By.CLASS_NAME, 'brand-name').text
            except:
                print(f'Brand Name error in: {product}')
                continue

            # TITLE *
            try:
                title = driver.find_element(By.CLASS_NAME, 'prod-name').text
            except:
                print(f'Title error in: {product}')
                continue

            # CURRENT PRICE *
            try:
                price = driver.find_element(By.CSS_SELECTOR, '.prod-sp').text

                # EXTRACTING
                price = price.replace('₹', '').replace(',', '').replace('MRP', '')
                if price.replace('.', '').isnumeric():
                    price = int(float(price))
                else:
                    price = price

            except:
                print(f'Price error in: {product}')
                price = None

            # ORIGINAL PRICE
            try:
                oprice = driver.find_element(By.CSS_SELECTOR, '.prod-cp').text

                # EXTRACTING
                oprice = oprice.replace('₹', '').replace(',', '')
                if oprice.replace('.', '').isnumeric():
                    oprice = int(float(oprice))
                else:
                    oprice = oprice

                original_price = oprice
            except:
                original_price = price

            # RATING INFO
            try:
                rating_info = driver.find_element(By.CSS_SELECTOR, '._1jiCk.rating-label-star-count').text

                # EXTRACTING REQUIRED DATA.
                rating_counts = rating_info.split('Ratings')[0].strip()
                rating_counts = int(convert_to_number(rating_counts.lower()))

                review_counts = None
                revwDict = {}

            except:
                rating_counts = None
                review_counts = None
                revwDict = {}

            # RATINGS NUMBER
            try:
                rating = driver.find_element(By.CSS_SELECTOR, '._1jiCk._3iz7j').text

                # EXTRACTING
                if rating.replace('.', '').isnumeric():
                    rating = round(float(rating), 1)
                else:
                    rating = rating

            except:
                rating = None

            driver.execute_script(f"window.scrollTo(0, 300);")
            time.sleep(0.25)

            # PRODUCT DETAILS VALUES - ATTRIBUTES
            attributes = []
            try:
                for j in driver.find_elements(By.CSS_SELECTOR, '.detail-list'):
                    attributes.append(j.text)
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
                'ratings_count': rating_counts,
                'current_price': price,
                'original_price': original_price,
                'img_link': img_link,
                'product_link': product,
                'reviews_count': review_counts,
                'reviews_detail': revwDict,
                'attributes': attributes,
                'category': SUB_CATEGORY,
                'platform': 'Ajio'
                }
            )

            index += 1

        FINALDATA[SUB_CATEGORY][sort_type] = sample


# MAKING THE JSON FILE FO THE FINAL DATA
with open(f'prodData_Ajio.json', 'w', encoding="utf-8") as fl:
    fl.write(json.dumps(FINALDATA, indent=1, ensure_ascii=False))

driver.quit()
tm_end = time.time()
total_scrapped = MAX_PRODUCT_FROM_EACH_CATEGORY * len(URL_DICT.keys()) * len(sort_dict.keys())

try:
    print(f'\nTotal Products Scrapped: {total_scrapped}')
    print(f'Total Time Taken: {round((tm_end-tm_start)/60, 2)} Minutes')
    print(f'Time Taken per product: {round(((tm_end-tm_start))/total_scrapped, 2)} Seconds')
finally:
    print('SCRAPPED AJIO!\n')

quit()
