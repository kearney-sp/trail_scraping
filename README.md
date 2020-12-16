# How to use

Go here to launch: https://mybinder.org/v2/gh/kearney-sp/trail_scraping.git/main?filepath=trailforks_scraper.ipynb

Need to add:
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install(), chrome_options=options)
