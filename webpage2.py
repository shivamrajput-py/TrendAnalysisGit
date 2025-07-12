import streamlit as st
import json
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
import matplotlib.colors as mcolors
from itertools import combinations
from collections import defaultdict
import numpy as np


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
st.set_page_config(
    page_title="Rawcult Trend Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ENHANCED CSS STYLING - SIMPLIFIED HEADER, IMPROVED PRODUCT CARD
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Override Streamlit's default styling */
    .stApp {
        background-color: #0e1117;
    }

    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }

    /* Remove default Streamlit sidebar styling */
    .css-1d391kg, .css-1rs6os, .css-17eq0hr {
        background-color: #262730 !important;
    }

    /* Custom selectbox styling */
    .stSelectbox > div > div {
        background-color: #262730 !important;
        border: 1px solid #4a4a4a !important;
        color: white !important;
    }

    .stMultiSelect > div > div {
        background-color: #262730 !important;
        border: 1px solid #4a4a4a !important;
    }

    .stTextInput > div > div > input {
        background-color: #262730 !important;
        border: 1px solid #4a4a4a !important;
        color: white !important;
    }

    * {
        font-family: 'Inter', sans-serif;
    }

    .main-header {
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 1.5rem;
        color: #4db8ff;
    }

    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
    }

    .product-card {
        background: #262730;
        border-radius: 12px;
        margin: 1rem 0;
        border: 1px solid #4a4a4a;
        transition: all 0.3s ease;
        overflow: hidden;
    }

    .product-card:hover {
        border-color: #4db8ff;
        box-shadow: 0 4px 20px rgba(77, 184, 255, 0.2);
    }

    .product-content {
        display: flex;
        padding: 1.2rem;
        gap: 1.2rem;
    }

    .product-image-section {
        display: flex;
        flex-direction: column;
        gap: 0.8rem;
        min-width: 240px;
    }

    .product-image-container {
        width: 100%;
        height: 280px;
        border-radius: 8px;
        overflow: hidden;
        background: #1e1e1e;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .product-image {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.3s ease;
    }

    .product-image:hover {
        transform: scale(1.05);
    }

    .product-info {
        flex: 1;
        display: flex;
        gap: 1.2rem;
    }

    .product-details {
        flex: 2;
        min-width: 0;
    }

    .product-rank {
        display: inline-block;
        background: #4db8ff;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 0.3rem;
    }

    .product-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #fafafa;
        margin: 0.2rem 0 0.4rem 0;
        line-height: 1.3;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }

    .product-brand {
        color: #b3b3b3;
        font-size: 0.9rem;
        margin-bottom: 0.4rem;
    }

    .rating-container {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        margin: 0.4rem 0;
        flex-wrap: wrap;
    }

    .rating-badge {
        display: flex;
        align-items: center;
        gap: 0.2rem;
        background: rgba(255, 193, 7, 0.2);
        color: #ffc107;
        padding: 0.2rem 0.5rem;
        border-radius: 5px;
        font-size: 0.85rem;
        font-weight: 500;
    }

    .reviews-badge {
        background: rgba(23, 162, 184, 0.2);
        color: #17a2b8;
        padding: 0.2rem 0.5rem;
        border-radius: 5px;
        font-size: 0.85rem;
    }

    .price-container {
        margin: 0.6rem 0;
    }

    .current-price {
        font-size: 1.2rem;
        font-weight: 700;
        color: #28a745;
        margin-right: 0.5rem;
    }

    .original-price {
        font-size: 0.9rem;
        color: #999;
        text-decoration: line-through;
    }

    .score-badge {
        background: rgba(40, 167, 69, 0.2);
        color: #28a745;
        padding: 0.3rem 0.6rem;
        border-radius: 6px;
        font-weight: 600;
        display: inline-block;
        margin: 0.3rem 0;
        font-size: 0.85rem;
    }

    .rank-info {
        font-size: 0.8rem;
        color: #b3b3b3;
        margin: 0.2rem 0;
        background: rgba(77, 184, 255, 0.1);
        border-left: 3px solid #4db8ff;
        padding: 0.3rem 0.6rem;
        border-radius: 0 4px 4px 0;
    }

    .product-attributes {
        flex: 1;
        background: #1e1e1e;
        padding: 0.8rem;
        border-radius: 6px;
        border: 1px solid #3a3a3a;
        min-width: 200px;
    }

    .attributes-title {
        font-weight: 600;
        color: #fafafa;
        margin-bottom: 0.4rem;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .attributes-list {
        font-size: 0.8rem;
        color: #b3b3b3;
        line-height: 1.3;
        word-break: break-word;
    }

    .reviews-section {
        margin-top: 0.8rem;
        padding-top: 0.8rem;
        border-top: 1px solid #3a3a3a;
        display: block;
    }

    .reviews-title {
        font-weight: 600;
        color: #fafafa;
        margin-bottom: 0.4rem;
        font-size: 0.85rem;
    }

    .review-item {
        font-size: 0.85rem;  /* Increased font size */
        color: #b3b3b3;
        margin-bottom: 0.4rem;
        line-height: 1.4;
        padding: 0.5rem;
        background: rgba(30, 30, 30, 0.5);
        border-radius: 6px;
    }

    .no-results {
        text-align: center;
        padding: 2rem;
        background: #262730;
        border-radius: 12px;
        border: 1px solid #4a4a4a;
        color: #b3b3b3;
    }

    .no-results h3 {
        color: #fafafa;
        margin-bottom: 1rem;
    }

    .section-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.8rem;
        border-bottom: 2px solid #4a4a4a;
    }

    .section-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #fafafa;
        margin: 0;
    }

    .results-count {
        background: #4db8ff;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.85rem;
        font-weight: 500;
    }

    /* Hide empty review sections */
    .reviews-section:empty {
        display: none !important;
    }

    /* Fix for empty reviews */
    .reviews-section:empty + * {
        display: none;
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .product-content {
            flex-direction: column;
        }

        .product-info {
            flex-direction: column;
        }

        .product-image-section {
            width: 100%;
            align-self: center;
        }
    }

     .btn {
        background: linear-gradient(135deg, #4db8ff, #3399e6);
        color: white !important;
        padding: 0.7rem 1.2rem;
        border: none;
        border-radius: 8px;
        text-decoration: none !important;
        font-weight: 600;
        font-size: 0.85rem;
        transition: all 0.2s ease;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 0.3rem;
        cursor: pointer;
        text-align: center;
        box-shadow: 0 2px 8px rgba(77, 184, 255, 0.3);
    }

    .btn:hover {
        background: linear-gradient(135deg, #3399e6, #1a7bc8) !important;
        color: white !important;
        text-decoration: none !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(77, 184, 255, 0.4);
    }

    .btn-container {
        display: flex;
        gap: 0.5rem;
        padding: 1rem;
        background: #262730;
        border-top: none;
        margin: 0;
        border-radius: 0 0 12px 12px;
    }

    .btn-full {
        flex: 1;
    }

    /* Make product card and buttons appear as one unit */
    .product-card {
        background: #262730;
        border-radius: 12px 12px 0 0;
        margin: 1rem 0 0 0;
        border: 1px solid #4a4a4a;
        border-bottom: none;
        transition: all 0.3s ease;
        overflow: hidden;
    }

    .product-card:hover, .product-card:hover + .btn-container {
        border-color: #4db8ff;
        box-shadow: 0 4px 20px rgba(77, 184, 255, 0.2);
    }

    .btn-container {
        border: 1px solid #4a4a4a;
        border-top: none;
        border-radius: 0 0 12px 12px;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }

    /* Trend Analysis Page */
    .trend-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1.5rem;
        margin-top: 1.5rem;
    }

    .trend-card {
        background: #262730;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #4a4a4a;
    }

    .trend-card h3 {
        color: #4db8ff;
        margin-top: 0;
        border-bottom: 1px solid #4a4a4a;
        padding-bottom: 0.8rem;
    }

    /* Product Detail Page */
    .detail-container {
        background: #0e1117;
        color: white;
        padding: 1rem;
    }

    .detail-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #fafafa;
        margin-bottom: 1.5rem;
        line-height: 1.3;
    }

    .detail-row {
        display: flex;
        gap: 2rem;
        margin-bottom: 1.5rem;
    }

    .detail-image {
        flex: 1;
        background: #1e1e1e;
        border-radius: 8px;
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 350px;
        max-height: 400px;
    }

    .detail-image img {
        width: 100%;
        height: 100%;
        object-fit: contain;
    }

    .detail-info {
        flex: 1.5;
    }

    .detail-section {
        margin-bottom: 1.5rem;
    }

    .detail-section-title {
        color: #4db8ff;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #4a4a4a;
    }

    .info-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1.2rem;
        margin-bottom: 1.5rem;
    }

    .info-item {
        display: flex;
        flex-direction: column;
        gap: 0.3rem;
        padding: 0.8rem;
        background: #1e1e1e;
        border-radius: 8px;
        border: 1px solid #3a3a3a;
    }

    .info-label {
        font-weight: 500;
        color: #b3b3b3;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .info-value {
        color: #fafafa;
        font-size: 1.1rem;
        font-weight: 600;
    }

    /* Simple attributes - just like in product listing */
    .simple-attributes {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 0.5rem;
    }

    .attribute-badge {
        background: rgba(77, 184, 255, 0.2);
        color: #4db8ff;
        padding: 0.4rem 0.8rem;
        border-radius: 15px;
        font-size: 0.9rem;
        font-weight: 500;
    }

    /* Simple rankings */
    .rankings-simple {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        margin-top: 1rem;
    }

    .ranking-simple {
        background: #1e1e1e;
        padding: 0.7rem 1.2rem;
        border-radius: 8px;
        border: 1px solid #3a3a3a;
        font-size: 0.95rem;
        min-width: 150px;
    }

    .ranking-simple .rank-number {
        color: #4db8ff;
        font-weight: 700;
        font-size: 1.2rem;
    }

    .ranking-simple .rank-category {
        color: #b3b3b3;
        margin-left: 0.5rem;
    }

    /* Simple reviews */
    .reviews-simple {
        background: #1e1e1e;
        padding: 1rem;
        border-radius: 6px;
        border: 1px solid #3a3a3a;
        max-height: 400px;
        overflow-y: auto;
    }

    .review-simple {
        font-size: 0.95rem;
        color: #e0e0e0;
        line-height: 1.5;
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #3a3a3a;
    }

    .review-simple:last-child {
        border-bottom: none;
        margin-bottom: 0;
        padding-bottom: 0;
    }

    .back-btn-container {
        margin-top: 1rem;
        margin-bottom: 1.5rem;
    }

    .back-btn {
        background: linear-gradient(135deg, #4db8ff, #3399e6) !important;
        color: white !important;
        padding: 0.7rem 1.5rem !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
        text-decoration: none !important;
        display: inline-block !important;
        box-shadow: 0 2px 8px rgba(77, 184, 255, 0.3);
    }

    .back-btn:hover {
        background: linear-gradient(135deg, #3399e6, #1a7bc8) !important;
        color: white !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(77, 184, 255, 0.4);
        text-decoration: none !important;
    }

    /* Streamlit button override */
    .stButton > button {
        background: linear-gradient(135deg, #4db8ff, #3399e6) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.7rem 1.5rem !important;
        font-size: 0.95rem !important;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #3399e6, #1a7bc8) !important;
        color: white !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(77, 184, 255, 0.4);
    }

    /* Attribute combination chart */
    .node {
        fill: #4db8ff;
        stroke: #1e1e1e;
        stroke-width: 2px;
    }

    .node-label {
        fill: white;
        font-family: 'Inter', sans-serif;
        font-size: 10px;
        text-anchor: middle;
        pointer-events: none;
    }

    .link {
        stroke: rgba(255, 255, 255, 0.3);
        stroke-opacity: 0.6;
    }

    /* Gap analysis card */
    .gap-card {
        background: #262730;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #4a4a4a;
        margin-bottom: 1.5rem;
    }

    .gap-card h4 {
        color: #4db8ff;
        margin-top: 0;
        margin-bottom: 1rem;
    }

    .gap-item {
        padding: 0.8rem;
        background: #1e1e1e;
        border-radius: 8px;
        margin-bottom: 0.8rem;
        border-left: 3px solid #4db8ff;
    }

    /* New styles for attributes and rankings section */
    .attributes-rankings-container {
        display: flex;
        gap: 2rem;
        margin-bottom: 1.5rem;
    }

    .attributes-container {
        flex: 1;
        background: #1e1e1e;
        padding: 1.2rem;
        border-radius: 8px;
        border: 1px solid #3a3a3a;
    }

    .rankings-container {
        flex: 1;
        background: #1e1e1e;
        padding: 1.2rem;
        border-radius: 8px;
        border: 1px solid #3a3a3a;
    }

    .section-header {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
    }

    .section-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #4db8ff;
        margin: 0;
        width: 100%;
    }

    /* Responsive */
    @media (max-width: 768px) {
        .detail-row {
            flex-direction: column;
            gap: 1rem;
        }

        .info-grid {
            grid-template-columns: repeat(2, 1fr);
        }

        .rankings-simple {
            flex-direction: column;
        }

        .attributes-rankings-container {
            flex-direction: column;
            gap: 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)


# Load CSS
load_css()

# LOAD JSON DATA
try:
    with open('multi_category_trend_analysis_20250712_11.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
except FileNotFoundError:
    st.error(
        "Data file not found. Please ensure 'enhanced_trend_analysis_multi_category.json' is in the correct directory.")
    st.stop()

# Extract available categories from the new format
if "results" in data:
    available_categories = list(data["results"].keys())
    processing_summary = data.get("processing_summary", {})
else:
    st.error("Invalid data format. Please check the JSON file structure.")
    st.stop()


# Helper function to get category data
def get_category_data(category_name):
    """Extract category-specific data from the new format"""
    if category_name in data["results"]:
        category_data = data["results"][category_name]
        return {
            "category_rankings": category_data.get("category_rankings", {}),
            "overall_ranking": pd.DataFrame(category_data.get("overall_ranking", [])),
            "metadata": category_data.get("metadata", {})
        }
    return None


# Combine all products for search (updated for multi-category)
def get_all_products_for_category(category_name):
    """Get all products for a specific category"""
    category_info = get_category_data(category_name)
    if not category_info:
        return []

    all_products = []
    for group in category_info["category_rankings"].values():
        all_products.extend(group)
    all_products.extend(category_info["overall_ranking"].to_dict(orient="records"))
    return all_products


# ENHANCED PROFESSIONAL PRODUCT DETAIL PAGE - UPDATED FOR MULTI-CATEGORY
def show_product_detail(product_id, category_name):
    # Find the product by ID in the specific category
    all_products = get_all_products_for_category(category_name)
    product = None
    for p in all_products:
        if p['product_id'] == product_id:
            product = p
            break

    if not product:
        st.error("Product not found")
        return

    # Minimal, clean CSS (keeping the existing styling)
    st.markdown("""
    <style>
    .back-button {
        background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
        color: white;
        padding: 0.7rem 1.5rem;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.9rem;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        transition: all 0.2s ease;
        margin-bottom: 1.5rem;
        margin-top: 2.5rem;
    }

    .back-button:hover {
        background: linear-gradient(135deg, #4b5563 0%, #374151 100%);
        transform: translateY(-1px);
        text-decoration: none;
        color: white;
    }

    .detail-header-section {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 2rem;
        border: 1px solid #2d3748;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }

    .detail-breadcrumb {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 1.5rem;
        font-size: 0.9rem;
        color: #94a3b8;
    }

    .breadcrumb-link {
        color: #4db8ff;
        text-decoration: none;
        transition: color 0.2s ease;
    }

    .breadcrumb-link:hover {
        color: #60c7ff;
    }

    .detail-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0 0 1rem 0;
        line-height: 1.3;
    }

    .detail-subtitle {
        font-size: 1.1rem;
        color: #94a3b8;
        margin: 0;
        font-weight: 400;
    }
    </style>
    """, unsafe_allow_html=True)

    # Calculate discount
    discount = 0
    if product.get('original_price', 0) > 0:
        discount = round((product['original_price'] - product['current_price']) / product['original_price'] * 100, 1)

    # Back button with category parameter
    st.markdown(f"""
    <a href="?category={category_name}" class="back-button">
        ← Back to {category_name.replace('-', ' ').title()} Products
    </a>
    """, unsafe_allow_html=True)

    # Header Section
    st.markdown(f"""
    <div class="detail-header-section">
        <div class="detail-breadcrumb">
            <a href="?" class="breadcrumb-link">Products</a>
            <span>›</span>
            <span>{category_name.replace('-', ' ').title()}</span>
            <span>›</span>
            <span>{product['brand']}</span>
            <span>›</span>
            <span>Product Details</span>
        </div>
        <h1 class="detail-title">{product['title']}</h1>
        <p class="detail-subtitle">by <strong>{product['brand']}</strong> • Available on {product['platform']}</p>
    </div>
    """, unsafe_allow_html=True)

    # Main layout - cleaner approach
    left_col, right_col = st.columns([1, 1.5])

    # LEFT COLUMN - Image and Buy Button
    with left_col:
        st.image(product['img_link'], use_column_width=True)

        st.markdown("---")

        # Primary buy button
        st.link_button(
            f"🛒 Buy on {product['platform']}",
            product['product_link'],
            use_container_width=True,
            type="primary"
        )

        # Stock status
        st.success("✅ In Stock")

    # RIGHT COLUMN - Product Info
    with right_col:
        # Price section
        st.markdown("### 💰 Price")

        if discount > 0:
            price_col1, price_col2 = st.columns(2)
            with price_col1:
                st.metric("Current Price", f"₹{product['current_price']:,}")
            with price_col2:
                st.metric("You Save", f"₹{product['original_price'] - product['current_price']:,}",
                          f"{discount}% OFF")
        else:
            st.metric("Price", f"₹{product['current_price']:,}")

        st.markdown("---")

        # Ratings
        st.markdown("### ⭐ Ratings")

        rating_col1, rating_col2, rating_col3 = st.columns(3)

        with rating_col1:
            st.metric("Rating", f"{product['rating_outof5']}/5")

        with rating_col2:
            st.metric("Ratings", number_Str(product['ratings_count']))

        with rating_col3:
            st.metric("Reviews", number_Str(product['reviews_count']))

        st.markdown("---")

        # Product details
        st.markdown("### 📋 Details")

        st.write(f"**Brand:** {product['brand']}")
        st.write(f"**Platform:** {product['platform']}")
        st.write(f"**Product ID:** {product['product_id']}")
        st.write(f"**Category:** {category_name.replace('-', ' ').title()}")

        if 'main_category' in product:
            st.write(f"**Main Category:** {product['main_category']}")

    # Full width sections below
    st.markdown("---")

    # Product Attributes
    if 'attribute_tokenset' in product and product['attribute_tokenset']:
        attributes = product['attribute_tokenset']
        if isinstance(attributes, list) and len(attributes) > 0:
            valid_attributes = [attr for attr in attributes if attr and str(attr).strip()]

            if valid_attributes:
                st.markdown("### 🏷️ Product Features")

                # Display attributes in a clean way
                for i in range(0, len(valid_attributes), 4):
                    attr_cols = st.columns(4)
                    for j, attr in enumerate(valid_attributes[i:i + 4]):
                        with attr_cols[j]:
                            st.info(attr)

    # Category Rankings
    if 'other_category_ranks' in product and product['other_category_ranks']:
        other_ranks = product['other_category_ranks']
        if isinstance(other_ranks, dict) and len(other_ranks) > 0:
            valid_ranks = {}
            for cat, rank in other_ranks.items():
                if cat and rank and str(rank).strip():
                    try:
                        rank_num = int(float(rank))
                        valid_ranks[cat] = rank_num
                    except (ValueError, TypeError):
                        continue

            if valid_ranks:
                st.markdown("### 📈 Category Rankings")

                rank_cols = st.columns(min(len(valid_ranks), 3))
                for i, (cat, rank) in enumerate(valid_ranks.items()):
                    with rank_cols[i % 3]:
                        st.metric(cat, f"#{rank}")

    # Reviews Section
    reviews = []
    for i in range(1, 10):
        review_key = f'reviews_detail.{i}'
        if review_key in product:
            review = product[review_key]
            if review and str(review) != 'nan' and str(review).strip():
                reviews.append(review)

    if reviews:
        st.markdown("### 💬 Customer Reviews")

        # Show first 3 reviews in expandable format
        for i, review in enumerate(reviews[:3]):
            with st.expander(f"Review {i + 1}"):
                st.write(review)

        if len(reviews) > 3:
            st.info(f"+ {len(reviews) - 3} more reviews available")

    # Final purchase section
    st.markdown("---")

    final_col1, final_col2 = st.columns([2, 1])

    with final_col1:
        st.link_button(
            f"🛒 Buy Now on {product['platform']}",
            product['product_link'],
            use_container_width=True,
            type="primary"
        )

    with final_col2:
        st.link_button(
            "🖼️ View Image",
            product['img_link'],
            use_container_width=True
        )


# Check if we should show product detail page
if 'product_id' in st.query_params and 'category' in st.query_params:
    show_product_detail(st.query_params['product_id'], st.query_params['category'])
    st.stop()

# MAIN APP CONTENT

# PAGE SELECTION
page = st.sidebar.pills("", ["Products", "Trend Analysis"], label_visibility='hidden', default='Products')

# SIDEBAR CONFIGURATION
with st.sidebar:
    if page == "Products":
        st.sidebar.write('---')
        st.markdown("### Category Selection")
        selected_category = st.selectbox(
            "Choose a Category:",
            available_categories,
            index=0,
            format_func=lambda x: x.replace('-', ' ').title()
        )

        # Get category-specific data
        category_info = get_category_data(selected_category)
        if not category_info:
            st.error(f"No data found for category: {selected_category}")
            st.stop()

        sorting_options =  ["Overall Ranking"] + list(category_info["category_rankings"].keys())
        sorting_group = st.selectbox(
            "Sort By:",
            sorting_options,
            index=len(sorting_options) - 1  # Default to Overall Ranking
        )

        st.sidebar.write('---')

        # Get all unique attributes for the selected category
        all_products_in_category = get_all_products_for_category(selected_category)
        unique_attributes = set()
        for product in all_products_in_category:
            unique_attributes.update(set([attr.lower() for attr in product.get("attribute_tokenset", [])]))

        st.markdown("### Filter by Attributes")

        # Attribute Selection Mode
        attribute_mode = st.selectbox(
            "Attribute Mode:",
            ("All Available Attributes", "Enter Custom Attributes"),
            index=1,
        )

        # Attribute Selection Logic
        if attribute_mode == "All Available Attributes":
            selected_attributes = st.multiselect(
                "Select Attributes:",
                sorted(list(unique_attributes)),
                help="Select one or more attributes to filter products"
            )
        else:
            custom_attributes_input = st.text_input(
                "Enter Attributes (space-separated):",
                placeholder="e.g., cotton round oversized",
                help="Enter attributes separated by spaces"
            )
            selected_attributes = [attr.lower() for attr in
                                   custom_attributes_input.split()] if custom_attributes_input else []

        st.sidebar.write('---')

        # Add this after the attribute selection section in the sidebar
        st.markdown("### Display Settings")
        product_limit_percentage = st.slider(
            "Products to Show:",
            min_value=10,
            max_value=100,
            value=10,
            step=10,
            format="%d%%",
            help="Adjust the percentage of products to display for better performance"
        )

        if custom_attributes_input:
            product_limit_percentage = 100


# Function to Filter Products by Attributes (case-insensitive)
def filter_products_by_attributes(products, attributes):
    if not attributes:
        return pd.DataFrame(products)
    filtered_products = []
    for product in products:
        # Convert both to lowercase for case-insensitive comparison
        product_attrs = [attr.lower() for attr in product.get("attribute_tokenset", [])]
        if all(attr.lower() in product_attrs for attr in attributes):
            filtered_products.append(product)
    return pd.DataFrame(filtered_products)


# Helper function to safely convert to numeric values
def safe_numeric(value, default=0):
    """Safely convert a value to numeric, handling strings, None, and invalid values"""
    if value is None or value == '' or str(value).lower() in ['nan', 'none', 'null']:
        return default
    try:
        # Handle string numbers (including those with commas)
        if isinstance(value, str):
            # Remove commas and convert
            cleaned = value.replace(',', '').strip()
            return float(cleaned)
        return float(value)
    except (ValueError, TypeError, AttributeError):
        return default
# ENHANCED TREND ANALYSIS PAGE - MULTI-CATEGORY VERSION
if page == "Trend Analysis":
    st.markdown("## 📊 Multi-Category Market Intelligence Dashboard")
    st.markdown("Get actionable insights across all product categories to drive your strategy")

    # Category selection for trend analysis
    st.markdown("### 🎯 Select Category for Analysis")
    trend_category = st.selectbox(
        "Choose Category:",
        available_categories,
        index=0,
        format_func=lambda x: x.replace('-', ' ').title(),
        key="trend_category"
    )

    # Get data for selected category
    category_info = get_category_data(trend_category)
    if not category_info:
        st.error(f"No data found for category: {trend_category}")
        st.stop()

    category_rankings = category_info["category_rankings"]
    overall_ranking = category_info["overall_ranking"]

    # Show processing summary
    if processing_summary:
        st.markdown("### 📋 Processing Summary")
        summary_col1, summary_col2, summary_col3 = st.columns(3)

        with summary_col1:
            st.metric("Total Categories", processing_summary.get("total_categories_processed", 0))
        with summary_col2:
            st.metric("Total Products", processing_summary.get("total_products_across_categories", 0))
        with summary_col3:
            st.metric("Current Category", f"{trend_category.replace('-', ' ').title()}")

    # Quick Stats Overview for selected category
    st.markdown(f"### 📈 {trend_category.replace('-', ' ').title()} Market Overview")
    st.markdown("Get actionable insights to drive your product strategy and design decisions")

    # Calculate key metrics with safe numeric conversion
    total_products = sum(len(group) for group in category_rankings.values())

    # Safe price calculation
    valid_prices = []
    for group in category_rankings.values():
        for p in group:
            price = safe_numeric(p.get('current_price'))
            if price > 0:
                valid_prices.append(price)
    avg_price = np.mean(valid_prices) if valid_prices else 0

    # Safe rating calculation
    valid_ratings = []
    for group in category_rankings.values():
        for p in group:
            rating = safe_numeric(p.get('rating_outof5'))
            if rating > 0:
                valid_ratings.append(rating)
    avg_rating = np.mean(valid_ratings) if valid_ratings else 0

    # Safe discount calculation
    valid_discounts = []
    for group in category_rankings.values():
        for p in group:
            original = safe_numeric(p.get('original_price'))
            current = safe_numeric(p.get('current_price'))
            if original > current > 0:
                discount = (original - current) / original * 100
                valid_discounts.append(discount)
    avg_discount = np.mean(valid_discounts) if valid_discounts else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Products Analyzed", f"{total_products:,}")
    with col2:
        st.metric("Average Price", f"₹{avg_price:.0f}")
    with col3:
        st.metric("Average Rating", f"{avg_rating:.1f}★")
    with col4:
        st.metric("Average Discount", f"{avg_discount:.1f}%")

    # Attribute Analysis
    st.markdown("### 🔍 Top Trending Attributes")
    st.markdown("Discover the most popular product features in the current market")

    attribute_counter = Counter()
    for group in category_rankings.values():
        for product in group:
            attributes = [attr.lower() for attr in product.get("attribute_tokenset", [])]
            attribute_counter.update(attributes)

    # Sort by frequency and keep the top 20
    sorted_attributes = attribute_counter.most_common(20)
    attribute_df = pd.DataFrame(sorted_attributes, columns=["Attribute", "Count"])

    # Create an enhanced Plotly chart with better styling
    if not attribute_df.empty:
        fig = px.bar(
            attribute_df,
            x="Count",
            y="Attribute",
            orientation='h',
            color="Count",
            color_continuous_scale="viridis",
            title="Attribute Popularity Distribution",
            text="Count"
        )

        fig.update_layout(
            height=600,
            showlegend=False,
            font=dict(family="Inter, sans-serif", color="white"),
            title_font_size=18,
            xaxis_title="Frequency",
            yaxis_title="Attributes",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
        )

        fig.update_traces(texttemplate='%{text}', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    # 1. PRICE OPPORTUNITY ANALYSIS - Fixed with safe numeric conversion
    st.markdown("### 💰 Price Opportunity Matrix")
    st.markdown("**Actionable Insight**: Find the optimal price points for maximum profitability")

    # Create price bands analysis with safe conversion
    price_data = []
    for group in category_rankings.values():
        for product in group:
            price = safe_numeric(product.get('current_price'))
            score = safe_numeric(product.get('composite_score_norm'))
            rating = safe_numeric(product.get('rating_outof5'))
            reviews = safe_numeric(product.get('reviews_count'))

            if price > 0 and score > 0:
                price_data.append({
                    'price': price,
                    'score': score,
                    'rating': rating,
                    'reviews': reviews,
                    'title': str(product.get('title', ''))[:50]
                })

    if price_data:
        price_df = pd.DataFrame(price_data)

        # Define strategic price bands
        price_df['price_band'] = pd.cut(price_df['price'],
                                        bins=[0, 500, 1000, 1500, 2500, float('inf')],
                                        labels=['Budget (₹0-500)', 'Mid (₹500-1K)', 'Premium (₹1-1.5K)',
                                                'Luxury (₹1.5-2.5K)', 'Ultra-Premium (₹2.5K+)'])

        # Calculate performance metrics by price band
        price_analysis = price_df.groupby('price_band').agg({
            'score': ['mean', 'count'],
            'rating': 'mean',
            'reviews': 'mean',
            'price': 'mean'
        }).round(2)

        price_analysis.columns = ['Avg_Score', 'Product_Count', 'Avg_Rating', 'Avg_Reviews', 'Avg_Price']
        price_analysis['Market_Share'] = (price_analysis['Product_Count'] / len(price_df) * 100).round(1)
        price_analysis['Opportunity_Index'] = (price_analysis['Avg_Score'] * price_analysis['Avg_Rating'] /
                                               price_analysis['Product_Count'] * 10).round(2)

        # Visualize price opportunity
        fig_price = px.scatter(price_analysis.reset_index(),
                               x='Product_Count', y='Avg_Score',
                               size='Opportunity_Index', color='Avg_Rating',
                               hover_name='price_band',
                               title="Price Band Opportunity Analysis",
                               labels={'Product_Count': 'Competition Level',
                                       'Avg_Score': 'Performance Score'})

        fig_price.update_layout(
            height=400,
            font=dict(family="Inter, sans-serif", color="white"),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_price, use_container_width=True)

        # Show actionable insights
        best_opportunity = price_analysis.loc[price_analysis['Opportunity_Index'].idxmax()]
        st.success(
            f"🎯 **Best Opportunity**: {best_opportunity.name} - High performance ({best_opportunity['Avg_Score']:.1f}) with lower competition ({best_opportunity['Product_Count']} products)")

        # Show detailed table
        st.markdown("#### Price Band Performance Analysis")
        display_price = price_analysis[
            ['Product_Count', 'Market_Share', 'Avg_Price', 'Avg_Score', 'Avg_Rating', 'Opportunity_Index']]
        st.dataframe(display_price, use_container_width=True)

    # 2. ATTRIBUTE TREND ANALYSIS - Fixed with safe numeric conversion
    st.markdown("### 🏷️ Trending Attributes & Market Gaps")
    st.markdown("**Actionable Insight**: Discover which features to include in your next product line")

    # Get all attributes with performance metrics - with safe conversion
    attribute_performance = {}
    for group in category_rankings.values():
        for product in group:
            attributes = product.get("attribute_tokenset", [])
            score = safe_numeric(product.get('composite_score_norm'))
            rating = safe_numeric(product.get('rating_outof5'))
            reviews = safe_numeric(product.get('reviews_count'))

            for attr in attributes:
                attr_lower = str(attr).lower()
                if attr_lower not in attribute_performance:
                    attribute_performance[attr_lower] = {
                        'count': 0, 'total_score': 0, 'total_rating': 0,
                        'total_reviews': 0, 'products': []
                    }

                attribute_performance[attr_lower]['count'] += 1
                attribute_performance[attr_lower]['total_score'] += score
                attribute_performance[attr_lower]['total_rating'] += rating
                attribute_performance[attr_lower]['total_reviews'] += reviews
                attribute_performance[attr_lower]['products'].append(str(product.get('title', '')))

    # Create attribute insights
    attr_insights = []
    for attr, data in attribute_performance.items():
        if data['count'] >= 3:  # Only attributes with sufficient data
            avg_score = data['total_score'] / data['count']
            avg_rating = data['total_rating'] / data['count']
            avg_reviews = data['total_reviews'] / data['count']
            market_penetration = data['count'] / total_products * 100

            # Calculate opportunity score (high performance, low penetration = high opportunity)
            opportunity = (avg_score * avg_rating) / (market_penetration + 1) * 10

            attr_insights.append({
                'Attribute': attr.title(),
                'Products': data['count'],
                'Market_Share': market_penetration,
                'Avg_Score': avg_score,
                'Avg_Rating': avg_rating,
                'Avg_Reviews': avg_reviews,
                'Opportunity_Score': opportunity,
                'Category': 'High Opportunity' if opportunity > 15 and market_penetration < 30 else
                'Trending' if market_penetration > 30 else 'Niche'
            })

    if attr_insights:
        attr_df = pd.DataFrame(attr_insights)
        attr_df = attr_df.sort_values('Opportunity_Score', ascending=False)

        # Visualize attribute opportunities
        fig_attr = px.scatter(attr_df,
                              x='Market_Share', y='Avg_Score',
                              color='Category', size='Opportunity_Score',
                              hover_name='Attribute',
                              title="Attribute Market Position & Opportunity",
                              labels={'Market_Share': 'Market Penetration (%)',
                                      'Avg_Score': 'Performance Score'})

        fig_attr.update_layout(
            height=500,
            font=dict(family="Inter, sans-serif", color="white"),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_attr, use_container_width=True)

        # Show top opportunities and trending attributes
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 🚀 High Opportunity Attributes")
            high_opp = attr_df[attr_df['Category'] == 'High Opportunity'].head(5)
            if not high_opp.empty:
                for _, row in high_opp.iterrows():
                    st.markdown(f"""
                    **{row['Attribute']}**  
                    • Market Share: {row['Market_Share']:.1f}%  
                    • Performance: {row['Avg_Score']:.1f} score, {row['Avg_Rating']:.1f}★  
                    • Opportunity: {row['Opportunity_Score']:.1f}/100
                    """)
            else:
                st.info("No high-opportunity attributes found. Market may be well-saturated.")

        with col2:
            st.markdown("#### 📈 Trending Attributes")
            trending = attr_df[attr_df['Category'] == 'Trending'].head(5)
            if not trending.empty:
                for _, row in trending.iterrows():
                    st.markdown(f"""
                    **{row['Attribute']}**  
                    • Market Share: {row['Market_Share']:.1f}%  
                    • Performance: {row['Avg_Score']:.1f} score, {row['Avg_Rating']:.1f}★  
                    • Products: {row['Products']}
                    """)
            else:
                st.info("All attributes show balanced market penetration.")

    # 3. COMPETITIVE ANALYSIS - Fixed with safe numeric conversion
    st.markdown("### 🎯 Competitive Gap Analysis")
    st.markdown("**Actionable Insight**: Find underserved combinations with high potential")

    # Analyze attribute combinations with better error handling and safe conversion
    combination_analysis = {}

    for group in category_rankings.values():
        for product in group:
            attributes = [str(attr).lower() for attr in product.get("attribute_tokenset", []) if attr]
            score = safe_numeric(product.get('composite_score_norm'))
            rating = safe_numeric(product.get('rating_outof5'))
            price = safe_numeric(product.get('current_price'))

            # Only consider products with valid data
            if len(attributes) >= 2 and score > 0 and rating > 0:
                # Get all 2-attribute combinations
                for combo in combinations(sorted(set(attributes)), 2):
                    combo_key = " + ".join(combo)

                    if combo_key not in combination_analysis:
                        combination_analysis[combo_key] = {
                            'count': 0, 'scores': [], 'ratings': [], 'prices': []
                        }

                    combination_analysis[combo_key]['count'] += 1
                    combination_analysis[combo_key]['scores'].append(score)
                    combination_analysis[combo_key]['ratings'].append(rating)
                    if price > 0:
                        combination_analysis[combo_key]['prices'].append(price)

    # Process combinations for gap analysis
    gap_opportunities = []
    for combo, data in combination_analysis.items():
        if 2 <= data['count'] <= 10:  # Underserved but not absent
            avg_score = np.mean(data['scores'])
            avg_rating = np.mean(data['ratings'])
            avg_price = np.mean([p for p in data['prices'] if p > 0])

            # High potential = high performance with low competition
            if avg_score >= 4.0 and avg_rating >= 4.0:
                opportunity_score = (avg_score * avg_rating) / data['count']

                gap_opportunities.append({
                    'Combination': combo.title(),
                    'Current_Products': data['count'],
                    'Avg_Score': round(avg_score, 2),
                    'Avg_Rating': round(avg_rating, 2),
                    'Avg_Price': round(avg_price, 0) if avg_price > 0 else 0,
                    'Opportunity_Score': round(opportunity_score, 2)
                })

    # Fix the error by checking if gap_opportunities is not empty
    if gap_opportunities:
        gap_df = pd.DataFrame(gap_opportunities)
        gap_df = gap_df.sort_values('Opportunity_Score', ascending=False).head(10)

        # Visualize gaps
        if not gap_df.empty:
            fig_gap = px.scatter(gap_df,
                                 x='Current_Products', y='Opportunity_Score',
                                 size='Avg_Score', color='Avg_Rating',
                                 hover_name='Combination',
                                 title="Market Gap Opportunities",
                                 color_continuous_scale='viridis')

            fig_gap.update_layout(
                height=400,
                font=dict(family="Inter, sans-serif", color="white"),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_gap, use_container_width=True)

            # Show top 3 opportunities with detailed insights
            st.markdown("#### 🎯 Top Market Opportunities")
            for i, (_, row) in enumerate(gap_df.head(3).iterrows(), 1):
                market_size = "Small" if row['Current_Products'] <= 3 else "Medium"
                roi_potential = "High" if row['Opportunity_Score'] > 1.5 else "Medium"

                st.markdown(f"""
                <div style="background: #262730; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 4px solid #4db8ff;">
                    <h4 style="color: #4db8ff; margin: 0 0 0.5rem 0;">#{i} {row['Combination']}</h4>
                    <p style="margin: 0; color: #e0e0e0;">
                        <strong>Market Status:</strong> {market_size} market ({row['Current_Products']} products)<br>
                        <strong>Performance:</strong> {row['Avg_Score']} score, {row['Avg_Rating']}★ rating<br>
                        <strong>Price Point:</strong> ₹{row['Avg_Price']:,.0f} average<br>
                        <strong>ROI Potential:</strong> {roi_potential} ({row['Opportunity_Score']:.1f} opportunity score)
                    </p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info(
            "🔍 **Market Analysis**: All major attribute combinations are well-served. Consider focusing on premium positioning or emerging trends.")

    # 4. ACTIONABLE RECOMMENDATIONS DASHBOARD
    st.markdown("### 🚀 Strategic Recommendations")
    st.markdown("**Ready-to-implement insights for your next product launch**")

    # Generate specific recommendations based on analysis
    recommendations = []

    # Price-based recommendations
    if 'price_analysis' in locals() and not price_analysis.empty:
        best_price_band = price_analysis.loc[price_analysis['Opportunity_Index'].idxmax()]
        recommendations.append({
            'category': 'Pricing Strategy',
            'priority': 'High',
            'action': f"Launch products in {best_price_band.name} segment",
            'rationale': f"Shows {best_price_band['Opportunity_Index']:.1f} opportunity index with {best_price_band['Avg_Score']:.1f} performance score",
            'timeline': '1-2 months'
        })

    # Attribute-based recommendations
    if 'attr_df' in locals() and not attr_df.empty:
        top_attr = attr_df.iloc[0]
        if top_attr['Category'] == 'High Opportunity':
            recommendations.append({
                'category': 'Product Features',
                'priority': 'High',
                'action': f"Incorporate '{top_attr['Attribute']}' in new designs",
                'rationale': f"Only {top_attr['Market_Share']:.1f}% market penetration but {top_attr['Avg_Score']:.1f} performance",
                'timeline': '2-3 months'
            })

    # Gap-based recommendations
    if 'gap_df' in locals() and not gap_df.empty:
        top_gap = gap_df.iloc[0]
        recommendations.append({
            'category': 'Market Gap',
            'priority': 'Medium',
            'action': f"Develop {top_gap['Combination']} product line",
            'rationale': f"Underserved market with {top_gap['Opportunity_Score']:.1f} opportunity score",
            'timeline': '3-4 months'
        })

    # Display recommendations in cards
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            priority_color = '#ff6b6b' if rec['priority'] == 'High' else '#4ecdc4'
            st.markdown(f"""
            <div style="background: #262730; padding: 1.2rem; border-radius: 8px; margin: 1rem 0; border-left: 4px solid {priority_color};">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
                    <h4 style="color: #4db8ff; margin: 0;">{i}. {rec['category']}</h4>
                    <span style="background: {priority_color}; color: white; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.8rem;">{rec['priority']} Priority</span>
                </div>
                <p style="color: #e0e0e0; margin: 0.5rem 0; font-weight: 600;">{rec['action']}</p>
                <p style="color: #b3b3b3; margin: 0.5rem 0; font-size: 0.9rem;">{rec['rationale']}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Analysis complete. Market shows balanced competition across all segments.")

    # 5. MARKET MONITORING ALERTS
    st.markdown("### 🔔 Market Monitoring Setup")
    st.markdown("**Proactive insights**: Set up alerts for market changes")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **📊 Key Metrics to Track:**
        - New product launches in your target price band
        - Attribute trend changes (monthly)
        - Competitor performance shifts
        - Customer review sentiment changes
        """)

    with col2:
        st.markdown("""
        **🎯 Alert Triggers:**
        - New gap opportunities (Opportunity Score > 1.5)
        - Price band saturation changes (>15% increase)
        - Attribute performance drops (>0.5 score decrease)
        - Market share shifts (>10% change)
        """)

    # Summary footer
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem; color: #b3b3b3; border-top: 1px solid #4a4a4a;">
        <p><strong>Analysis Complete</strong> - {total_products} products analyzed in {trend_category.replace('-', ' ').title()}</p>
        <p style="font-size: 0.9rem;">Data includes {len(available_categories)} categories: {', '.join([cat.replace('-', ' ').title() for cat in available_categories])}</p>
        <p style="font-size: 0.9rem;">Last updated: {processing_summary.get('processing_date', pd.Timestamp.now().strftime('%B %d, %Y at %I:%M %p'))}</p>
    </div>
    """, unsafe_allow_html=True)

    st.stop()


# PRODUCTS PAGE CONTENT - UPDATED FOR MULTI-CATEGORY
# Update the function signature and add limit parameter
def display_products(filtered_data, section_title, category_name, limit_percentage=30):
    if filtered_data.empty:
        st.markdown("""
        <div class="no-results">
            <h3>🔍 No Products Found</h3>
            <p>Try adjusting your filters or search criteria</p>
        </div>
        """, unsafe_allow_html=True)
        return

    # Calculate number of products to show
    total_products = len(filtered_data)
    products_to_show = max(1, round(total_products * limit_percentage / 100))

    # Limit the data
    limited_data = filtered_data.head(products_to_show)

    st.markdown(f"""
    <div class="section-header">
        <h3 class="section-title">{section_title}</h3>
        <span class="results-count">Showing {len(limited_data)} of {total_products} Results</span>
    </div>
    """, unsafe_allow_html=True)

    # Rest of the function remains the same, but use limited_data instead of filtered_data
    for idx, (_, product) in enumerate(limited_data.iterrows(), 1):
        # Prepare attributes display
        attributes = product.get("attribute_tokenset", [])
        attr_display = " | ".join(attributes)

        # Prepare reviews display
        reviews_html = ""
        review_count = 0
        for i in range(1, 4):
            review = product.get(f'reviews_detail.{i}', '')
            if review and str(review) != 'nan' and str(review).strip():
                reviews_html += f'<div class="review-item">• {str(review)[:120]}{"..." if len(str(review)) > 120 else ""}</div>'
                review_count += 1

        reviews_section = ""
        if review_count > 0:
            reviews_section = f'<div class="reviews-section"><div class="reviews-title">RECENT REVIEWS</div>{reviews_html}</div>'
        else:
            reviews_section = '<div style="display: none;"></div>'

        # Category ranks
        cat_ranks = []
        for cat, rank in product.get('other_category_ranks', {}).items():
            cat_ranks.append(f"<div class='rank-info'>#{int(rank)} in {cat}</div>")
        cat_ranks_str = "".join(cat_ranks)

        # URL for product details with category
        details_url = f"?product_id={product['product_id']}&category={category_name}"

        # Product card with updated buttons
        st.markdown(f"""
        <div class="product-card">
            <div class="product-content">
                <div class="product-image-section">
                    <div class="product-image-container">
                        <img src="{product['img_link']}" class="product-image" alt="{product['title']}" />
                    </div>
                </div>
                <div class="product-info">
                    <div class="product-details">
                        <div class="product-rank">#{idx}</div>
                        <h3 class="product-title">{product['title']}</h3>
                        <div class="product-brand">
                            <strong>{product['brand']}</strong> • {product['platform']}
                        </div>
                        <div class="rating-container">
                            <div class="rating-badge">
                                ⭐ {product['rating_outof5']} ({number_Str(product['ratings_count'])})
                            </div>
                            <div class="reviews-badge">
                                {number_Str(product['reviews_count'])} Reviews
                            </div>
                        </div>
                        <div class="price-container">
                            <span class="current-price">₹{product['current_price']}</span>
                            <span class="original-price">₹{product['original_price']}</span>
                        </div>
                        <div class="score-badge">
                            Score: {round(product.get('composite_score_norm', 0), 2)}
                        </div>
                        <div class="rank-info">
                            Platform Rank: #{product['sorting_rank']} in {product.get('sorting', 'N/A')}
                        </div>
                        <div class="rank-info">
                            Category: {category_name.replace('-', ' ').title()}
                        </div>
                        {cat_ranks_str}
                    </div>
                    <div class="product-attributes">
                        <div class="attributes-title">Product Attributes ({len(attributes)})</div>
                        <div class="attributes-list">{attr_display}</div>
                        {reviews_section}
                    </div>
                </div>
            </div>
        </div>
        <div class="btn-container">
            <a href="{product['img_link']}" target="_blank" class="btn btn-full">
                🖼️ View Image
            </a>
            <a href="{product['product_link']}" target="_blank" class="btn btn-full">
                🛒 View Product
            </a>
            <a href="?product_id={product['product_id']}&category={category_name}" class="btn btn-full">
                📋 Complete Details
            </a>
        </div>
        """, unsafe_allow_html=True)


# DISPLAY PRODUCTS BASED ON SORTING - UPDATED FOR MULTI-CATEGORY
# Update both display_products calls to include the limit parameter
if page == "Products":
    category_info = get_category_data(selected_category)

    if sorting_group != "Overall Ranking":
        section_title = f"Best {selected_category.replace('-', ' ').title()} in {sorting_group}"
        group_data = category_info["category_rankings"][sorting_group]
        filtered_data = filter_products_by_attributes(group_data, selected_attributes)
        display_products(filtered_data, section_title, selected_category, product_limit_percentage)
    else:
        section_title = f"Overall Best {selected_category.replace('-', ' ').title()}"
        filtered_data = filter_products_by_attributes(
            category_info["overall_ranking"].to_dict(orient="records"),
            selected_attributes
        )
        display_products(filtered_data, section_title, selected_category, product_limit_percentage)

# FOOTER
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; padding: 1.5rem; color: #b3b3b3;">
    <p>🚀 <strong>Rawcult Multi-Category Trend Analysis</strong> - Powered by Data-Driven Insights</p>
    <p style="font-size: 0.9rem;">Analyzing {len(available_categories)} categories: {', '.join([cat.replace('-', ' ').title() for cat in available_categories])}</p>
    <p style="font-size: 0.9rem;">Total products across all categories: {processing_summary.get('total_products_across_categories', 'N/A')}</p>
</div>
""", unsafe_allow_html=True)