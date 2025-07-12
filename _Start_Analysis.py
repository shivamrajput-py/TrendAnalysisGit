import json
import pandas as pd
import re
import numpy as np
from collections import Counter
import os
from datetime import datetime

# Enhanced stopwords - removing generic/non-descriptive terms
ENGLISH_STOPWORDS = {
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'aren\'t', 'as', 'at',
    'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'can\'t', 'cannot', 'could',
    'couldn\'t', 'did', 'didn\'t', 'do', 'does', 'doesn\'t', 'doing', 'don\'t', 'down', 'during', 'each', 'few',
    'for', 'from', 'further', 'had', 'hadn\'t', 'has', 'hasn\'t', 'have', 'haven\'t', 'having', 'he', 'he\'d',
    'he\'ll', 'he\'s', 'her', 'here', 'here\'s', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'how\'s', 'i',
    'i\'d', 'i\'ll', 'i\'m', 'i\'ve', 'if', 'in', 'into', 'is', 'isn\'t', 'it', 'it\'s', 'its', 'itself', 'let\'s',
    'me', 'more', 'most', 'mustn\'t', 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or',
    'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', 'shan\'t', 'she', 'she\'d',
    'she\'ll', 'she\'s', 'should', 'shouldn\'t', 'so', 'some', 'such', 'than', 'that', 'that\'s', 'the', 'their',
    'theirs', 'them', 'themselves', 'then', 'there', 'there\'s', 'these', 'they', 'they\'d', 'they\'ll', 'they\'re',
    'they\'ve', 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', 'wasn\'t', 'we',
    'we\'d', 'we\'ll', 'we\'re', 'we\'ve', 'were', 'weren\'t', 'what', 'what\'s', 'when', 'when\'s', 'where',
    'where\'s', 'which', 'while', 'who', 'who\'s', 'whom', 'why', 'why\'s', 'with', 'won\'t', 'would', 'wouldn\'t',
    'you', 'you\'d', 'you\'ll', 'you\'re', 'you\'ve', 'your', 'yours', 'yourself', 'yourselves'
}

# Enhanced fashion stopwords based on frequency analysis
FASHION_STOPWORDS = {
    # Generic product terms
    'tshirt', 'tee', 'shirt', 'top',
    # 'clothing', 'apparel', 'garment', 'wear', 'product', 'item',
    # Generic descriptors
    'men', 'women', 'mens', 'womens', 'male', 'female', 'unisex', 'adult', 'kids', 'boy', 'girl',
    # Fabric specifications (too technical for trend analysis)
    # 'cotton', 'polyester', 'fabric', 'material', 'blend', 'spandex', 'lycra', 'viscose', 'rayon',
    # 'linen', 'modal', 'bamboo', 'organic', 'combed', 'ringspun', 'jersey', 'interlock',
    # Care instructions
    'machinewash', 'handwash', 'dryclean', 'wash', 'care', 'instructions', 'delivered',
    # Generic terms
    'size', 'sizes', 'standard', 'classic', 'basic', 'essential',
    # 'premium', 'quality',
    'brand', 'collection', 'series', 'line', 'range', 'new', 'latest', 'season',
    # Collar types (keep specific necklines but remove generic collar)
    'collar', 'neckline',
    # Brand-specific codes and SKUs (from frequency analysis)
    'black222', 'black225', 'black226', 'black230', 'black233', 'black235', 'black239', 'black240',
    'black242', 'black248', 'black258', 'black259', 'black269', 'black274', 'black277', 'black280',
    'black285', 'black287', 'black290', 'black295', 'black298', 'black299', 'black300', 'black302',
    'black_m+vgf', 'black_nm12', 'black_nm7', 'black_nm9', 'black_r+vgf', 'black_s+vgf',
    'blue_nm11', 'green_nm13', 'red_nm19', 'white_m', 'white_r', 'white_s',
    # Generic fit terms that appeared as noise
    # 'regularfit', 'fitness',
    'benefits', 'powered', 'compared', 'delivered', 'assured',
    'manufactured', 'covered', 'desired', 'incredibly', 'admired', 'inspired', 'ushered',
    'redefining', 'redefine', 'emphasize', 'scarred', 'altered', 'reduce', 'unaltered',
    # Specific brand noise
    'outfitters', 'outfits', 'outfit', 'redtape', 'boldfit', 'rangfit', 'blackworld',
    'fitinc', 'beefits', 'comfits', 'fitjeans', 'notsofit', 'zenfit', 'gymfit', 'drifit',
    # Color variations that are too specific/noisy
    # 'od_grey', 'wgrey', 'lgrey', 'darkgrey', 'plaingrey', 'mblue', 'lightblue', 'iceblue',
    # 'swanwhite', 'awblack', 'bgreen', 'greenlake', 'bluematrix', 'pinkk', 'cred',
    # 'ligthskyblue', 'lightskyblue', 'royalblue', 'greener', 'greens',
    # Pattern noise
    'bepldrj03_grey', 'bepldrj03_lightblue', 'lh_regular_jeans_02_d_blue', '737_blue30',
    'cut_sleeve_cap', 'oversizetsrt', 'checkeredpattern',
    # Generic descriptors that don't add value
    # 'coloured', 'colored', 'multicoloured', 'multicolored', 'collered', 'collarneck',
    # 'neckband', 'short_sleeve', 'halfsleeves', 'sleeves¿striking', 'sleeved'
}

# Enhanced valuable attributes - keep descriptive terms that tell us about style/design
VALUABLE_ATTRIBUTES = {
    # Fit types
    'oversized', 'slim', 'regular', 'loose', 'tight', 'baggy', 'fitted', 'relaxed',
    'skinny', 'athletic', 'muscular', 'trim', 'tailored', 'tapered', 'oversize',

    # Sleeve types
    'shortsleeve', 'longsleeve', 'sleeveless', 'halfsleeve', 'fullsleeve', 'threequarter',
    'raglan', 'drop', 'dolman', 'puff', 'sleeves',

    # Neck styles
    'roundneck', 'crewneck', 'vneck', 'polo', 'henley', 'mock', 'turtle', 'boat',
    'scoop', 'high', 'low', 'deep', 'neck', 'collared',

    # Design elements
    'striped', 'solid', 'plain', 'graphic', 'printed', 'embroidered', 'logo',
    'text', 'typography', 'vintage', 'retro', 'minimalist', 'abstract', 'geometric',
    'floral', 'cartoon', 'anime', 'band', 'music', 'sports', 'gaming', 'graffiti',

    # Colors (all major colors)
    'black', 'white', 'red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink',
    'brown', 'grey', 'gray', 'navy', 'maroon', 'burgundy', 'olive', 'khaki', 'beige',
    'cream', 'ivory', 'lime', 'teal', 'cyan', 'magenta', 'coral', 'salmon', 'gold',
    'silver', 'rose', 'mint', 'lavender', 'peach', 'turquoise', 'emerald', 'ruby',

    # Patterns
    'checked', 'plaid', 'polka', 'dots', 'camouflage', 'camo', 'tie', 'dye', 'ombre',
    'gradient', 'fade', 'distressed', 'washed', 'bleached', 'checkered', 'chequered',
    'textured', 'heathered', 'flared', 'structured', 'engineered',

    # Styles
    'casual', 'formal', 'street', 'urban', 'sporty', 'athletic', 'outdoor', 'workwear',
    'bohemian', 'preppy', 'edgy', 'punk', 'goth', 'hipster', 'trendy', 'fashion',

    # Special features
    'pocket', 'pockets', 'button', 'zip', 'zipper', 'hood', 'hooded', 'drawstring',
    'elastic', 'ribbed', 'mesh', 'breathable', 'moisture', 'quick', 'dry', 'fit',
    'sleeve', 'fits', 'fitting'
}

# Combine stopwords but exclude valuable attributes
CRAP_BOX = (ENGLISH_STOPWORDS.union(FASHION_STOPWORDS)) - VALUABLE_ATTRIBUTES

# Global counter for all attributes across all categories
GLOBAL_ATTRIBUTE_COUNTER = Counter()


def clean_and_tokenize_text(text):
    """
    Clean and tokenize text from title/brand with better preprocessing
    """
    if not text or str(text).lower() in ['nan', 'none', '']:
        return []

    # Convert to lowercase
    text = str(text).lower()

    # Remove special characters and normalize
    text = re.sub(r'[^\w\s]', ' ', text)

    # Handle common separators and compound words
    text = re.sub(r'[-_/\\]', ' ', text)

    # Split into tokens
    tokens = text.split()

    # Filter tokens
    valid_tokens = []
    for token in tokens:
        # Skip very short tokens or numeric-only tokens
        if len(token) <= 2 or token.isnumeric():
            continue

        # Skip if in crap box
        if token in CRAP_BOX:
            continue

        # Keep if it's a valuable attribute
        if token in VALUABLE_ATTRIBUTES:
            valid_tokens.append(token)
            continue

        # Keep tokens that might be color variations
        if any(color in token for color in
               ['black', 'white', 'red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink', 'brown', 'grey',
                'gray']):
            valid_tokens.append(token)
            continue

        # Keep compound style words
        if any(style in token for style in ['fit', 'neck', 'sleeve', 'size', 'wear', 'style']):
            valid_tokens.append(token)
            continue

        # Keep if it seems like a meaningful descriptor (not in stopwords)
        if len(token) > 3 and token not in ENGLISH_STOPWORDS:
            valid_tokens.append(token)

    return valid_tokens


def refine_attributes(row):
    """
    Enhanced attribute extraction including title and brand words
    """
    all_tokens = []

    # 1) Process title - most important source
    title = row.get("title", "")
    title_tokens = clean_and_tokenize_text(title)
    all_tokens.extend(title_tokens)

    # 2) Process brand - second most important
    brand = row.get("brand", "")
    brand_tokens = clean_and_tokenize_text(brand)
    all_tokens.extend(brand_tokens)

    # 3) Process attributes from the attributes field
    attr_lines = row.get("attributes", [])
    if attr_lines:
        for line in attr_lines:
            # More comprehensive cleaning
            clean_line = re.sub(r"[,\.\:\(\)\/\-\;\'\"\[\]\{\}\\]+", " ", str(line).lower())
            # Handle compound words (e.g., "round-neck" -> "roundneck")
            clean_line = re.sub(r"(\w+)-(\w+)", r"\1\2", clean_line)

            # Extract tokens
            attr_tokens = clean_line.split()
            for token in attr_tokens:
                if len(token) > 2 and token not in CRAP_BOX:
                    # Apply same filtering logic as title/brand
                    if (token in VALUABLE_ATTRIBUTES or
                            any(color in token for color in
                                ['black', 'white', 'red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink',
                                 'brown', 'grey', 'gray']) or
                            any(style in token for style in ['fit', 'neck', 'sleeve', 'size', 'wear', 'style']) or
                            (len(token) > 3 and token not in ENGLISH_STOPWORDS)):
                        all_tokens.append(token)

    # 4) Additional processing for better quality
    # Remove duplicates while preserving order
    seen = set()
    unique_tokens = []
    for token in all_tokens:
        if token not in seen:
            seen.add(token)
            unique_tokens.append(token)

    # 5) Final filtering - remove any remaining noise
    final_tokens = []
    for token in unique_tokens:
        # Skip if it's clearly a product code or SKU
        if re.match(r'^[a-z]+\d+$', token) or re.match(r'^\d+[a-z]+\d*$', token):
            continue

        # Skip if it contains underscores or plus signs (likely codes)
        if '_' in token or '+' in token:
            continue

        # Skip if it's all caps (likely brand codes)
        if token.isupper() and len(token) > 4:
            continue

        final_tokens.append(token)

    # Update global counter
    GLOBAL_ATTRIBUTE_COUNTER.update(final_tokens)

    # Return sorted unique tokens
    return sorted(list(set(final_tokens)))


def enhanced_median_imputation(df):
    """Enhanced missing data handling with better grouping logic"""

    # Ensure we have the required columns
    required_cols = ['rating_outof5', 'ratings_count', 'reviews_count']
    for col in required_cols:
        if col not in df.columns:
            df[col] = np.nan

    # Group by platform and sorting for more accurate imputation
    def smart_fill(group_cols, value_col, default_val):
        if not df[group_cols].empty:
            return df.groupby(group_cols)[value_col].transform(
                lambda x: x.fillna(x.median() if not x.dropna().empty else default_val)
            )
        else:
            return df[value_col].fillna(default_val)

    # Try platform-specific medians first, fall back to sorting-specific
    df['rating_outof5'] = smart_fill(['platform', 'sorting'], 'rating_outof5', 3.5)
    df['ratings_count'] = smart_fill(['platform', 'sorting'], 'ratings_count', 50)
    df['reviews_count'] = smart_fill(['platform', 'sorting'], 'reviews_count', 10)

    return df


def calculate_enhanced_review_score(df):
    """Improved review score calculation with better normalization"""

    # Calculate platform-specific medians for better normalization
    platform_medians = df.groupby(['platform', 'sorting'])['reviews_count'].transform(
        lambda x: x[x > 0].median()
    ).fillna(1)  # Avoid division by zero

    def enhanced_review_score(row, med):
        reviews = row['reviews_count']
        if reviews <= 0:
            return 0.0

        # Use log transformation but with better scaling
        raw_score = np.log1p(reviews) / np.log1p(med)  # log1p is more stable

        # Apply sigmoid transformation to prevent extreme values
        sigmoid_score = 2 / (1 + np.exp(-raw_score)) - 1  # Maps to [-1, 1], shift to [0, 2]

        return max(0, min(2, sigmoid_score))  # Clamp to [0, 2]

    # Apply the enhanced calculation
    df['reviews_score'] = df.apply(
        lambda row: enhanced_review_score(row, platform_medians[row.name]),
        axis=1
    )

    # Cap at 95th percentile instead of 90th for less aggressive capping
    cap_value = df['reviews_score'].quantile(0.95)
    df['reviews_score'] = df['reviews_score'].clip(upper=cap_value)

    return df


def calculate_enhanced_composite_score(df):
    """Enhanced composite score with better weighting and normalization"""

    # Normalize rating to [0, 1] scale for consistency
    df['rating_normalized'] = (df['rating_outof5'] - 1) / 4  # 1-5 scale to 0-1

    # Enhanced base score calculation
    base_score = df['rating_normalized'] * np.sqrt(df['ratings_count']) / (np.sqrt(df['ratings_count']) + 10)

    # Logarithmic rank transformation for better distribution
    df['inv_rank'] = 1 / np.log1p(df['sorting_rank'])  # More gradual decrease

    # Normalize inverse rank within each sorting group
    df['inv_rank_norm'] = df.groupby('sorting')['inv_rank'].transform(
        lambda x: (x - x.min()) / (x.max() - x.min()) if x.max() != x.min() else 0.5
    )

    # Enhanced weighting based on sorting type with more balanced approach
    weights = {
        'Recommended': {'quality': 0.4, 'popularity': 0.3, 'reviews': 0.3},
        'Popularity': {'quality': 0.3, 'popularity': 0.4, 'reviews': 0.3},
        'Freshness': {'quality': 0.25, 'popularity': 0.5, 'reviews': 0.25},
        'Feedback': {'quality': 0.5, 'popularity': 0.2, 'reviews': 0.3}
    }

    # Calculate composite score for each sorting type
    df['composite_score'] = 0.0

    for sorting_type, weight_dict in weights.items():
        mask = df['sorting'] == sorting_type
        if mask.any():
            df.loc[mask, 'composite_score'] = (
                    weight_dict['quality'] * base_score.loc[mask] +
                    weight_dict['popularity'] * df.loc[mask, 'inv_rank_norm'] +
                    weight_dict['reviews'] * df.loc[mask, 'reviews_score'] / 2  # Normalize reviews_score
            )

    return df


def get_enhanced_rankings(df):
    """Get cross-category rankings"""
    ranking_info = {}
    for _, row in df.iterrows():
        pid = row['product_id']
        if pid not in ranking_info:
            ranking_info[pid] = {}
        ranking_info[pid][row['sorting']] = int(row['category_rank'])

    df['other_category_ranks'] = df['product_id'].apply(lambda x: ranking_info.get(x, {}))
    return df


def process_single_category(category_data, category_name):
    """Process a single category and return results"""
    print(f"  📊 Processing category: {category_name}")

    dataframes = []

    for platform_name, platform_data in category_data.items():
        for sorting, products in platform_data.items():
            if not products:  # Skip empty product lists
                continue

            # Apply enhanced refinement
            for i, product in enumerate(products):
                products[i]["attribute_tokenset"] = refine_attributes(product)
                products[i].pop("attributes", None)  # Remove raw attributes

            temp_df = pd.json_normalize(products)
            temp_df['platform'] = platform_name
            temp_df['sorting'] = sorting
            dataframes.append(temp_df)

    if not dataframes:
        print(f"    ⚠️ No data found for category: {category_name}")
        return None

    # Combine all dataframes
    df = pd.concat(dataframes, ignore_index=True, sort=False)

    # Remove any completely empty rows
    df = df.dropna(how='all')

    if df.empty:
        print(f"    ⚠️ No valid data after processing for category: {category_name}")
        return None

    # Apply enhanced processing pipeline
    df = enhanced_median_imputation(df)
    df = calculate_enhanced_review_score(df)
    df = calculate_enhanced_composite_score(df)

    # Enhanced normalization to [0, 100] scale
    min_score = df['composite_score'].min()
    max_score = df['composite_score'].max()

    if max_score == min_score:
        df['composite_score_norm'] = 50.0
    else:
        # Apply power transformation for better score distribution
        normalized = (df['composite_score'] - min_score) / (max_score - min_score)
        df['composite_score_norm'] = (normalized ** 0.8) * 100

    # Round to integers for cleaner presentation
    df['composite_score_norm'] = df['composite_score_norm'].round().astype(int)

    # Calculate rankings
    df['category_rank'] = df.groupby('sorting')['composite_score'].rank(method='dense', ascending=False)
    df = get_enhanced_rankings(df)

    # Create aggregated results
    aggregated = {}
    for sorting in df['sorting'].unique():
        sorting_df = df[df['sorting'] == sorting].sort_values(by='category_rank')
        aggregated[sorting] = sorting_df.to_dict(orient='records')

    # Enhanced overall ranking with deduplication
    final_ranking = df.sort_values(by='composite_score', ascending=False).drop_duplicates(
        subset=['title', 'brand'], keep='first'
    )

    # Attribute frequency analysis
    all_attributes = []
    for attrs in df['attribute_tokenset']:
        all_attributes.extend(attrs)

    attribute_freq = Counter(all_attributes)
    top_attributes = dict(attribute_freq.most_common(50))

    # Create category result
    category_result = {
        'metadata': {
            'category': category_name,
            'total_products': len(df),
            'platforms': df['platform'].nunique(),
            'processing_date': datetime.now().isoformat(),
            'top_attributes': top_attributes,
            'score_distribution': {
                'min': float(df['composite_score_norm'].min()),
                'max': float(df['composite_score_norm'].max()),
                'mean': float(df['composite_score_norm'].mean()),
                'median': float(df['composite_score_norm'].median())
            }
        },
        'category_rankings': aggregated,
        'overall_ranking': final_ranking.to_dict(orient='records')
    }

    print(f"    ✅ Processed {len(df):,} products from {df['platform'].nunique()} platforms")

    return category_result


def discover_categories_from_files(files):
    """Discover all available categories across all files"""
    all_categories = set()

    for file in files:
        if not os.path.exists(file):
            print(f"⚠️ Warning: File {file} not found. Skipping.")
            continue

        try:
            with open(file, 'r', encoding='utf-8') as f:
                platform_data = json.load(f)
                all_categories.update(platform_data.keys())
        except Exception as e:
            print(f"⚠️ Warning: Could not open/parse {file}: {e}")
            continue

    return sorted(list(all_categories))


def load_category_data(files, category):
    """Load data for a specific category from all files"""
    category_data = {}

    for file in files:
        if not os.path.exists(file):
            continue

        try:
            with open(file, 'r', encoding='utf-8') as f:
                platform_data = json.load(f)

            if category in platform_data:
                # Extract platform name from the data itself
                platform_name = None
                for sorting_type, products in platform_data[category].items():
                    if products and len(products) > 0:
                        first_product = products[0]
                        if 'platform' in first_product:
                            platform_name = first_product['platform']
                            break

                # Fallback to extracting from filename
                if not platform_name:
                    platform_name = file.replace('prodData_', '').replace('.json', '')
                    if platform_name.endswith('F'):
                        platform_name = platform_name[:-1]

                category_data[platform_name] = platform_data[category]

        except Exception as e:
            print(f"⚠️ Warning: Could not process {file}: {e}")
            continue

    return category_data


def print_global_attributes_summary():
    """Print a summary of all unique attributes across all categories"""
    print("\n" + "=" * 80)
    print("🔍 GLOBAL ATTRIBUTE ANALYSIS - ALL CATEGORIES")
    print("=" * 80)

    if not GLOBAL_ATTRIBUTE_COUNTER:
        print("❌ No attributes found across all categories.")
        return

    total_unique_attributes = len(GLOBAL_ATTRIBUTE_COUNTER)
    total_attribute_occurrences = sum(GLOBAL_ATTRIBUTE_COUNTER.values())

    print(f"📊 Total unique attributes: {total_unique_attributes:,}")
    print(f"📊 Total attribute occurrences: {total_attribute_occurrences:,}")
    print(f"📊 Average occurrences per attribute: {total_attribute_occurrences / total_unique_attributes:.2f}")

    print("\n🏆 THE MOST FREQUENT ATTRIBUTES:")
    print("-" * 50)

    # Sort by frequency and display top 100
    sorted_attributes = GLOBAL_ATTRIBUTE_COUNTER.most_common(min(100, total_unique_attributes))

    for i, (attribute, count) in enumerate(sorted_attributes, 1):
        print(f"{i:3d}. {attribute:20} → {count:,} occurrences")

    print("\n📈 FREQUENCY DISTRIBUTION:")
    print("-" * 30)

    # Create frequency bins
    counts = list(GLOBAL_ATTRIBUTE_COUNTER.values())
    bins = [1, 2, 5, 10, 50, 100, 500, 1000, float('inf')]
    bin_labels = ['1', '2-4', '5-9', '10-49', '50-99', '100-499', '500-999', '1000+']

    for i, (bin_start, bin_end) in enumerate(zip(bins[:-1], bins[1:])):
        count_in_bin = sum(1 for c in counts if bin_start <= c < bin_end)
        percentage = (count_in_bin / total_unique_attributes) * 100
        print(f"{bin_labels[i]:>8} occurrences: {count_in_bin:,} attributes ({percentage:.1f}%)")

    print("\n💡 ATTRIBUTES TO CONSIDER FOR CRAP_BOX (appearing only once):")
    print("-" * 55)

    single_occurrence_attrs = [attr for attr, count in GLOBAL_ATTRIBUTE_COUNTER.items() if count == 1]
    if single_occurrence_attrs:
        print(f"Found {len(single_occurrence_attrs)} attributes appearing only once:")
        for i, attr in enumerate(sorted(single_occurrence_attrs), 1):
            print(f"{i:3d}. {attr}")
    else:
        print("✅ No attributes appear only once - good data quality!")


# -------- Main Processing Pipeline --------

def main():
    files = [
        'prodData_AjioF.json',
        'prodData_AmazonF.json',
        'prodData_BewakoofF.json',
        'prodData_BeyoungF.json',
        'prodData_BombaySCF.json',
        'prodData_BonkersF.json',
        'prodData_CampusutraF.json',
        'prodData_FlipkartF.json',
        'prodData_FlipkartspoylF.json',
        'prodData_MyntraF.json',
        'prodData_MyntrafwdF.json',
        'prodData_PronkF.json',
        'prodData_SlikkF.json',
        # 'prodData_Snitch.json',
        'prodData_SouledstoreF.json',
        'prodData_TatacliqF.json',
        # 'prodData_TheindgarageF.json',
    ]

    # Clear global counter at start
    global GLOBAL_ATTRIBUTE_COUNTER
    GLOBAL_ATTRIBUTE_COUNTER.clear()

    print("🔍 Discovering available categories...")

    # Discover all categories across all files
    all_categories = discover_categories_from_files(files)

    if not all_categories:
        print("❌ No categories found in any files. Exiting.")
        return

    print(f"📋 Found {len(all_categories)} categories: {', '.join(all_categories)}")

    # Process each category
    final_results = {}

    for category in all_categories:
        print(f"\n🔄 Processing category: {category}")

        # Load data for this category from all files
        category_data = load_category_data(files, category)

        if not category_data:
            print(f"  ⚠️ No data found for category: {category}")
            continue

        # Process the category
        category_result = process_single_category(category_data, category)

        if category_result:
            final_results[category] = category_result

    # Print global attribute analysis
    print_global_attributes_summary()

    if not final_results:
        print("❌ No results generated. Exiting.")
        return

    # Save results
    output_file = f'multi_category_trend_analysis_{datetime.now().strftime("%Y%m%d_%H")}.json'

    # Add overall summary
    summary = {
        'processing_summary': {
            'total_categories_processed': len(final_results),
            'categories': list(final_results.keys()),
            'processing_date': datetime.now().isoformat(),
            'total_products_across_categories': sum(
                result['metadata']['total_products'] for result in final_results.values()
            ),
            'global_attribute_stats': {
                'total_unique_attributes': len(GLOBAL_ATTRIBUTE_COUNTER),
                'total_attribute_occurrences': sum(GLOBAL_ATTRIBUTE_COUNTER.values()),
                'top_50_attributes': dict(GLOBAL_ATTRIBUTE_COUNTER.most_common(50))
            }
        },
        'results': final_results
    }

    with open(output_file, 'w', encoding='utf-8') as outfile:
        json.dump(summary, outfile, indent=2, ensure_ascii=False)

    print(f"\n✅ Multi-category trend analysis complete!")
    print(f"📁 Results saved to: {output_file}")
    print(f"🎯 Categories processed: {len(final_results)}")

    # Display summary for each category
    for category, result in final_results.items():
        metadata = result['metadata']
        print(f"  📊 {category}: {metadata['total_products']:,} products from {metadata['platforms']} platforms")


if __name__ == "__main__":
    main()