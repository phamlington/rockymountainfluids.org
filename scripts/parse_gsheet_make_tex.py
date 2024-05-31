# Tyler Souders, August 3rd, 2022

# This script should be able to take a google drive link (what the form should output to)
# and convert the information to a nice tex file using some user-provided information.

# I don't have the time to put my heart and soul into this script, but it should be reasonably
# bulletproof as long as you tell the code which column everything is in. Obviously, you need
# to give everything a check before posting it anywhere, but it should make your life like
# 98% easier. Hope it helps!

import pandas as pd
import numpy as np
import datetime as dt
import string

def main():

    print('Starting Script to Generate RMFM Schedule and Program...\n')

    # Step 0: Some basic information
    confdate = [2022, 8, 9] #[year, month, day]
    acronyms = {'NREL', 'NCAR', 'CEAE'} # Put department acronyms here

    # Step 1: Download the responsese as a CSV and put it in the 'csv' directory
    filename = 'RMFM2022_responses.csv'

    # Step 2: In the above .csv file, you need to insert another column and shift
    # everything else s.t. column "A" is only integers with the header "Group". This
    # should be the only "annoying" part of this script - you need to sort the
    # responses into N appropriate topic groups indexing from 0 (for instance, 8 groups in 
    # 2022 would be 0, 1, 2, ..., 7). Then you need to fill out this dictionary with the 
    # corresponding group names and their respective session chair.
    gnames = {'Atmospheric and Aerodynamic Flows' : 'Matthew Munson', \
    'Biological Flows':'Bradford Smith', \
    'Reacting Flows':'Ciprian Dumitrache',\
    'Geophysical Flows':'Melissa Moulton',\
    'Nonequilibrium Flows and Energy Systems':'Brennan Sprinkle',\
    'CFD Techniques and Modeling':'Debanjan Mukherjee',\
    'Multiphase Flows':'Michael Calvisi',\
    'Turbulent Flows':'Ryan King'
    }

    session_ids = ['1A', '1B', '1C', '2A', '2B', '2C', '3A', '3C']
    session_room = ['AERO 111', 'AERO 120', 'AERO 114', 'AERO 111', 'AERO 120', 'AERO 114', 'AERO 111', 'AERO 114']
    session_start_times = np.array([[8, 45], [8, 45], [8, 45], \
     [10,30], [10,30], [10,30], [3,15], [3,15], [3,15]]) # format: [hour, minute]

    talk_length = 15 #minutes

    # Step 2: Provide Column Necessary Column Names
    # Note that we assume that everything after "Add more authors" will never change... ever
    # Please don't change that part of the sheet or else this will become a nightmare
    colnames = {'email':'C', 'diet_restriction':'E', 'needsParking':'F', \
    'presenterFirstName':'K', 'presenterLastName':'L', \
    'presenterAffil':'N', 'presenterDept':'O', 'presentationTitle':'P', 'abstract':'Q', 'keywords':'R', 'addAuthors':'S'}

    # ----------- Don't Edit Below This Line :) ------------

    # Echo some basic debug information
    print(f'Number of groups = {len(gnames)}')

    # Convert Excel to Index
    colnums = col_2_index(colnames)

    # Load the file
    print('Loading .csv File...')
    df = pd.read_csv(f'csv/{filename}')
    df.fillna(-1, inplace=True)
    df = df.to_numpy()

    # Check the number of specified groups
    numGroups = int(df[:, 0].max()) + 1
    print(f'Reading {numGroups} groups from the csv file')

    # Determine the number of talks for each group
    pres_in_group = []
    for i in range(numGroups):

        mask = (df[:, 0] == i)
        pres_in_group.append(df[mask,0].shape[0])

    print(f'List of groups from user input: {[keys for keys in gnames]}')
    print(f'Number of talks found in each group : {pres_in_group}\n')

    # Fix capitalization for names and keywords
    # df[:, colnums['presenterFirstName']] = str(df[:, colnums['presenterFirstName']]).title()
    # df[:, colnums['presenterLastName']] = str(df[:, colnums['presenterLastName']]).title()
    # df[:, colnums['presentationTitle']] = str(df[:, colnums['presentationTitle']]).title()
    # df[:, colnums['keywords']] = str(df[:, colnums['keywords']]).title()
    # df[:, colnums['presenterAffil']] = str(df[:, colnums['presenterAffil']]).title()


    # Start Routine to Write schedule.tex
    print('Writing Schedule ...')
    with open('tex/schedule.tex', "w") as f:

        for i in range(numGroups):

            # Find some info
            t_len = dt.timedelta(minutes=talk_length)
            t_start = dt.datetime(confdate[0], confdate[1], confdate[2], \
                session_start_times[i, 0], session_start_times[i, 1])
            t_end = t_start+t_len*pres_in_group[i]

            t_start_str = t_start.strftime('%I:%M %p')
            t_end_str = t_end.strftime('%I:%M %p')

            t_id = session_ids[i]
            for ii, key in enumerate(gnames.keys()):
                if ii == i:
                    t_group=key

            # Write the first line
            tex = f'\\subsection*{{Session {t_id}: {t_group} \\\\ {t_start_str}  -- {t_end_str} ({session_room[i]})}}\n'
            f.write(tex)
            f.write('\\begin{enumerate}\n')
            # Find indices for this section
            rows = np.array(np.where(df[:, 0] == i))

            # Now loop to write each presentation
            for j, row in enumerate(rows[0]): 

                firstname = df[row, colnums['presenterFirstName']].title()
                lastname = df[row, colnums['presenterLastName']].title()
                title = df[row, colnums['presentationTitle']].title()
                affil = df[row, colnums['presenterAffil']].title()

                prestime = (t_start+j*t_len).strftime('%I:%M %p')

                tex = f'\\item [{prestime}] {firstname} {lastname} ({affil}) \\\\ \hyperlink{{{firstname}{lastname}}}{{\it {title} }}\n'
                f.write(tex)

            f.write('\\end{enumerate}\n')

    # Now write the abstracts file
    print('Writing Abstracts ...')
    with open('tex/abstracts.tex', 'w') as f:

        for i in range(numGroups):

            # Find some info
            t_len = dt.timedelta(minutes=talk_length)
            t_start = dt.datetime(confdate[0], confdate[1], confdate[2], \
                session_start_times[i, 0], session_start_times[i, 1])
            t_end = t_start+t_len*pres_in_group[i]

            t_start_str = t_start.strftime('%I:%M %p')
            t_end_str = t_end.strftime('%I:%M %p')

            t_id = session_ids[i]
            for ii, key in enumerate(gnames.keys()):
                if ii == i:
                    t_group=key

            # Find indices for this section
            rows = np.array(np.where(df[:, 0] == i))

            # Now loop to write each presentation
            for j, row in enumerate(rows[0]): 

                firstname = df[row, colnums['presenterFirstName']].title().strip()
                lastname = df[row, colnums['presenterLastName']].title().strip()
                title = df[row, colnums['presentationTitle']].title().strip()
                affil = df[row, colnums['presenterAffil']].title().strip()
                dept = df[row, colnums['presenterDept']]
                
                # Filter the acronym departments
                if dept != -1 and not str(dept).lower() in([name.lower() for name in acronyms]): 
                    dept = dept.title().strip()
                elif dept !=-1:
                    dept = str(dept).upper().strip()
                else:
                    dept = ''

                abstract = df[row, colnums['abstract']]
                prestime = (t_start+j*t_len).strftime('%I:%M %p')

                
                hypertarget = f'{firstname}{lastname}'
                
                # Write the title
                f.write(f'\\hypertarget{{{hypertarget}}}{{\subsection*{{\color{{CUGOLD}} {title}}}}} \\vsp \n')

                # Write presenter's name underlined - it is assumed that the first author is the presenter
                if dept!='':
                    f.write(f'\\underline{{{firstname} {lastname}}}, \\textit{{{dept}, {affil}}}\\\\ \n')
                else:
                    f.write(f'\\underline{{{firstname} {lastname}}}, \\textit{{{affil}}}\\\\ \n')

                # Write out the rest of the authors
                checkcol = colnums['addAuthors']

                # Add however many authors they indicated
                while 'yes' in df[row, checkcol].lower():

                    co_firstname = df[row, checkcol+2].title().strip()
                    co_lastname = df[row, checkcol+3].title().strip()
                    co_affil = df[row, checkcol+5].title().strip()
                    co_dept = df[row, checkcol+6]

                    # Filter the acronym departments
                    if co_dept != -1 and not str(co_dept).lower() in([name.lower() for name in acronyms]): 
                        co_dept = co_dept.title().strip()
                    elif co_dept !=-1:
                        co_dept = str(co_dept).upper().strip()
                    else:
                        co_dept = ''

                    # Add the co-author
                    if co_dept!='':
                        f.write(f'{{{co_firstname} {co_lastname}}}, \\textit{{{co_dept}, {co_affil}}}\\\\ \n')
                    else:
                        f.write(f'{{{co_firstname} {co_lastname}}}, \\textit{{{co_affil}}}\\\\ \n')

                    # increment checkcol
                    checkcol += 7

                # Now write the abstract out
                f.write('\\vspace{-0.1 in} \\\\ \n')

                # Split based on paragraphs
                abstract = abstract.split('\n')
                print(abstract)
                for pcount, para in enumerate(abstract):
                    f.write(f'\\noindent {para} \\\\ \n')

                # Write hyperlink back to toc
                f.write('\\begin{flushright}\\vspace{-0.2 in}\\hyperlink{toc}{Back to table of contents}\\end{flushright}\\vspace{-0.2 in}\n')


def col_2_index(colnames):

    # Takes dictionary of column names and returns dictionary of indices
    for key, value in colnames.items():

        num = 0
        if value in string.ascii_letters:

            num = num*26 + (ord(value.upper()) - ord('A'))
            colnames[key] = num

    return colnames


if __name__ == "__main__": main()