import os

# FINAL CONSTANTS
SCRAPE_THESE_WEBSITES = ['Amazon', 'Myntra', 'Flipkart', 'Tatacliq', 'Ajio', 'Bewakoof', 'Beyoung', 'Pronk']
SYSTEM = 0  #[ 0 - win & 1 - mac ]
NO_OF_PRODUCTS_TO_SCRAPE = 5 # [From Each Sub Category- Sorting]

# ---------------------------------------------------------------------------------------

# FUNCTIONS
def convert_to_number(s):
    multipliers = {
        'K': 1_000,
        'k': 1_000,
        'M': 1_000_000,
        'B': 1_000_000_000,
        'T': 1_000_000_000_000
    }
    if len(s) > 1 and s[-1] in multipliers:
        try:
            num_part = float(s[:-1])
            multiplier = multipliers[s[-1]]
            return str(int(num_part * multiplier))
        except ValueError:
            return s
    else:
        return s


def make_id(title: str, brand: str):
    samp_id = ''

    for word in brand.split(' '):
        if (len(word) > 0) and (len(word) < 3):
            samp_id += word
        else:
            samp_id += word[0:3]

    samp_id += '_'

    for word in title.split(' '):
        if (len(word) > 0) and (len(word) < 3):
            samp_id += word
        else:
            samp_id += word[0:3]

    return samp_id

# ---------------------------------------------------------------------------------------

if __name__ == '__main__':

    list_of_bots = []
    if SYSTEM == 0: cmd_in = 'python '
    else: cmd_in = 'python3 '

    for dir in os.listdir():
        if 'Sbot' in dir:
            if dir.replace('Sbot_', '').replace('.py', '') in SCRAPE_THESE_WEBSITES:
                list_of_bots.append(dir)

    print(f'STARTING THE SCRAPPER...\nBOTS: {list_of_bots}\n')
    for bot in list_of_bots:
        print(f'{bot} run:\n')
        os.system(cmd_in + bot)

