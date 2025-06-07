# SCRAPPING TATACLIQ FOR RAW CULT TREND ANALYSIS AND FORECASTING PROJECT !!
# - SHIVAM RAJPUT # COMPLETED 85% # LAST UPDATED - 27-12-night
''' WRITTEN REVIEWS AND REVIEWS COUNT ARE NOT THERE IN TATACLIQ'''

# ALL IMPORT IMPORTS
import time, json
tm_start = time.time()
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from runBot_TA import *

# THE SUB CATOGORIES OF MYNTRA YOU WANT TO SCRAPE! PUT THE LINKS HERE
URL_DICT = {
    'men-tshirts': 'https://www.tatacliq.com/mens-clothing-casual-wear-t-shirts-polos/c-msh1116100?q=%3Arelevance%3Acategory%3AMSH1116100%3AinStockFlag%3Atrue%3Adisplay-classification%3APolo+T-Shirts%3Adisplay-classification%3APolo+T-Shirt%3Adisplay-classification%3APolo%2BT-shirts&icid2=regu:nav:main:mnav:m1116100:mulb:best:09:R3'
}

# EDITABLE CONSTANTS
MAX_PRODUCT_FROM_EACH_CATEGORY = NO_OF_PRODUCTS_TO_SCRAPE
HEADLESS_BROWSER = False
scroll_pause_time = 1.5 # According to your Internet Speed
IMPLICIT_WAIT = 0.5

sort_dict = {
    'Popularity': 'relevance',
    'Freshness': 'isProductNew'
}

# CONSTANTS
scroll_height_step = 1000
FINALDATA = {}
scroll_count = int(MAX_PRODUCT_FROM_EACH_CATEGORY / 8) + 1  # Set the maximum number of scrolls

#TODO: a lot to put in here cause of that short description thing
details_crap = []

options = webdriver.ChromeOptions()
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument("--start-maximized")
if HEADLESS_BROWSER: options.add_argument('--headless=new')

driver = webdriver.Chrome(options=options)
driver.implicitly_wait(IMPLICIT_WAIT)

# MAIN URL LOOP FOR THE SCRAPPER !
for SUB_CATEGORY in URL_DICT:

    FINALDATA[SUB_CATEGORY] = {}

    for sort_type in sort_dict.keys():

        # ACCORDING TO THE SORTING , GOING TO THE WEBSITE PAGE TO SCRAPE
        driver.get(URL_DICT[SUB_CATEGORY].replace('relevance', sort_dict[sort_type]))

        # SETTING UP LOOP VARIABLE TO THE INITAL VALUES
        FINALDATA[SUB_CATEGORY][sort_type] = []
        sample = []
        productList = []

        # TRYING TO CANCEL THAT POPUP
        try:
            driver.find_element(By.ID, 'wzrk-cancel').click()
        except:
            pass

        print(f'[TATACLIQ] >> {SUB_CATEGORY} >> {sort_type}\n')

        # SCROLL TILL WHAT NECESSARY
        step = 0
        current_scroll = 0
        while True:
            if current_scroll <= scroll_count:
                if (current_scroll+1) % 5 == 0:
                    button = driver.find_element(By.CLASS_NAME, 'ShowMoreButtonPlp__button')
                    driver.execute_script("arguments[0].click();", button)
                    time.sleep(2)
                driver.execute_script(f"window.scrollTo(0, {step});")
                time.sleep(scroll_pause_time)
                step += scroll_height_step
                current_scroll += 1
            else:
                break

        for elm in driver.find_elements(By.XPATH, '//div[contains(@class, "PlpComponent__base")]'):
            try:
                productList.append(elm.find_element(By.XPATH, 'div/a').get_attribute('href'))
            except:
                continue

        # -----------------------------------------------------------------------------------------

        # NOW SCRAPPING EACH PRODUCT
        index = 1
        for product in productList:

            if index>MAX_PRODUCT_FROM_EACH_CATEGORY: break

            driver.get(product)

            # IMAGE LINK *
            try:
                img_link = driver.find_element(By.CSS_SELECTOR, '.ProductGalleryDesktopUpdated__images').get_attribute('src')
            except:
                try:
                    img_link = driver.find_element(By.CSS_SELECTOR, '.ProductGalleryDesktopUpdated__imgBoxFirst')
                    img_link = img_link.find_element(By.TAG_NAME, 'img').get_attribute('src')
                except:
                    try:
                        img_link = driver.find_element(By.ID, 'pg-image-multiple-0')
                        img_link = img_link.find_element(By.TAG_NAME, 'img').get_attribute('src')
                    except:
                        print(f'Image Link Error in {product}')
                        img_link = None

            # BRAND *
            try:
                brand = driver.find_element(By.ID, 'pd-brand-name').text
            except:
                try:
                    brand = driver.find_element(By.CLASS_NAME, 'ProductDetailsMainCard__brandName').text
                except:
                    print(f'Brand Name error in: {product}')
                    brand = None

            # TITLE *
            try:
                title = driver.find_element(By.CSS_SELECTOR, '.ProductDetailsMainCard__productName').text
            except:
                print(f'Title error in: {product}')
                title = None

            # CURRENT PRICE *
            try:
                price = driver.find_element(By.CSS_SELECTOR, '.ProductDetailsMainCard__price').text

                # EXTRACTING
                price = price.replace('₹', '').replace(',', '').replace('MRP:', '')
                if price.replace('.', '').isnumeric():
                    price = int(float(price))
                else:
                    price = price

            except:
                print(f'Price error in: {product}')
                price = None


            # ORIGINAL PRICE
            try:
                oprice = driver.find_element(By.CSS_SELECTOR, '.ProductDetailsMainCard__cancelPrice').text

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
                rating_info = driver.find_element(By.CSS_SELECTOR, '.ProductDetailsMainCard__labelText').text

                # EXTRACTING REQUIRED DATA.
                ratings_count = rating_info.split('Ratings')[0].strip()
                ratings_count = rating_info.split('Rating')[0].strip()
                if convert_to_number(ratings_count).replace(',', '').replace('.', '').isnumeric():
                    ratings_count = int(convert_to_number(ratings_count).replace(',', ''))
                else:
                    ratings_count = convert_to_number(ratings_count).replace(',', '')

                reviews_count = None
                revwDict = {}

            except:
                ratings_count = None
                reviews_count = None
                revwDict = {}

            # RATINGS NUMBER
            try:
                rating = driver.find_element(By.CSS_SELECTOR, '.ProductDetailsMainCard__reviewElectronics').text

                # EXTRACTING
                if rating.replace('.', '').isnumeric():
                    rating = round(float(rating), 1)
                else:
                    rating = rating

            except:
                rating = None


            # PRODUCT DETAILS VALUES - ATTRIBUTES
            attributes = []
            try:
                for j in driver.find_elements(By.CSS_SELECTOR, '.Accordion__shortDescription'):
                    attributes.append(j.text)
                for k in driver.find_elements(By.CSS_SELECTOR, '.Accordion__contentDetailsPDP'):
                    attributes.extend(k.text.split('\n'))
            except:
                attributes = []

            # ATTRIBUTE FORMATTING
            attributes = [
                [word for word in line.lower().strip().split() if word not in details_crap]
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
                'original_price': original_price,
                'img_link': img_link,
                'product_link': product,
                'reviews_count': reviews_count,
                'reviews_detail': revwDict,
                'attributes': attributes,
                'category': SUB_CATEGORY,
                'platform': 'Tatacliq',
                }
            )

            index += 1

        FINALDATA[SUB_CATEGORY][sort_type] = sample

smpdt = FINALDATA[SUB_CATEGORY]['Popularity']
for dt in smpdt: dt['sorting'] = 'Recommended'
FINALDATA[SUB_CATEGORY]['Recommended'] = smpdt

# MAKING THE JSON FILE FO THE FINAL DATA
with open(f'prodData_Tatacliq.json', 'w', encoding="utf-8") as fl:
    fl.write(json.dumps(FINALDATA, indent=2, ensure_ascii=False))

driver.quit()
tm_end = time.time()
total_scrapped = MAX_PRODUCT_FROM_EACH_CATEGORY * len(URL_DICT.keys()) * len(sort_dict.keys())
try:
    print(f'\nTotal Products Scrapped: {total_scrapped}')
    print(f'Total Time Taken: {round((tm_end-tm_start)/60, 2)} Minutes')
    print(f'Time Taken per product: {round(((tm_end-tm_start))/total_scrapped, 2)} Seconds')
finally:
    print('SCRAPPED TATACLIQ!\n')

quit()
