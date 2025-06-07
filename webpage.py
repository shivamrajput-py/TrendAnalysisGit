import streamlit as st
import json
import pandas as pd

# FUNCTION THAT CONVERTS NUMBERS TO SHORT FORMAT STR NUMBER
def number_Str(number):
    if not str(number).replace('.', '').isnumeric():
        return number

    if number >= 10 ** 7:
        return f"{number / 10 ** 7:.1f} Cr."
    elif number >= 10 ** 5:
        return f"{number / 10 ** 5:.1f} Lakh"
    elif number >= 10 ** 3:
        return f"{number / 10 ** 3:.1f} k"
    else:
        return int(number)

# SETTING UP INITIAL CONFIGS
st.set_page_config(page_title="Trend Analysis By Rawcult", page_icon=":tshirt:", layout="wide")

# DETAILED PRODUCT INFO POPUP
@st.experimental_dialog("Product Details", width="large")
def product_detail_popup(product):
    import streamlit as st

    @st.experimental_dialog("Product Details", width="large")
    def product_detail_popup(product):
        product_found = product  # Assigning product details

        # UI Styling
        st.markdown(
            """
            <style>
                .product-container {
                    display: flex;
                    gap: 20px;
                    align-items: flex-start;
                    border-radius: 12px;
                    background-color: #f9f9f9;
                    padding: 20px;
                    box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
                }
                .product-img {
                    border-radius: 10px;
                    max-width: 250px;
                    height: auto;
                    object-fit: contain;
                    border: 2px solid #ddd;
                }
                .product-info {
                    flex: 1;
                }
                .product-header {
                    font-size: 22px;
                    font-weight: bold;
                    margin-bottom: 10px;
                    color: #333;
                }
                .product-subtext {
                    font-size: 16px;
                    color: #555;
                }
                .highlight {
                    font-weight: bold;
                    color: #ff4b4b;
                }
                .button-container {
                    margin-top: 15px;
                }
                .stButton>button {
                    width: 100%;
                    padding: 8px;
                    border-radius: 6px;
                    font-size: 16px;
                }
            </style>
            """, unsafe_allow_html=True
        )

        # Container for Image + Info
        st.markdown('<div class="product-container">', unsafe_allow_html=True)

        # Image Section
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(product_found['img_link'], use_column_width=True, caption="Product Image", output_format="JPEG")

        # Product Details
        with col2:
            st.markdown(f'<div class="product-header">{product_found["title"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="product-subtext"><b>Brand:</b> {product_found["brand"]}</div>',
                        unsafe_allow_html=True)
            st.markdown(f'<div class="product-subtext"><b>Platform:</b> {product_found["platform"]}</div>',
                        unsafe_allow_html=True)
            st.markdown(
                f'<div class="product-subtext"><b>Rating:</b> ⭐ {product_found["rating_outof5"]} | <b>Ratings:</b> {product_found["ratings_count"]} | <b>Reviews:</b> {product_found["reviews_count"]}</div>',
                unsafe_allow_html=True)
            st.markdown(
                f'<div class="product-subtext"><b>Price:</b> ₹{product_found["current_price"]} (<s>₹{product_found["original_price"]}</s>)</div>',
                unsafe_allow_html=True)
            st.markdown(
                f'<div class="product-subtext"><b>Composite Score:</b> {product_found["composite_score"]}</div>',
                unsafe_allow_html=True)
            st.markdown(f'<div class="product-subtext"><b>Adjusted Rank:</b> {product_found["adjusted_rank"]}</div>',
                        unsafe_allow_html=True)
            st.markdown(
                f'<div class="product-subtext"><b>Attributes:</b> {", ".join(product_found["attribute_tokenset"])}</div>',
                unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)  # Close product container

        # Buttons for Viewing Image and Product
        col3, col4 = st.columns(2)
        with col3:
            st.markdown(
                f'<a href="{product_found["img_link"]}" target="_blank"><button class="stButton">🔍 View Image</button></a>',
                unsafe_allow_html=True)
        with col4:
            st.markdown(
                f'<a href="https://www.example.com/product/{product_found["product_id"]}" target="_blank"><button class="stButton">🛒 View Product</button></a>',
                unsafe_allow_html=True)


# LOAD JSON DATA
with open('trend_analysis_men-tshirts.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

available_categories = ['men-tshirts']

# ------------------------------------- SIDEBAR: CATEGORY SELECTION -------------------------

st.sidebar.title("Trend Analysis By Rawcult")
selected_category = st.sidebar.selectbox(
    "CHOOSE A CATEGORY:",
    available_categories,
    help="If a category is missing, scrape its data first."
)

# Extract data from JSON
category_rankings = data["category_rankings"]
overall_ranking = pd.DataFrame(data["overall_ranking"])

# ------------------------------------- SIDEBAR: SORTING SELECTION -------------------------

sorting_group = st.sidebar.selectbox(
    "SORT BY:",
    list(category_rankings.keys()) + ["Overall Ranking"]
)

all_attributes = {"round", "red", "oversized", "skinny", "straight", "cotton", "lenin", "gym", 'typographic', 'uspolo',
                  'striped', 'sporty', 'name-tees'}

# Sidebar: Attribute Filtering
st.sidebar.title("ATTRIBUTES")
if "selected_attributes" not in st.session_state:
    st.session_state["selected_attributes"] = []

def update_attributes(selected):
    st.session_state["selected_attributes"] = selected

# Sidebar: Attribute Selection Mode
attribute_mode = st.sidebar.selectbox(
    "CHOOSE ATTRIBUTE MODE:",
    ("Predefined Attributes", "Enter Your Own Attributes", "All Available Attributes"),
    index=1,
    help="Choose whether to use predefined attributes or input your own."
)

# Attribute Selection Logic
if attribute_mode == "Predefined Attributes":
    # Predefined attribute multiselect
    selected_attributes = st.sidebar.multiselect(
        "SELECT ATTRIBUTES", all_attributes, default=st.session_state["selected_attributes"]
    )

elif attribute_mode == "All Available Attributes":
    unique_attributes = set()
    for group in category_rankings.values():
        for product in group:
            unique_attributes.update(set(product.get("attribute_tokenset", [])))
    selected_attributes = st.sidebar.multiselect(
        "SELECT ATTRIBUTES", set(unique_attributes), default=st.session_state["selected_attributes"]
    )

else:
    # Custom attribute input
    custom_attributes_input = st.sidebar.text_area(
        "Enter Attributes (space-separated)",
        placeholder="e.g., cotton round oversized",
    )
    selected_attributes = custom_attributes_input.split()

# Function to Filter Products by Attributes (Intersection)
def filter_products_by_attributes(products, attributes):
    if not attributes:
        return products
    filtered_products = []
    products = products.to_dict()
    for product in products:
        if set(attributes).issubset(set(product.get("attribute_tokenset", []))):  # Ensure intersection
            filtered_products.append(product)
    return filtered_products

# Enhance UI Styling
with open("style.css") as f:
    st.markdown(f"""<style>{f.read()}</style>""", unsafe_allow_html=True)

# Main Content
st.markdown("<div><h3 style='text-align: center;'>Trend Analysis By Rawcult</h3></div>", unsafe_allow_html=True)

# Product ID Search Page
st.sidebar.subheader("Product ID Search")
product_id = st.sidebar.text_input("Enter Product ID", "")


def calculate_composite_score(row):
    sorting_type = row['sorting']
    rating = row['rating_outof5']
    n = row['ratings_count']
    rank = row['sorting_rank']
    review_score = row['reviews_score']

    if sorting_type == 'Recommended':
        score = 0.5 * (rating * n) / (n + 50) + 0.3 * (1 / rank) + 0.2 * review_score
        formula = f"0.45 * ({rating} * {n}) / ({n} + 50) + 0.3 * (1 / {rank}) + 0.25 * {review_score}"

    elif sorting_type == 'Popularity':
        score = 0.4 * (rating * n) / (n + 50) + 0.35 * (1 / rank) + 0.25 * review_score
        formula = f"0.4 * ({rating} * {n}) / ({n} + 50) + 0.4 * (1 / {rank}) + 0.2 * {review_score}"

    elif sorting_type == 'Freshness':
        score = 0.3 * (rating * n) / (n + 50) + 0.5 * (1 / rank) + 0.2 * review_score
        formula = f"0.2 * ({rating} * {n}) / ({n} + 50) + 0.7 * (1 / {rank}) + 0.1 * {review_score}"

    elif sorting_type == 'Feedback':
        score = 0.5 * (rating * n) / (n + 50) + 0.2 * (1 / rank) + 0.3 * review_score
        formula = f"0.5 * ({rating} * {n}) / ({n} + 50) + 0.35 * (1 / {rank}) + 0.15 * {review_score}"

    else:
        score = 0  # Fallback if no match
        formula = "No formula applied"

    # Return both score and formula
    return pd.Series([score, formula])


st.sidebar.slider('Rating Weights', min_value=0.0, max_value=1.0, step=0.1, key='rating_weights')
st.sidebar.slider('Rank Weights', min_value=0.0, max_value=1.0, step=0.1, key='rank_weights')
st.sidebar.slider('Review Weights', min_value=0.0, max_value=1.0, step=0.1, key='Review_weights')


# Sorting and displaying products
if sorting_group != "Overall Ranking":
    st.markdown(f"##### Products in {sorting_group} ({len(category_rankings[sorting_group])} results) - {selected_category} category")
    group_data = category_rankings[sorting_group]
    group_data = pd.DataFrame(group_data)
    # Apply Composite Score and Store Formula
    group_data[['composite_score', 'score_calculator']] = group_data.apply(calculate_composite_score, axis=1)

    # Filter products dynamically
    filtered_data = filter_products_by_attributes(group_data, selected_attributes)

    if filtered_data.isnull().values.any():
        st.warning("No products match the selected attributes.")
    else:
        for rnk, product in enumerate(filtered_data):

            atr = ''
            lennn = len(product.get("attribute_tokenset", []))
            for j,strr in enumerate(product['attribute_tokenset']):
                if j<35:
                    atr += strr + ' | '
                else:
                    atr += f"... {lennn-j+1} more"
                    break

            revw_str = 'Recent Reviews:\n\n'
            review_count = 0
            for i in range(1, 4):
                review = product.get(f'reviews_detail.{i}', '')
                if review and str(review) != 'nan':
                    revw_str += f"{i}. {str(review)[:110].replace('#', '')}...\n"
                    review_count += 1
            revw_str = revw_str if review_count > 0 else ''



            st.markdown(
                f"""
                <div class="product-box">
                    <div class="product-left">
                        <div class="imgbox"><img src="{product['img_link']}" class="product-image" /></div>
                        <div class="product-details">
                            <div class="product-title">#{rnk+1} | {product['title']}</div>
                            <div class="product-brand">Brand: {product['brand']} | Platform: {product['platform']}</div>
                            <div class="product-rating">{product['rating_outof5']}⭐ | {number_Str(product['ratings_count'])} | {number_Str(product['reviews_count'])} Reviews.</div>
                            <div class="product-composite-score">Score: {round(product['composite_score'],2)}</div>
                            <div class="other-stats">Ranked: #{product['sorting_rank']} in [{product['sorting']}][{product['platform']}]</div>
                            <div class="product-price">Price: ₹{product['current_price']} (Original: ₹{product['original_price']})</div>
                            <div class="product-links">
                                <a href="{product['img_link']}" target="_blank">View Image</a> | 
                                <a href="{product['product_link']}" target="_blank">View Product</a>
                            </div>
                        </div>
                    </div>
                    <div class="product-right">
                        <div class="product-attributes">Attribute-Tokens: {atr}</div>
                        <div class="product-attributes">{revw_str}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            bt = st.button(f'#{rnk+1}th PRODUCT FULL INFO...', key=f'{product["product_id"]}{rnk+1}{product['sorting_rank']}')
            if bt:
                product_detail_popup(product)
            # Modify the "else" block for Overall Ranking (replace existing code)
else:
    st.subheader("Overall Rankings")
    filtered_data = filter_products_by_attributes(overall_ranking.to_dict(orient="records"),
                                          selected_attributes)

    if not filtered_data:
        st.warning("No products match the selected attributes.")
    else:
        for rnk, product in enumerate(filtered_data):

            # Attribute string formatting
            atr = ''
            lennn = len(product.get("attribute_tokenset", []))
            for j, strr in enumerate(product.get("attribute_tokenset", [])):
                if j < 35:
                    atr += strr + ' | '
                else:
                    atr += f"... {lennn - j + 1} more"
                    break

            # Review string formatting (only if reviews exist)
            revw_str = ''
            reviews_exist = False
            revw_str = 'Recent Reviews:\n\n'
            review_count = 0
            for i in range(1, 4):
                review = product.get(f'reviews_detail.{i}', '')
                if review and str(review) != 'nan':
                    revw_str += f"{i}. {str(review)[:110].replace('#', '')}...\n"
                    review_count += 1
            if review_count == 0:
                revw_str = ''

            st.markdown(
                f"""
                    <div class="product-box">
                        <div class="product-left">
                            <div class="imgbox"><img src="{product['img_link']}" class="product-image" /></div>
                            <div class="product-details">
                                <div class="product-title">#{rnk + 1} | {product['title']}</div>
                                <div class="product-brand">Brand: {product['brand']} | Platform: {product['platform']}</div>
                                <div class="product-rating">{product['rating_outof5']}⭐ | {number_Str(product['ratings_count'])} | {number_Str(product['reviews_count'])} Reviews.</div>
                                <div class="product-composite-score">Score: {round(product['composite_score'], 2)}</div>
                                <div class="other-stats">Ranked: #{product.get('sorting_rank', 'N/A')} in [{product.get('sorting', '')}][{product['platform']}]</div>
                                <div class="product-price">Price: ₹{product['current_price']} (Original: ₹{product['original_price']})</div>
                                <div class="product-links">
                                    <a href="{product['img_link']}" target="_blank">View Image</a> | 
                                    <button class="detail-button" onclick="document.getElementById('product-detail-{product['product_id']}').style.display='block'">View Details</button>
                                </div>
                            </div>
                        </div>
                        <div class="product-right">
                            {f'<div class="product-attributes">Attribute-Tokens: {atr}</div>' if atr else ''}
                            {f'<div class="product-attributes">{revw_str}</div>' if revw_str else ''}
                        </div>
                    </div>
                    """,
                unsafe_allow_html=True,
            )




# PRODUCT SEARCH BY ID PAGE
if product_id:
    product_found = None
    # Searching for product by Product ID
    for product in overall_ranking.to_dict(orient="records"):
        if product['product_id'] == product_id:
            product_found = product
            break

    if product_found:
        # Display product details
        st.subheader(f"Product Details for ID: {product_id}")
        st.image(product_found['img_link'], width=250)

        st.markdown(f"**Title:** {product_found['title']}")
        st.markdown(f"**Brand:** {product_found['brand']}")
        st.markdown(f"**Platform:** {product_found['platform']}")
        st.markdown(f"**Rating:** {product_found['rating_outof5']} | **Rating Count:** {product_found['ratings_count']} | **Reviews Count:** {product_found['reviews_count']}")
        st.markdown(f"**Price:** ₹{product_found['current_price']} (Original: ₹{product_found['original_price']})")
        st.markdown(f"**Composite Score:** {product_found['composite_score']}")
        st.markdown(f"**Adjusted Rank:** {product_found['adjusted_rank']}")
        st.markdown(f"**Attributes:** {', '.join(product_found['attribute_tokenset'])}")

        # Buttons for viewing image and actual product
        st.markdown(f"[**View Image**]({product_found['img_link']})")
        st.markdown(f"[**View Product**](https://www.example.com/product/{product_id})")

    else:
        st.warning("No product found with the given ID.")