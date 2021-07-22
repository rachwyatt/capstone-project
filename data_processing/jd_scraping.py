import requests
from bs4 import BeautifulSoup
import time
from selenium import webdriver
import chromedriver_autoinstaller
from tqdm import tqdm
import pymysql.cursors
import pandas as pd
from datetime import datetime
import json
from jd_parse_utils import get_skill_education

chromedriver_autoinstaller.install()
today = str(datetime.now().date())


def load_titles(jobtitles='jobtitles_ds.txt'):
    with open(jobtitles, 'r') as f:
        titles = f.readlines()
    titles = [x.lower().strip().replace(' ', '%20') for x in titles]
    return titles


def scrape_parent_links():
    print('Scraping job pages links...')
    joblinks_batch = []
    titles = load_titles()
    ## this code only deals with 30 pages for each query (seems that's what glassdoor release)
    for keyword in tqdm(titles):
        link = f'https://www.glassdoor.com/Job/jobs.htm?sc.keyword={keyword}&fromAge=1'
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        wd = webdriver.Chrome('chromedriver', options=chrome_options)
        wd.get(link)
        raw = wd.page_source
        soup = BeautifulSoup(raw, 'lxml')
        joblinks = list(set([x['href'] for x in soup.find_all('a', {'class': 'jobLink'})]))
        while True:
            try:
                wd.find_element_by_xpath('//*[@id="FooterPageNav"]/div/ul/li[7]/a').click()
                time.sleep(4)

                for l in BeautifulSoup(wd.page_source, 'lxml').find_all('a'):
                    try:
                        link = (l['href'])
                        if link.startswith('/partner/'):
                            joblinks.append(link)
                    except:
                        continue

                joblinks = list(set(joblinks))

            except:
                break
                wd.close()

        wd.close()
        joblinks_batch += joblinks

    return joblinks_batch


def glassdoor_clean(soup):
    cleaned = {}

    parsed = []
    for x in soup.find_all('script'):
        try:
            parsed.append(json.loads(x.text))
        except:
            try:
                temp = str(x).split('<script type="application/ld+json">')[-1].split('</script>')[0]
                temp = json.loads(temp)
                parsed.append(temp)
            except:
                continue

    if not parsed:
        return {}

    try:
        title = parsed[0]['title']
        company = parsed[0]['hiringOrganization']['name']
        addr = parsed[0]['jobLocation']['address']
        try:
            location = str(addr['addressLocality']) + ', ' + str(addr['addressRegion'])
        except:
            location = str(addr['addressRegion'])
    except:
        title = ''
        company = ''
        location = ''

    raw = parsed[0]
    try:
        jd = BeautifulSoup(parsed[0]['description'], 'lxml').text
    except:
        jd = parse_jd(soup)

    cleaned['title'] = title
    cleaned['company'] = company
    cleaned['location'] = location
    cleaned['jd'] = jd
    cleaned['meta'] = raw

    return cleaned


def parse_jd(soup):
    jd = soup.find('div', {'id': 'JobDescriptionContainer'})
    if not jd:
        return soup
    children = []
    for ch in jd.findChildren(recursive=False):
        for ch2 in ch.findChildren(recursive=False):
            ch3 = ch2.findChildren(recursive=False)
            if ch3:
                for x in ch3:
                    children += x
            else:
                children += ch2

    elements = []
    for n, ch in enumerate(children):
        try:
            sub = ch.find_all('li')
            if len(sub) > 1:
                elements += sub
            else:
                elements.append(ch)
        except:
            elements.append(ch)

    jd_cleaned = []
    for x in elements:
        try:
            txt = x.text.strip()
            if txt != '':
                jd_cleaned.append(txt)
        except:
            jd_cleaned.append(str(x).strip())

    jd_cleaned = '\n'.join(jd_cleaned)

    return jd_cleaned


def scrape_job_page(joblinks_batch):
    print('Scraping each job pages...')
    cleaned_dicts = []

    chrome_options2 = webdriver.ChromeOptions()
    chrome_options2.add_argument('--headless')
    chrome_options2.add_argument('--no-sandbox')
    chrome_options2.add_argument('--disable-dev-shm-usage')

    for l in tqdm(joblinks_batch):
        wd2 = webdriver.Chrome('chromedriver', options=chrome_options2)
        wd2.get("https://www.glassdoor.com" + l)
        raw2 = wd2.page_source
        cleaned = glassdoor_clean(BeautifulSoup(raw2, 'lxml'))
        cleaned_dicts.append(cleaned)
        wd2.close()

    cleaned_dicts = [x for x in cleaned_dicts if x != {}]
    cleaned = pd.DataFrame(cleaned_dicts)
    cleaned.columns = ['job_title', 'company_name', 'location', 'job_description', 'meta']

    metas = cleaned['meta'].tolist()

    date_posted = []
    job_types = []
    urls = []

    for meta in metas:
        try:
            d1 = meta['datePosted']
        except:
            d1 = today
        date_posted.append(d1)
        try:
            d2 = meta['employmentType']
        except:
            d2 = ''
        job_types.append(d2)
        try:
            d3 = meta['url']
        except:
            d3 = ''
        urls.append(d3)

    cleaned['url'] = urls
    cleaned['job_type'] = job_types
    cleaned['date_posted'] = date_posted
    cleaned = cleaned[cleaned['url'] != '']
    df = cleaned.fillna('')
    df['crawl_timestamp'] = str(today)
    df = df.rename(columns={'date_posted': 'post_date'})
    df['job_board'] = 'glassdoor'

    edu = []
    skill = []
    for jd in df['job_description'].tolist():
        e, s = get_skill_education(jd)
        edu.append(e)
        skill.append(s)

    df['skill'] = skill
    df['education'] = edu

    return df


def insert_into_db(df):
    print('Inserting into DB...')

    connection = pymysql.connect(host="job-market.chfeqjbmewii.us-west-1.rds.amazonaws.com", user="root",
                                 password="mads_capstone", database="capstone", port=3306,
                                 charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()

    sql = """INSERT INTO jd (crawl_timestamp, url, job_title, company_name,
    post_date, job_description, job_type, job_board, location, skill, education) 
    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""

    dup_cnt = 0
    commit_cnt = 0
    for i in tqdm(range(len(df))):
        try:
            data = df.iloc[i]
            cursor.execute(sql, (data['crawl_timestamp'], data['url'], data['job_title'],
                                 data['company_name'], data['post_date'], data['job_description'],
                                 data['job_type'], data['job_board'], data['location'], data['skill'],
                                 data['education']))
            connection.commit()
            commit_cnt += 1
        except pymysql.IntegrityError as err:
            dup_cnt += 1

    connection.close()

    print('=====> newly commited entries:', commit_cnt, '\nduplicated entries:', dup_cnt)


def main():
    job_links_batch = scrape_parent_links()
    df = scrape_job_page(job_links_batch)
    insert_into_db(df)
