# Fashion Trend Analysis

A multi-platform fashion intelligence project that scrapes product data from Indian fashion marketplaces, extracts trend signals from apparel metadata, ranks products with a scoring pipeline, and serves the results through a Streamlit dashboard.

This project is built around a practical product question:

`What are the strongest fashion signals in the market right now, and how can we turn raw catalog noise into usable merchandising insight?`

It combines web automation, dataset generation, text cleaning, ranking logic, and dashboard design into one end-to-end workflow.

## What This Project Does

- Scrapes men's fashion products from multiple e-commerce platforms
- Collects titles, brands, prices, rankings, ratings, review counts, attributes, images, and product URLs
- Cleans noisy product metadata into more meaningful trend attributes
- Scores products using quality, credibility, engagement, and marketplace ranking signals
- Generates category-level and overall rankings
- Visualizes the results in a Streamlit dashboard
- Shows the latest locally generated research file automatically
- Optionally surfaces live web research/news in the dashboard through a lightweight RSS-based lookup

## Why This Project Is Useful

This repo can be used for:

- fashion trend analysis
- competitor assortment benchmarking
- pricing strategy research
- category planning
- attribute gap analysis
- early-stage market intelligence for D2C fashion brands
- portfolio demonstration of scraping + analytics + dashboard engineering

## Project Scale

Current repository configuration and generated outputs show:

- `17` supported scraping platforms in the scraper config
- `3` tracked menswear categories:
  - `men-tshirts`
  - `men-shirts`
  - `men-jeans`
- up to `50` products targeted per platform/category/sort slice in the scraper configuration
- `15` finalized `prodData_*F.json` inputs currently used by the analysis pipeline
- `3` processed categories in the latest improved research file
- `5,743` total analyzed product rows in the latest improved analysis snapshot
- `3,623` unique cleaned attributes in the latest improved analysis snapshot
- `81,870` total attribute occurrences in the latest improved analysis snapshot

Latest improved analysis snapshot in this repo:

- file: [`_ImprovedTrendAnalysis_20250730_0211.json`](_ImprovedTrendAnalysis_20250730_0211.json)
- processing date inside file: `2025-07-30T02:11:05.899726`

Category sizes in the latest improved analysis:

- `men-tshirts`: `2,238` products across `13` platforms
- `men-shirts`: `1,745` products across `12` platforms
- `men-jeans`: `1,760` products across `13` platforms

## Tech Stack

- `Python`
- `Streamlit`
- `Selenium`
- `ChromeDriver`
- `Pandas`
- `NumPy`
- `Plotly`
- `Matplotlib`
- `NetworkX`

Python dependencies are listed in [`requirements.txt`](requirements.txt).

## Supported Platforms

Configured in [`runBot_TA.py`](runBot_TA.py):

- Ajio
- Amazon
- Bewakoof
- Beyoung
- BombayShirtCompany
- Bonkers
- CampusSutra
- Flipkart
- FlipkartSpoyl
- Myntra
- Myntrafwd
- Pronk
- Slikk
- Snitch
- TheSouledStore
- Tatacliq
- TheIndianGarage

## Repository Structure

### Core application files

- [`webpage2.py`](webpage2.py)
  - Main Streamlit app
  - Loads the latest valid trend-analysis JSON automatically
  - Provides product exploration and trend-analysis views
  - Includes fallback logic so the dashboard does not depend on one hardcoded file path

- [`_Start_Analysis.py`](_Start_Analysis.py)
  - Main analytics pipeline
  - Discovers product JSON inputs
  - Cleans attributes
  - Imputes missing numeric values
  - Calculates composite scores
  - Writes `_ImprovedTrendAnalysis_<timestamp>.json`

- [`runBot_TA.py`](runBot_TA.py)
  - Shared scraper configuration
  - Marketplace URLs
  - product limits
  - helper functions such as numeric conversion and product ID generation

### Scraper bots

Each `Sbot_*.py` file is a Selenium bot tailored to one platform:

- [`Sbot_Ajio.py`](Sbot_Ajio.py)
- [`Sbot_Amazon.py`](Sbot_Amazon.py)
- [`Sbot_Bewakoof.py`](Sbot_Bewakoof.py)
- [`Sbot_Beyoung.py`](Sbot_Beyoung.py)
- [`Sbot_BombayShirtc.py`](Sbot_BombayShirtc.py)
- [`Sbot_Bonkers.py`](Sbot_Bonkers.py)
- [`Sbot_Campusutra.py`](Sbot_Campusutra.py)
- [`Sbot_Flipkart.py`](Sbot_Flipkart.py)
- [`Sbot_FlipkartSpoyl.py`](Sbot_FlipkartSpoyl.py)
- [`Sbot_Myntra.py`](Sbot_Myntra.py)
- [`Sbot_Myntrafwd.py`](Sbot_Myntrafwd.py)
- [`Sbot_Pronk.py`](Sbot_Pronk.py)
- [`Sbot_Slikk.py`](Sbot_Slikk.py)
- [`Sbot_Snitch.py`](Sbot_Snitch.py)
- [`Sbot_Souledstore.py`](Sbot_Souledstore.py)
- [`Sbot_Tatacliq.py`](Sbot_Tatacliq.py)
- [`Sbot_Theindgarage.py`](Sbot_Theindgarage.py)

### Data files

- `prodData_*.json`
  - marketplace-specific scraped product datasets

- `prodData_*F.json`
  - finalized/curated datasets currently preferred by the analysis pipeline

- `_ImprovedTrendAnalysis_*.json`
  - processed research output used by the dashboard

- `_TrendAnalysis_*.json` and `multi_category_trend_analysis_*.json`
  - earlier analysis snapshots preserved in the repo

### Environment/config

- [`.streamlit/config.toml`](.streamlit/config.toml)
  - Streamlit theme config

- [`.devcontainer/devcontainer.json`](.devcontainer/devcontainer.json)
  - VS Code/devcontainer setup

- [`chromedriver.exe`](chromedriver.exe)
  - local ChromeDriver binary for Selenium

## End-to-End Workflow

### 1. Data scraping

Each Selenium bot:

- opens category URLs
- applies available sort modes such as `Recommended`, `Popularity`, `Freshness`, and `Feedback`
- scrapes listing pages
- opens each product page
- extracts structured fields
- saves JSON output

Typical captured fields include:

- `product_id`
- `sorting_rank`
- `sorting`
- `title`
- `brand`
- `rating_outof5`
- `ratings_count`
- `current_price`
- `original_price`
- `img_link`
- `product_link`
- `reviews_count`
- `reviews_detail`
- `attributes`
- `category`
- `platform`

### 2. Trend-analysis pipeline

[`_Start_Analysis.py`](_Start_Analysis.py) performs:

- discovery of product JSON files
- category discovery across platforms
- text cleaning and tokenization
- removal of noisy/non-informative fashion terms
- curated retention of trend-relevant attributes
- numeric coercion and missing-value handling
- score calculation
- category ranking generation
- overall ranking generation
- global attribute frequency analysis

### 3. Dashboard rendering

[`webpage2.py`](webpage2.py) then:

- automatically selects the latest valid analysis file
- supports browsing products by category
- filters products by attributes
- supports free-text product search
- displays ranked products
- shows market statistics and opportunity views
- shows recent live web research when the network is available

## Ranking Logic

The improved scoring logic in [`_Start_Analysis.py`](_Start_Analysis.py) is built around a quality-first approach:

- `rating_quality`
  - normalized from product rating

- `credibility`
  - confidence score based on ratings volume using log scaling

- `engagement`
  - derived from review-rate intensity

- `popularity_bonus`
  - based on the product's relative marketplace ranking position

Composite scoring emphasizes:

- `60%` quality-related strength
- `25%` engagement
- `15%` popularity bonus

This is intended to avoid over-rewarding items that are merely visible while still accounting for marketplace traction.

## Running The Project

### 1. Create a virtual environment

```bash
python -m venv .venv
```

### 2. Activate it

Windows PowerShell:

```bash
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the dashboard

```bash
streamlit run webpage2.py
```

## Running The Analysis Pipeline

If your `prodData_*.json` files are already present:

```bash
python _Start_Analysis.py
```

This will generate a new file like:

```text
_ImprovedTrendAnalysis_YYYYMMDD_HHMM.json
```

The Streamlit app is now designed to pick the newest valid analysis file automatically.

## Running Scrapers

To run all scraper bots discovered by the controller:

```bash
python runBot_TA.py
```

Important note:

- scraper execution is platform-dependent and marketplace HTML changes can break selectors over time
- this repo already contains datasets, so the dashboard can run without scraping first
- `chromedriver.exe` and a compatible Chrome version are required for local scraping

## Limitations

- scraper selectors are fragile by nature and may need periodic maintenance
- some marketplaces expose incomplete review/rating fields
- live web research in the UI depends on network availability
- some raw JSON snapshots in the repo reflect different collection dates and coverage levels

## Future Improvements

- sentiment analysis for written reviews
- automated scheduler for refresh runs
- CSV/Parquet export pipeline
- stronger de-duplication across marketplaces
- price-band forecasting
- trend change detection across time snapshots
- vector search over attributes and reviews

## Authoring Note

This repository currently favors operational clarity over heavy abstraction: scraper files are separated by platform because each site has its own DOM structure and scraping constraints. That makes the project easier to debug and extend when selectors need to be updated.

