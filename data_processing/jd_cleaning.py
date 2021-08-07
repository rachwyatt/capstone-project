def clean_jd_linebreaks(ids, jds):
    """
    Given a list of ids and corresponding jds, clean up some linebreaks that's not recognized by
    sent_tokenizer in nltk package.

    re-insert into database for cleaned up jds, also delete rows that does not have enough sentences.

    NOT NEEDED IF DOES NOT USE SENT_TOKENIZER FUNCTION
    """
    import re

    break1 = r'&[a-z]{2,}[;/]*[a-z]*'
    break2 = '\n'
    break3 = '\xa0'

    new_short_jds = []
    failed = []
    for id_, jd in zip(ids, jds):
        new = re.split(break1, jd)
        if len(new)>1:
            new = [x.strip() for x in new if x.strip()!='']
            new_short_jds.append((id_, '.\n '.join(new)))
        else:
            new=jd.split(break2)
            if len(new)>1:
                new = [x.strip() for x in new if x.strip()!='']
                new_short_jds.append((id_, '.\n '.join(new)))
            else:
                new = jd.split(break3)
                if len(new)>1:
                    new = [x.strip() for x in new if x.strip()!='']
                    new_short_jds.append((id_, '.\n '.join(new)))
                else:
                    if len(jd)>100:
                        new_short_jds.append((id_, jd))
                    else:
                        failed.append((id_, jd))
                        
    # now remove failed jds
    delete_ids = [x[0] for x in failed]

    if len(delete_ids)>0:
        from tqdm import tqdm

        connection = pymysql.connect(host="job-market.chfeqjbmewii.us-west-1.rds.amazonaws.com",
                                     user="root",password="mads_capstone",database="capstone",
                                     port=3306,charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
        cursor = connection.cursor()

        for i in tqdm(range(len(delete_ids))):
            id_ = delete_ids[i]
            cursor.execute(f"""DELETE FROM jd WHERE id={id_};""")
            connection.commit()

        connection.close()
        

    df = pd.DataFrame(new_short_jds, columns = ['id', 'jd'])
    sent_cnt = [len(sent_tokenize(x[-1])) for x in new_short_jds]
    df['sent_len']=sent_cnt
    df['len'] = df['jd'].apply(len)
    
    connection = pymysql.connect(host="job-market.chfeqjbmewii.us-west-1.rds.amazonaws.com",
                             user="root",password="mads_capstone",database="capstone",
                             port=3306,charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()
    for i in tqdm(range(len(df))):
        id_test = df.iloc[i]['id']
        test = df.iloc[i]['jd'].replace('.\n', '').replace('\'', '')
        cursor.execute(f"""UPDATE jd SET job_description='{test}' WHERE id={id_test};""")
        connection.commit()

    connection.close()
    

def clean_html(jd):
    p = r'\<[\/a-z]+\>'
    found = re.findall(p, jd.lower())
    jd = re.sub(p, ' ', jd.lower())
    
    return found, jd


def clean_html2(jd):
    p = r'\<[\/a-z\d =\"]+\>'
    found = re.findall(p, jd.lower())
    keep = ['<num>', '<url>', '<email>']
    found = [x for x in found if x not in keep]
    for f in found:
        jd = jd.replace(f, ' ')
    return jd


def replace_email(jd):

    p = r'([\S]+@[a-z]+.org|[\S]+@[a-z]+.edu|[\S]+@[a-z\.]+.com)'
    found = re.findall(p, jd.lower())
    jd = re.sub(p, ' <email> ', jd.lower())
    
    return found, jd


def replace_nums(jd):
    p=r'([$x]*[\d]{2,}[\.\-\+\d\(\)k%\,]*|\d[\-\+\d]* year[s]*|\d[\-\+\d]* yr[s]*|#[ ]*[\d]+|\d+:[ ]*\d{2}[ amp]*)'
    found = re.findall(p, jd.lower())
    jd = re.sub(p, ' <num> ', jd.lower())
    jd = jd.replace(' amp ', ' ')
    jd = jd.replace(' quote ', ' ')
    jd = jd.replace(' quotes ', ' ')
    
    return found, jd


def replace_urls(jd):
    p=r'([\(]*http[s]*[\S]+|www.[\S]+)'
    found = re.findall(p, jd.lower())
    jd = re.sub(p, ' <url> ', jd.lower())
    
    return found, jd


def clean_paragraph(jd):
    p1 = r'[\n;\. ][ \w]+ is an equal opportunity[,]* [\w ,]+\.'
    p2 = r'[\n;\. ]click here to [\w ,]+'
    p3 = r'applicants will receive consideration [\w ]+'
    p4 = r'an equal [employment ]*opportunity[\w ,/\(\)]+'
    p5 = r'we are proud to[\w ,/]+\.'
    p6 = r'[\w ,/]+terms and conditions[\w ,/]+'
    p7 = r'[\w ,/\-\’—\']+race, color,[\w ,/\-\’—]+'
    p71 = r'[\w ,/\-\’—\']+, religion,[\w ,/\-\’—]+'
    p8 = r'follow us [\w ]+'
    p9 = r'diversity[ &]*inclusion[ \w,]+'
    patterns = [p1,p2,p3,p4,p5,p6,p7,p71,p8,p9]
    
    founds = []
    for p in patterns:
        founds += re.findall(p, jd.lower())
        jd = re.sub(p, ' ', jd.lower())
    
    return founds, jd


def remove_by_list(words_list, jd):
    """
    remove words in the words_list from jd. 
    jd is a text string
    """
    import regex as ree
    
    p1 = ree.compile(r" \L<words> ", words=words_list)
    p2 = ree.compile(r"\t\L<words> ", words=words_list)
    p3 = ree.compile(r",\L<words> ", words=words_list)
    p4 = ree.compile(r" \L<words>,", words=words_list)
    p5 = ree.compile(r" \L<words>\.", words=words_list)
    p6 = ree.compile(r" \L<words>\n", words=words_list)
    p7 = ree.compile(r" \L<words>/", words=words_list)
    p8 = ree.compile(r"/\L<words>", words=words_list)
    p9 = ree.compile(r"\(\L<words>", words=words_list)
    p10 = ree.compile(r" \L<words>\)", words=words_list)
    p11 = ree.compile(r"\n\L<words>", words=words_list)
    patterns=[p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11]

    for p in patterns:
        jd = p.sub('; ', jd)

    return jd


def load_agency_city():
    with open('agencies_list.txt', 'r') as f:
        agencies = f.readlines()
        f.close()
    agencies = [x.lower().strip() for x in agencies]

    with open('cities.txt', 'r') as f:
        cities = f.readlines()
        cities = [c.strip() for c in cities]
        f.close()

    return agencies, cities


def clean_agency_city(agencies, cities, jd):

    jd = remove_by_list(agencies, jd)
    jd = remove_by_list(cities, jd)

    return jd


def clean_jd_process(jd, agencies, cities):
    """
    jd is a text string, clean the job description with all functions defined above
    return the cleaned jd string.
    """
    jd = clean_html(jd)[1]
    jd = clean_html2(jd)
    jd = replace_nums(jd)[1]
    jd = replace_email(jd)[1]
    jd = replace_urls(jd)[1]

    jd = clean_paragraph(jd)[1]

    # some further regex cleaning

    p = r'(job description|company description|skill requirement[s]*|qualification|we are hiring|you have|you will)'
    jd = re.sub(p, '', jd)

    p2 = r'referral[s]* [\w,\'& \(\)\-]+'
    p3 = r'insurance [\w,\'& \(\)\-]+'
    p4 = r'health [\w,\'& \(\)\-]+'
    p5 = r'employment [\w,\'& \(\)\-]+'

    p = (f'({p2}|{p3}|{p4}|{p5})')

    jd = re.sub(p, '', jd)

    # clean up facebook staples
    if 'facebooks mission is to' in jd:
        cnt+=1
        jd = jd.split('facebooks mission is to')[0].strip()

    test=r'((apply (today|now|directly|for))[\w,\'& \(\)\-]*)'
    found2 = re.findall(test, jd.replace('u.s.', 'us'))
    if found2:
        found2 = found2[0][0]
        jd = jd.replace(found2, '')

    jd = clean_agency_city(agencies, cities, jd)

    return jd


def update_database():

    # load raw data from databse
    connection = pymysql.connect(host="job-market.chfeqjbmewii.us-west-1.rds.amazonaws.com",
                             user="root",password="mads_capstone",database="capstone",
                             port=3306,charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()
    sql = """select id, job_description from jd;"""
    cursor.execute(sql)
    data = cursor.fetchall()
    connection.close()

    # start cleaning of job description
    data = pd.DataFrame(data)
    agencies, cities = load_agency_city()
    data['cleaned_jd'] = data['job_description'].apply(lambda x: clean_jd_process(agencies, cities, x.lower()))

    # insert the cleaned jds into db
    connection = pymysql.connect(host="job-market.chfeqjbmewii.us-west-1.rds.amazonaws.com",
                             user="root",password="mads_capstone",database="capstone",
                             port=3306,charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()

    for i in tqdm(range(len(data))):
        id_ = data.iloc[i]['id']
        # remove single quotes
        cleaned_jd = data.iloc[i]['cleaned_jd'].replace('.\n', '').replace('\'', '')
        cursor.execute(f"""UPDATE jd SET cleaned_jd='{cleaned_jd}' WHERE id={id_};""")
        connection.commit()

    connection.close()


