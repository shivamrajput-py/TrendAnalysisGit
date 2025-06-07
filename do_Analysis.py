import json
import pandas as pd
import re
import numpy as np
from collections import Counter

category = 'men-tshirts'

# Enhanced stopwords - removing generic/non-descriptive terms
ENGLISH_STOPWORDS = {
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'aren\'t', 'as', 'at',
    'be', 'because', 'been', 'before',
    'being', 'below', 'between', 'both', 'but', 'by', 'can\'t', 'cannot', 'could', 'couldn\'t', 'did', 'didn\'t', 'do',
    'does', 'doesn\'t', 'doing',
    'don\'t', 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had', 'hadn\'t', 'has', 'hasn\'t', 'have',
    'haven\'t', 'having', 'he', 'he\'d',
    'he\'ll', 'he\'s', 'her', 'here', 'here\'s', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'how\'s', 'i',
    'i\'d', 'i\'ll', 'i\'m', 'i\'ve',
    'if', 'in', 'into', 'is', 'isn\'t', 'it', 'it\'s', 'its', 'itself', 'let\'s', 'me', 'more', 'most', 'mustn\'t',
    'my', 'myself', 'no', 'nor', 'not',
    'of', 'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same',
    'shan\'t', 'she', 'she\'d',
    'she\'ll', 'she\'s', 'should', 'shouldn\'t', 'so', 'some', 'such', 'than', 'that', 'that\'s', 'the', 'their',
    'theirs', 'them', 'themselves',
    'then', 'there', 'there\'s', 'these', 'they', 'they\'d', 'they\'ll', 'they\'re', 'they\'ve', 'this', 'those',
    'through', 'to', 'too', 'under',
    'until', 'up', 'very', 'was', 'wasn\'t', 'we', 'we\'d', 'we\'ll', 'we\'re', 'we\'ve', 'were', 'weren\'t', 'what',
    'what\'s', 'when', 'when\'s',
    'where', 'where\'s', 'which', 'while', 'who', 'who\'s', 'whom', 'why', 'why\'s', 'with', 'won\'t', 'would',
    'wouldn\'t', 'you', 'you\'d', 'you\'ll',
    'you\'re', 'you\'ve', 'your', 'yours', 'yourself', 'yourselves'
}

# Expanded list of non-valuable fashion terms to remove
FASHION_STOPWORDS = {
    # Generic product terms
    'tshirt', 'tee', 'shirt', 'top', 'clothing', 'apparel', 'garment', 'wear', 'product',
    # Generic descriptors
    'men', 'women', 'mens', 'womens', 'male', 'female', 'unisex', 'adult',
    # Fabric specifications (too technical)
    'cotton', 'polyester', 'fabric', 'material', 'blend', 'spandex', 'lycra', 'viscose', 'rayon',
    'linen', 'modal', 'bamboo', 'organic', 'combed', 'ringspun', 'jersey', 'interlock',
    # Care instructions
    'machinewash', 'handwash', 'dryclean', 'wash', 'care', 'instructions',
    # Generic terms
    'size', 'regular', 'standard', 'classic', 'basic', 'essential', 'premium', 'quality',
    'brand', 'collection', 'series', 'line', 'range', 'new', 'latest', 'season',
    # Collar types (keep specific necklines but remove generic collar)
    'collar', 'neckline'
}

# Keep valuable descriptive attributes that tell us about the product style/design
VALUABLE_ATTRIBUTES = {
    # Fit types
    'oversized', 'slim', 'regular', 'loose', 'tight', 'baggy', 'fitted', 'relaxed',
    'skinny', 'athletic', 'muscular', 'trim', 'tailored',

    # Sleeve types
    'shortsleeve', 'longsleeve', 'sleeveless', 'halfsleeve', 'fullsleeve', 'threequarter',
    'raglan', 'drop', 'dolman', 'puff',

    # Neck styles
    'roundneck', 'crewneck', 'vneck', 'polo', 'henley', 'mock', 'turtle', 'boat',
    'scoop', 'high', 'low', 'deep',

    # Design elements
    'striped', 'solid', 'plain', 'graphic', 'printed', 'embroidered', 'logo',
    'text', 'typography', 'vintage', 'retro', 'minimalist', 'abstract', 'geometric',
    'floral', 'cartoon', 'anime', 'band', 'music', 'sports', 'gaming',

    # Colors (all major colors)
    'black', 'white', 'red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink',
    'brown', 'grey', 'gray', 'navy', 'maroon', 'burgundy', 'olive', 'khaki', 'beige',
    'cream', 'ivory', 'lime', 'teal', 'cyan', 'magenta', 'coral', 'salmon', 'gold',
    'silver', 'rose', 'mint', 'lavender', 'peach', 'turquoise', 'emerald', 'ruby',

    # Patterns
    'checked', 'plaid', 'polka', 'dots', 'camouflage', 'camo', 'tie', 'dye', 'ombre',
    'gradient', 'fade', 'distressed', 'washed', 'bleached',

    # Styles
    'casual', 'formal', 'street', 'urban', 'sporty', 'athletic', 'outdoor', 'workwear',
    'bohemian', 'preppy', 'edgy', 'punk', 'goth', 'hipster', 'trendy', 'fashion',

    # Special features
    'pocket', 'pockets', 'button', 'zip', 'zipper', 'hood', 'hooded', 'drawstring',
    'elastic', 'ribbed', 'mesh', 'breathable', 'moisture', 'quick', 'dry'
}

# Combine stopwords but exclude valuable attributes
CRAP_BOX = (ENGLISH_STOPWORDS.union(FASHION_STOPWORDS)) - VALUABLE_ATTRIBUTES


def refine_attributes(row):
    """
    Enhanced attribute extraction focusing on valuable descriptive terms
    """
    # 1) Tokenize title, brand, and platform (all lowercased)
    title_brand_platform = ' '.join([
        row.get("title", ""),
        row.get("brand", ""),
        row.get("platform", "")
    ]).lower()

    # More aggressive tokenization - split on various delimiters
    tokens = re.findall(r"[A-Za-z0-9]+", title_brand_platform)

    # 2) Process each attribute line with better cleaning
    attr_lines = row.get("attributes", [])
    for line in attr_lines:
        # More comprehensive punctuation removal and normalization
        clean_line = re.sub(r"[,\.\:\(\)\/\-\;\'\"\[\]\{\}\\]+", " ", line.lower())
        # Handle compound words (e.g., "round-neck" -> "roundneck")
        clean_line = re.sub(r"(\w+)-(\w+)", r"\1\2", clean_line)

        for w in clean_line.split():
            if len(w) > 2:  # Ignore very short tokens
                tokens.append(w)

    # 3) Filter tokens more intelligently
    valuable_tokens = []
    for token in tokens:
        # Skip if in crap box or purely numeric
        if token in CRAP_BOX or token.isnumeric():
            continue

        # Keep if it's a valuable attribute
        if token in VALUABLE_ATTRIBUTES:
            valuable_tokens.append(token)
            continue

        # Keep tokens that might be color variations or style descriptors
        if any(color in token for color in
               ['black', 'white', 'red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink', 'brown', 'grey',
                'gray']):
            valuable_tokens.append(token)
            continue

        # Keep compound style words
        if any(style in token for style in ['fit', 'neck', 'sleeve', 'size']):
            valuable_tokens.append(token)
            continue

    # Return unique tokens, sorted for consistency
    return sorted(list(set(valuable_tokens)))


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


# -------- Main Processing Pipeline --------

files = [
    'prodData_Ajio.json',
    'prodData_Amazon.json',
    'prodData_Bewakoof.json',
    'prodData_Beyoung.json',
    'prodData_BombaySC.json',
    'prodData_Campusutra.json',
    'prodData_Flipkart.json',
    'prodData_Myntra.json',
    'prodData_Pronk.json',
    'prodData_Snitch.json',
    'prodData_Souledstore.json',
    'prodData_Tatacliq.json',
    'prodData_Theindgarage.json',
]

dataframes = []

print("🔄 Loading and processing product data...")

for file in files:
    try:
        with open(file, 'r', encoding='utf-8') as f:
            platform_data = json.load(f)
    except Exception as e:
        print(f"⚠️ Warning: Could not open/parse {file}: {e}")
        continue

    if category not in platform_data:
        print(f"⚠️ Warning: '{category}' not found in {file}. Skipping.")
        continue

    for sorting, products in platform_data[category].items():
        # Apply enhanced refinement
        for i, product in enumerate(products):
            products[i]["attribute_tokenset"] = refine_attributes(product)
            products[i].pop("attributes", None)  # Remove raw attributes

        temp_df = pd.json_normalize(products)
        temp_df['platform'] = file.split('_')[1].split('.')[0]
        temp_df['sorting'] = sorting
        dataframes.append(temp_df)

if not dataframes:
    print("❌ No dataframes were loaded. Exiting.")
    exit()

print("📊 Combining data and calculating enhanced metrics...")

# Combine all dataframes with better handling of empty dataframes
df = pd.concat(dataframes, ignore_index=True, sort=False)

# Remove any completely empty rows that might cause issues
df = df.dropna(how='all')

# Apply enhanced processing pipeline
df = enhanced_median_imputation(df)
df = calculate_enhanced_review_score(df)
df = calculate_enhanced_composite_score(df)

# Enhanced normalization to [0, 100] scale with better distribution
min_score = df['composite_score'].min()
max_score = df['composite_score'].max()

if max_score == min_score:
    df['composite_score_norm'] = 50.0
else:
    # Apply power transformation for better score distribution
    normalized = (df['composite_score'] - min_score) / (max_score - min_score)
    # Slight power transformation to spread middle values
    df['composite_score_norm'] = (normalized ** 0.8) * 100

# Round to integers for cleaner presentation
df['composite_score_norm'] = df['composite_score_norm'].round().astype(int)

# Calculate rankings
print("🏆 Calculating rankings...")

df['category_rank'] = df.groupby('sorting')['composite_score'].rank(method='dense', ascending=False)


# Get cross-category rankings
def get_enhanced_rankings(df):
    ranking_info = {}
    for _, row in df.iterrows():
        pid = row['product_id']
        if pid not in ranking_info:
            ranking_info[pid] = {}
        ranking_info[pid][row['sorting']] = int(row['category_rank'])

    df['other_category_ranks'] = df['product_id'].apply(lambda x: ranking_info.get(x, {}))
    return df


df = get_enhanced_rankings(df)

# Create final aggregated results
print("📋 Generating final analysis...")

aggregated = {}
for sorting in df['sorting'].unique():
    sorting_df = df[df['sorting'] == sorting].sort_values(by='category_rank')
    aggregated[sorting] = sorting_df.to_dict(orient='records')

# Enhanced overall ranking with deduplication
final_ranking = df.sort_values(by='composite_score', ascending=False).drop_duplicates(
    subset=['title', 'brand'], keep='first'  # Better deduplication
)

# Add attribute frequency analysis
print("🔍 Analyzing attribute patterns...")

all_attributes = []
for attrs in df['attribute_tokenset']:
    all_attributes.extend(attrs)

attribute_freq = Counter(all_attributes)
top_attributes = dict(attribute_freq.most_common(50))

# Final output with enhanced metadata
output = {
    'metadata': {
        'category': category,
        'total_products': len(df),
        'platforms': df['platform'].nunique(),
        'processing_date': pd.Timestamp.now().isoformat(),
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

# Save results
output_file = f'enhanced_trend_analysis_{category}.json'
with open(output_file, 'w', encoding='utf-8') as outfile:
    json.dump(output, outfile, indent=2, ensure_ascii=False)

print(f"✅ Enhanced trend analysis complete!")
print(f"📁 Results saved to: {output_file}")
print(f"📈 Processed {len(df):,} products from {df['platform'].nunique()} platforms")
print(f"🎯 Top valuable attributes found: {list(top_attributes.keys())[:10]}")
print(f"🏆 Score range: {df['composite_score_norm'].min()}-{df['composite_score_norm'].max()}")