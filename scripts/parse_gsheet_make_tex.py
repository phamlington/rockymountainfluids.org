# Tyler Souders, August 3rd, 2022

# This script should be able to take a google drive link (what the form should output to)
# and convert the information to a nice tex file using some user-provided information.

# I don't have the time to put my heart and soul into this script, but it should be reasonably
# bulletproof as long as you tell the code which column everything is in. Obviously, you need
# to give everything a check before posting it anywhere, but it should make your life like
# 98% easier. Hope it helps!

import pandas as pd

def main():

    # Step 1: Download the responsese as a CSV and put it in the 'csv' directory
    filename = 'RMFM2022_responses.csv'

    # Step 2: Provide the index values of column types
    col_locs = {
        "email" : 1
    }

    # Run the script
    do_it(filename, col_locs)


def do_it(filename, col_locs):

    # Import the csv to a dataframe
    df = pd.read_csv(f'csv/{filename}', keep_default_na=False)

    for key in df.keys(): print(key)
    
    # Find those who are presenting versus attending only
    # is_presenting = df[:, 'Will you be presenting your work at RMFM 2022?'] == 'Yes, I will be presenting at RMFM 2022.'

if __name__ == "__main__": main()