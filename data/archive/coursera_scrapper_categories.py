from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import csv
from datetime  import datetime
import pandas as pd


CHROME_DRIVER_PATH = '/usr/local/bin/chromedriver'
course_number = 0
max_pages = 0
stop = False

class CourseInfo(object):

    def __init__(self, course_title, partner, product_type, enrollment, rating, level):
        self.course_title = course_title
        self.partner = partner
        self.product_type = product_type
        self.enrollment = enrollment
        self.rating = rating
        self.level = level

    def __str__(self):
        return '{self.course_title}, {self.partner}, ' \
               '{self.product_type}, {self.enrollment}, {self.rating}, {self.level}'.format(self=self)


def process_course_info(card_content: WebElement, title_class_name='card-title',
                        partner_class_name='partner-name',
                        product_type_class_name='product-type-pill-wrapper',
                        enrollment_class_name='enrollment-number',
                        rating_class_name='ratings-text',
                        level_class_name='cds-1 difficulty css-lqm5si cds-3'
                        ) -> CourseInfo:
    try:
        course_title: str = card_content.find_element(by=By.CLASS_NAME, value=title_class_name).text
    except NoSuchElementException:
        course_title: str = ""
    try:
        partner: str = card_content.find_element(by=By.CLASS_NAME, value=partner_class_name).text
    except NoSuchElementException:
        partner: str = ""
    try:
        product_type: str = card_content.find_element(by=By.CLASS_NAME, value=product_type_class_name).text
    except NoSuchElementException:
        product_type: str = ""
    try:
        enrollment: str = card_content.find_element(by=By.CLASS_NAME, value=enrollment_class_name).text
    except NoSuchElementException:
        enrollment: str = "0"
    try:
        rating: str = card_content.find_element(by=By.CLASS_NAME, value=rating_class_name).text
    except NoSuchElementException:
        rating: str = "0"
    try:
        level: str = card_content.find_element(by=By.CLASS_NAME, value=level_class_name).text
    except NoSuchElementException:
        level: str = "mixed"
    return CourseInfo(course_title, partner, product_type, enrollment,rating,level)


def process_page(chrome_driver, coursera_subject,FL_category, duration,timeout=10, result_class_name='ais-InfiniteHits-list', item_class_name='card-content'):

    try:
        _ = WebDriverWait(chrome_driver, timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, result_class_name)))

        course_content: list[WebElement] = chrome_driver.find_elements(by=By.CLASS_NAME, value=item_class_name)

        global course_number
        rows = []
        if len(course_content)==0:
            global stop
            stop = True
        for course in course_content:
            course_number = course_number + 1
            course_info: CourseInfo = process_course_info(course)
            rows.append((course_number,course_info.course_title,course_info.partner,course_info.product_type,course_info.enrollment,coursera_subject,FL_category,duration,course_info.rating,course_info.level))
            print(str(course_number)+" : "+str(course_info))

        global writer
        writer.writerows(rows)

        # global max_pages
        # max_pages = max_pages +1
        #
        # if max_pages <= 101:
        #     next_page_element: WebElement = chrome_driver.find_element(by=By.CSS_SELECTOR,
        #                                                            value='button.box[data-track-component="pagination_right_arrow"]')
        #     ActionChains(chrome_driver).click(next_page_element).perform()
        #     process_page(chrome_driver)
    except (TimeoutException, WebDriverException) as e:
        print("Last page reached")
        stop = True



def start_scraping():
    chrome_options: Options = Options()
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument('--headless')
    chrome_driver: WebDriver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, options=chrome_options)


    filename = 'data/coursera_' + datetime.today().strftime('%Y-%m-%d_%H:%M') + '.csv'
    csvFile = open(filename, 'w+')
    global writer
    writer = csv.writer(csvFile)
    writer.writerow(
        ('index', 'title', 'partner', 'product_type', 'enrollment', 'coursera_subject', 'FL_category', 'duration', 'rating','level'))


    df = pd.read_csv('data/topics2.csv')
    duration = ["1-3%20Months","1-4%20Weeks","Less%20Than%202%20Hours","3%2B%20Months"]
    duration_readable = ["1-3 Months", "1-4 Weeks", "Less Than 2 Hours", "3+ Months"]
    for x in df.index:
        coursera_subject = df['coursera_subject'][x]
        coursera_subject_readable = df['coursera_subject_readable'][x]
        FL_category = df['FL_category'][x]
        for y in range(0,4):
            z=0
            global stop
            stop = False
            while z<100 and stop==False:
                z = z+1
                url = "https://www.coursera.org/search?page=" + str(
                    z) + "&index=prod_all_launched_products_term_optimization&topic=" + coursera_subject +"&productDurationEnum=" + duration[y]
                print(url)
                chrome_driver.get(url)
                process_page(chrome_driver,coursera_subject_readable,FL_category,duration_readable[y])

    csvFile.close()
    # store_data()

    # Closing
    chrome_driver.close()


if __name__ == "__main__":
    start_scraping()

