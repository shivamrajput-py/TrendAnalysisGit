import json
import pandas as pd
import re
import numpy as np

category = 'men-tshirts'

# You may want to install nltk & download stopwords, but here is a hardcoded English stopword list + custom “fashion stopwords”
# Feel free to extend based on your domain knowledge.
ENGLISH_STOPWORDS = {
    'a','about','above','after','again','against','all','am','an','and','any','are','aren\'t','as','at','be','because','been','before',
    'being','below','between','both','but','by','can\'t','cannot','could','couldn\'t','did','didn\'t','do','does','doesn\'t','doing',
    'don\'t','down','during','each','few','for','from','further','had','hadn\'t','has','hasn\'t','have','haven\'t','having','he','he\'d',
    'he\'ll','he\'s','her','here','here\'s','hers','herself','him','himself','his','how','how\'s','i','i\'d','i\'ll','i\'m','i\'ve',
    'if','in','into','is','isn\'t','it','it\'s','its','itself','let\'s','me','more','most','mustn\'t','my','myself','no','nor','not',
    'of','off','on','once','only','or','other','ought','our','ours','ourselves','out','over','own','same','shan\'t','she','she\'d',
    'she\'ll','she\'s','should','shouldn\'t','so','some','such','than','that','that\'s','the','their','theirs','them','themselves',
    'then','there','there\'s','these','they','they\'d','they\'ll','they\'re','they\'ve','this','those','through','to','too','under',
    'until','up','very','was','wasn\'t','we','we\'d','we\'ll','we\'re','we\'ve','were','weren\'t','what','what\'s','when','when\'s',
    'where','where\'s','which','while','who','who\'s','whom','why','why\'s','with','won\'t','would','wouldn\'t','you','you\'d','you\'ll',
    'you\'re','you\'ve','your','yours','yourself','yourselves'
}

FASHION_STOPWORDS = {
    'size','color','fabric','cotton','polyester','slimfit','regular','roundneck','v-neck','crewneck','machinewash','formal','casual',
    'men','women','tee','tshirt','shirt','top','longsleeve','shortsleeve','cottonblend','denim','jeans','joggers','sleeve','striped','plain',
    'graphic','frock','dress','trouser','pants','belt','blouse','hoodie','jacket','blazer','sweater','linen','spandex','lycra','blend'
}

# Merge them all into a single set to drop in refine_attributes
CRAP_BOX = ENGLISH_STOPWORDS.union(FASHION_STOPWORDS)

def refine_attributes(row):
    """
    Take a product row, tokenize title + brand + platform + attributes,
    drop any words in CRAP_BOX or any purely-numeric tokens, and return a list.
    """
    # 1) Tokenize title, brand, and platform (all lowercased)
    title_brand_platform = ' '.join([
        row.get("title", ""),
        row.get("brand", ""),
        row.get("platform", "")
    ]).lower()

    # Find all alphanumeric tokens (letters and numbers), drop tokens that are in CRAP_BOX or purely numeric
    # This regex grabs words with letters/digits (e.g. “100%cotton” becomes “100” and “cotton”, but we’ll drop “100” as numeric)
    tokens = re.findall(r"[A-Za-z0-9]+", title_brand_platform)
    tokens = [t for t in tokens if (t not in CRAP_BOX and not t.isnumeric())]

    # 2) Process each attribute line: remove punctuation, split on whitespace, drop CRAP_BOX/numeric
    attr_lines = row.get("attributes", [])
    for line in attr_lines:
        # Lowercase + strip punctuation (commas, periods, colons, parentheses, semicolons, quotes)
        clean_line = re.sub(r"[,\.\:\(\)\/\-\;\']+", " ", line.lower())
        for w in clean_line.split():
            if w not in CRAP_BOX and not w.isnumeric():
                tokens.append(w)

    # Return unique tokens only
    return list(set(tokens))


# -------- Main Loading + Flattening --------

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
        # Apply refinement and drop raw “attributes” key
        for i, product in enumerate(products):
            products[i]["attribute_tokenset"] = refine_attributes(product)
            products[i].pop("attributes", None)

        temp_df = pd.json_normalize(products)
        # Extract platform name (assuming “prodData_XYZ.json” → “XYZ”)
        temp_df['platform'] = file.split('_')[1].split('.')[0]
        temp_df['sorting'] = sorting
        dataframes.append(temp_df)

# Step 2: Concatenate all DataFrames
if not dataframes:
    print("❌ No dataframes were loaded. Exiting.")
    exit()

df = pd.concat(dataframes, ignore_index=True)

# Step 3: Handle Missing Data (Median Imputation)
def calculate_group_median(df, group_col, value_col, default_value):
    group_filled = df.groupby(group_col)[value_col].transform(
        lambda x: x.fillna(x.median() if not x.dropna().empty else default_value)
    )
    # Align indices just in case
    df[value_col] = group_filled.reindex(df.index)
    return df


df = calculate_group_median(df, 'sorting', 'rating_outof5', 3.5)
df = calculate_group_median(df, 'sorting', 'ratings_count', 50)
df = calculate_group_median(df, 'sorting', 'reviews_count', 10)

# Step 4: Review-Score Normalization (log-based + capping at 90th percentile)
median_reviews_by_group = df.groupby('sorting')['reviews_count'].transform(lambda x: x[x > 0].median())

def calculate_review_score(row):
    reviews = row['reviews_count']
    med = median_reviews_by_group[row.name]
    if med == 0 or pd.isna(med):
        score = 0.0
        formula = f"log({reviews}+1) / log(1)"  # degenerate if med=0
    else:
        raw = np.log(reviews + 1) / np.log(med + 1)
        score = min(raw, 2)
        formula = f"log({reviews}+1) / log({med}+1)"
    return pd.Series([score, formula])

df[['reviews_score', 'reviews_score_calculator']] = df.apply(calculate_review_score, axis=1)
cap_value = df['reviews_score'].quantile(0.9)
df['reviews_score'] = df['reviews_score'].clip(upper=cap_value)

# Step 5: Composite Score (vectorized)
# Precompute common terms
base_score = (df['rating_outof5'] * df['ratings_count']) / (df['ratings_count'] + 100)
inv_rank   = 1 / df['sorting_rank']

# Initialize empty columns
df['composite_score'] = 0.0
df['composite_score_calculator'] = ""

# Masks for sorting types
mask_rec = df['sorting'] == 'Recommended'
mask_pop = df['sorting'] == 'Popularity'
mask_fre = df['sorting'] == 'Freshness'
mask_fdb = df['sorting'] == 'Feedback'

# Fill composite_score & formulas
df.loc[mask_rec, 'composite_score'] = (
    0.45 * base_score[mask_rec]
    + 0.35 * inv_rank[mask_rec]
    + 0.20 * df['reviews_score'][mask_rec]
)
df.loc[mask_rec, 'composite_score_calculator'] = (
    "0.45 * ({:.3f} * {:.0f}) / ({:.0f} + 100) + 0.35 * (1 / {:.0f}) + 0.20 * {:.3f}"
    .format(
        df.loc[mask_rec, 'rating_outof5'].iloc[0],
        df.loc[mask_rec, 'ratings_count'].iloc[0],
        df.loc[mask_rec, 'ratings_count'].iloc[0],
        df.loc[mask_rec, 'sorting_rank'].iloc[0],
        df.loc[mask_rec, 'reviews_score'].iloc[0]
    )
)

df.loc[mask_pop, 'composite_score'] = (
    0.40 * base_score[mask_pop]
    + 0.35 * inv_rank[mask_pop]
    + 0.25 * df['reviews_score'][mask_pop]
)
df.loc[mask_pop, 'composite_score_calculator'] = (
    "0.40 * ({:.3f} * {:.0f}) / ({:.0f} + 100) + 0.35 * (1 / {:.0f}) + 0.25 * {:.3f}"
    .format(
        df.loc[mask_pop, 'rating_outof5'].iloc[0],
        df.loc[mask_pop, 'ratings_count'].iloc[0],
        df.loc[mask_pop, 'ratings_count'].iloc[0],
        df.loc[mask_pop, 'sorting_rank'].iloc[0],
        df.loc[mask_pop, 'reviews_score'].iloc[0]
    )
)

df.loc[mask_fre, 'composite_score'] = (
    0.30 * base_score[mask_fre]
    + 0.50 * inv_rank[mask_fre]
    + 0.20 * df['reviews_score'][mask_fre]
)
df.loc[mask_fre, 'composite_score_calculator'] = (
    "0.30 * ({:.3f} * {:.0f}) / ({:.0f} + 100) + 0.50 * (1 / {:.0f}) + 0.20 * {:.3f}"
    .format(
        df.loc[mask_fre, 'rating_outof5'].iloc[0],
        df.loc[mask_fre, 'ratings_count'].iloc[0],
        df.loc[mask_fre, 'ratings_count'].iloc[0],
        df.loc[mask_fre, 'sorting_rank'].iloc[0],
        df.loc[mask_fre, 'reviews_score'].iloc[0]
    )
)

df.loc[mask_fdb, 'composite_score'] = (
    0.50 * base_score[mask_fdb]
    + 0.20 * inv_rank[mask_fdb]
    + 0.30 * df['reviews_score'][mask_fdb]
)
df.loc[mask_fdb, 'composite_score_calculator'] = (
    "0.50 * ({:.3f} * {:.0f}) / ({:.0f} + 100) + 0.20 * (1 / {:.0f}) + 0.30 * {:.3f}"
    .format(
        df.loc[mask_fdb, 'rating_outof5'].iloc[0],
        df.loc[mask_fdb, 'ratings_count'].iloc[0],
        df.loc[mask_fdb, 'ratings_count'].iloc[0],
        df.loc[mask_fdb, 'sorting_rank'].iloc[0],
        df.loc[mask_fdb, 'reviews_score'].iloc[0]
    )
)

# If any rows don’t match (just in case), leave composite_score=0 and calculator as “No formula applied”.

# Step 6: New – Normalize composite_score into [0, 100]
min_score = df['composite_score'].min()
max_score = df['composite_score'].max()
if max_score == min_score:
    # Avoid division by zero if all scores are identical
    df['composite_score_norm'] = 50.0  # arbitrary mid-point
else:
    df['composite_score_norm'] = ((df['composite_score'] - min_score) / (max_score - min_score)) * 100

# Now the “worst” product is 0, the “best” is 100, and everything else is linearly between.
# If you want to round to an integer: df['composite_score_norm'] = df['composite_score_norm'].round().astype(int)

# Step 7: Rank Within Each Sorting Group (unchanged)
df['category_rank'] = df.groupby('sorting')['composite_score'].rank(method='dense', ascending=False)

# Step 8: Get other ranks (unchanged)
def get_other_rankings(df):
    ranking_info = {}
    for _, row in df.iterrows():
        pid = row['product_id']
        if pid not in ranking_info:
            ranking_info[pid] = {}
        ranking_info[pid][row['sorting']] = row['category_rank']
    df['other_category_ranks'] = df['product_id'].apply(lambda x: ranking_info.get(x, {}))
    return df

df = get_other_rankings(df)

# Step 9: Aggregate by sorting
aggregated = {}
for sorting in df['sorting'].unique():
    aggregated[sorting] = df[df['sorting'] == sorting].sort_values(by='category_rank').to_dict(orient='records')

# Step 10: Unified final ranking (unchanged)
final_ranking = pd.concat([df[df['sorting'] == s] for s in df['sorting'].unique()])
final_ranking = final_ranking.sort_values(by='composite_score', ascending=False).drop_duplicates(subset=['title'], keep='first')

output = {
    'category_rankings': aggregated,
    'overall_ranking': final_ranking.to_dict(orient='records')
}

with open(f'trend_analysis_{category}NEW.json', 'w', encoding='utf-8') as outfile:
    json.dump(output, outfile, indent=2, ensure_ascii=False)

print("✅ Trend analysis JSON file created successfully with normalized scores!")
