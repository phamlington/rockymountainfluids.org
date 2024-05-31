import numpy as np
import csv
import datetime as dt


# User inputs -----------------------------------------------------------------

print('generating RMFM program ...')

# Start times for each session (format: year, month, day, hour, minute)
start_times = [dt.datetime(2020, 8, 4, 8,  30), \
               dt.datetime(2020, 8, 4, 8,  30), \
               dt.datetime(2020, 8, 4, 8,  30), \
               dt.datetime(2020, 8, 4, 10, 00), \
               dt.datetime(2020, 8, 4, 10, 00), \
               dt.datetime(2020, 8, 4, 10, 00), \
               dt.datetime(2020, 8, 4, 11, 30), \
               dt.datetime(2020, 8, 4, 11, 30), \
               dt.datetime(2020, 8, 4, 11, 30)]

session_ids = ['1A', '1B', '1C', \
               '2A', '2B', '2C', \
               '3A', '3B', '3C']
ntalk = 5
# print(start_times)
talk_length = dt.timedelta(seconds=300)
# print(start_times)
# print(start_times[0].time())
# print(start_times[0].time().strftime('%I:%M %p').lstrip("0").replace(" 0", " "))


# Assuming the following row format of csv:
#    Row 1:   
#    Row 2:   
#    Row 3:   
#    Row 4:   
#    Row ?:   
#    Row ?+1: 
#    Row ?+2:

# Assuming the following column format of csv:
#    Line 1:   Session 1 Name
#    Line 2:   - first presentation
#    Line 3:   - second presentation
#    Line 4:   ...
#    Line ?:   Session2 Name 
#    Line ?+1: - first presentation
#    Line ?+2: - ...


# Extract information and categorize into sessions ----------------------------
print('extracting data from the abstracts.csv ...')

# Load abstracts
with open('../abstracts.csv', newline='') as f:
    reader = csv.reader(f)
    lines  = list(reader)

# Sort data
first_names = [] # for first author
last_names  = [] # for first author
positions = [] # for first author
schools = []# for first author
affiliations = []# for first author
titles = []
abstracts = []
keywords = []
coauthors = [] # all details
session_nums = []
isession = -1
sessions = []
for l in lines:
    # Check if this line is a session title
    if l[0] != '' and l[1] == '':
        sessions.append(l[0])
        isession += 1

    # Check if this line is blank
    elif l[0] == '':
        pass

    # Only other option is if the line is a presentation
    else:
        first_names.append(l[0].lstrip(" ").rstrip(" "))
        last_names.append(l[1].lstrip(" ").rstrip(" "))
        positions.append(l[2])
        schools.append(l[3])
        affiliations.append(l[4])
        titles.append(l[5])
        abstracts.append(l[6])
        keywords.append(l[7])
        coauthors.append(l[8:])
        session_nums.append(isession)

# Check that we have the correct amount of sessions
assert len(sessions) == isession + 1
assert len(sessions) == len(start_times)
assert len(sessions) == len(session_ids)

# Write out schedule ----------------------------------------------------------
print('writing out schedule.tex ...')
fid = open('schedule.tex', 'w')
fid.write('% This file was written by `generate_program.py` and zoom links ' + \
    'added afterwards\n\n')

isession = -1
italk = 0
for i in range(len(abstracts)):

    # Write out session name
    if i == 0 or session_nums[i] != isession:
        isession += 1

        stime = start_times[isession]
        etime = stime + ntalk*talk_length
        sstr = stime.time().strftime('%I:%M %p').lstrip("0").replace(" 0", " ")
        estr = etime.time().strftime('%I:%M %p').lstrip("0").replace(" 0", " ")

        fid.write('\\subsection*{Session %s: %s \\\\ %s -- %s (ZOOM)}\n' % 
            (session_ids[isession], sessions[isession], sstr, estr))
        fid.write('\\begin{enumerate}\n')


    # Write out speaker and title
    stime = start_times[isession] + italk*talk_length
    sstr = stime.time().strftime('%I:%M %p').lstrip("0").replace(" 0", " ")
    fid.write('\\item[%s] %s %s (%s) \\\\\n' % \
        (sstr, first_names[i], last_names[i], schools[i]))
    fid.write('\t \\hyperlink{%s}{{\\it %s}}\n' % \
        (last_names[i], titles[i]))
    italk += 1

    # Finalize session
    if i < len(abstracts)-1:
        if session_nums[i+1] != isession:
            fid.write('\\end{enumerate}\n%%\n')
            italk = 0
    else:
        fid.write('\\end{enumerate}\n')

fid.close()

# Write out talks -------------------------------------------------------------
print('writing out abstracts.tex ...')
fid = open('abstracts.tex', 'w')
fid.write('% This file was written by `generate_program.py`\n\n')

# Sort abstracts by last name of first author
isort = sorted(range(len(last_names)), key=lambda k: last_names[k])
first_names  = [first_names[i] for i in isort]
last_names   = [last_names[i] for i in isort]
positions    = [positions[i] for i in isort]
schools      = [schools[i] for i in isort]
affiliations = [affiliations[i] for i in isort]
titles       = [titles[i] for i in isort]
abstracts    = [abstracts[i] for i in isort]
keywords     = [keywords[i] for i in isort]
coauthors    = [coauthors[i] for i in isort]

# Write file
for i in range(len(abstracts)):
    # Add hyperlinking
    fid.write('\\hypertarget{%s}{\\subsection*{\\color{Blue} %s}}\\vsp\n' % \
        (last_names[i], titles[i]))

    # Write first author
    fid.write('\\underline{%s %s}, \\textit{%s, %s}\\\\\n' % \
        (first_names[i], last_names[i], affiliations[i], schools[i]))

    # Write co-authors
    coauth = coauthors[i]
    if coauth[0] == 'Yes':
        for j in range(0, len(coauth), 7):
            fname = coauth[j+1]
            lname = coauth[j+2]
            affil = coauth[j+5].replace(";", "; ")
            depart = coauth[j+6]
            if fname != '' and lname != '':
                fid.write('{%s %s}, \\textit{%s, %s} \\\\\n' % \
                    (fname, lname, depart,affil))
            if coauth[j+7] == 'No':
                break

    # Add abstract
    fid.write('\\vspace{-0.1 in} \\\\\n')
    fid.write('%s \\\\\n' % abstracts[i])
    fid.write('\\begin{flushright}\\vspace{-0.2 in} \\hyperlink{toc}' + \
        '{Back to table of contents} \\end{flushright}\\vspace{-0.2 in} \n\n')

fid.close()



# Finished --------------------------------------------------------------------
print('finished generating RMFM program')
