import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import re

outpath = '/Users/spk/Documents/Code/Python/webscrape_proj/outputs/banff_national_park_trailforks.csv'

#url = 'https://www.trailforks.com/region/banff/trails/'
url = 'https://www.trailforks.com/region/banff-national-park-20480/trails/'

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
DRIVER_BIN = os.path.join(PROJECT_ROOT, "chromedriver")

options = webdriver.ChromeOptions()
options.add_argument("--incognito")
options.add_argument('--headless')

driver = webdriver.Chrome(executable_path=DRIVER_BIN)

driver.maximize_window()
timeout = 5

driver.get(url)
trail_table_elem = WebDriverWait(driver, timeout)\
    .until(ec.presence_of_all_elements_located((By.ID, 'trails_table')))

col_names = []
tbl_heads = driver.find_elements(By.TAG_NAME, 'thead')
for th in tbl_heads[0].find_elements(By.TAG_NAME, 'th'):
    col_names.append(th.text)
tbl_rows = driver.find_elements(By.TAG_NAME, "tr")

df_out = pd.DataFrame(columns=['title', 'trail_url', 'region', 'region_url', 'star_rating', 'star_votes',
                               'descent', 'climb'])
idx=0
for row in tbl_rows:
    try:
        row_cols = row.find_elements(By.TAG_NAME, "td")
        title = row_cols[col_names.index('title')].text
        trail_url = row_cols[col_names.index('title')].find_element(By.TAG_NAME, 'a').get_attribute('href')
        region = row_cols[col_names.index('riding area')].text
        region_url = row_cols[col_names.index('riding area')].find_element(By.TAG_NAME, 'a').get_attribute('href')
        star_votes = row_cols[col_names.index('rating')].text
        star_rating = row_cols[col_names.index('rating')]\
            .find_element(By.CLASS_NAME, 'hovertip').get_attribute('data-score')
        distance = row_cols[col_names.index('distance')].text
        descent = row_cols[col_names.index('descent')].text
        climb = row_cols[col_names.index('climb')].text

        df_tmp = pd.DataFrame(dict(title=title,
                                   trail_url=trail_url,
                                   region=region,
                                   region_url=region_url,
                              star_rating=star_rating,
                                   star_votes=star_votes,
                              distance=distance,
                              descent=descent,
                              climb=climb), index=[idx])
        df_out = df_out.append(df_tmp)
        del [title, trail_url, region, region_url, star_rating, distance, descent,
             df_tmp]
        idx += 1
    except IndexError:
        print('skipping row')

for idx_row, row in df_out.iterrows():
    print("\n" + str(idx_row + 1) + " of " + str(len(df_out) + 1))
    # Open a new window
    driver.execute_script("window.open('');")
    # Switch to the new window
    driver.switch_to.window(driver.window_handles[1])
    driver.get(row['trail_url'])

    trail_deets = driver.find_element(By.ID, 'traildetails_display')
    trail_spec_terms = trail_deets.find_elements(By.XPATH, "//li//div[@class='term']")
    trail_spec_defs = trail_deets.find_elements(By.XPATH, "//li//div[contains(@class, 'def')]")
    for idx_spec, spec in enumerate(trail_spec_terms):
        print(spec.text)
        if spec.text == "Activities":
            trail_activities = trail_spec_defs[idx_spec].find_elements(By.CLASS_NAME, 'badgesquare')
            df_out.loc[idx_row, 'activities'] = ','.join([x.text for x in trail_activities])
        if spec.text == 'Difficulty Rating':
            df_out.loc[idx_row, 'difficulty_rating'] = trail_spec_defs[idx_spec]\
                .find_element(By.XPATH, "//span[contains(@class, 'dicon')]")\
                .get_attribute('title')
        if spec.text == 'Voted Difficulty':
            df_out.loc[idx_row, 'voted_difficulty'] = trail_spec_defs[idx_spec]\
                .find_element(By.XPATH, "//span[contains(@class, 'dicon')]")\
                .get_attribute('title')
        if spec.text == 'Trail Type':
            df_out.loc[idx_row, 'trail_type'] = trail_spec_defs[idx_spec].text
        if spec.text == 'Bike Type':
            df_out.loc[idx_row, 'bike_type'] = trail_spec_defs[idx_spec].text.replace(" ", "")
        if spec.text == 'Trail Usage':
            df_out.loc[idx_row, 'trail_usage'] = trail_spec_defs[idx_spec].text
        if spec.text == 'Direction':
            df_out.loc[idx_row, 'direction'] = trail_spec_defs[idx_spec].text
        if spec.text == 'Climb Difficulty':
            df_out.loc[idx_row, 'climb_difficulty'] = trail_spec_defs[idx_spec] \
                .find_element(By.XPATH, "//span[contains(@class, 'dicon')]") \
                .get_attribute('title')
        if spec.text == 'Physical Rating':
            df_out.loc[idx_row, 'physical_rating'] = trail_spec_defs[idx_spec].text
        if spec.text == 'Dogs Allowed':
            df_out.loc[idx_row, 'dogs_allowed'] = trail_spec_defs[idx_spec].text
        if spec.text == 'eBike Allowed':
            df_out.loc[idx_row, 'ebike_allowed'] = trail_spec_defs[idx_spec].text
        if spec.text == 'Global Ranking':
            df_out.loc[idx_row, 'global_ranking'] = re.findall('(?<=#)[0-9]+', trail_spec_defs[idx_spec].text)[0]
            df_out.loc[idx_row, 'global_ranking_type'] = re.findall('(?<=in )(.*)', trail_spec_defs[idx_spec].text)[0]
        if spec.text == 'Local Popularity':
            df_out.loc[idx_row, 'local_popularity'] = re.findall('^([^in]*) in*', trail_spec_defs[idx_spec].text)[0]
            lp_xtra = re.findall('[+]', trail_spec_defs[idx_spec].text)
            if len(lp_xtra) != 0:
                df_out.loc[idx_row, 'local_popularity_type'] = re.sub(' \[\+\]', '', re.findall('(?<=in )(.*)',
                                                                          trail_spec_defs[idx_spec].text)[0])
                lp_xtras1 = trail_spec_defs[idx_spec].find_element(By.ID, 'popularity_activity')
                lp_xtras2 = lp_xtras1.find_elements(By.TAG_NAME, 'li')
                for idx_lp_xtra, lp_xtra in enumerate(lp_xtras2):
                    lp_pop = lp_xtra.find_elements(By.TAG_NAME, "span")
                    df_out.loc[idx_row, 'local_popularity_' + str(idx_lp_xtra + 1)] = \
                        lp_pop[0].get_attribute('innerHTML')
                    df_out.loc[idx_row, 'local_popularity_type' + str(idx_lp_xtra + 1)] = \
                        re.findall('(?<=in )(.*)', lp_pop[1].get_attribute('innerHTML'))[0]
            else:
                df_out.loc[idx_row, 'local_popularity_type'] = re.findall('(?<=in )(.*)',
                                                                          trail_spec_defs[idx_spec].text)[0]
    driver.close()
    driver.switch_to.window(driver.window_handles[0])


with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    print(df_out)

df_out.to_csv(outpath, index_label='index')