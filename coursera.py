from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

CHROME_DRIVER_PATH = '/usr/local/bin/chromedriver'


class CourseInfo(object):

    def __init__(self, course_title, partner, product_type, enrollment):
        self.course_title = course_title
        self.partner = partner
        self.product_type = product_type
        self.enrollment = enrollment

    def __str__(self):
        return 'Title: {self.course_title} Partner: {self.partner} ' \
               'Product type: {self.product_type} Enrollment: {self.enrollment}'.format(self=self)


def process_course_info(card_content: WebElement, title_class_name='card-title',
                        partner_class_name='partner-name',
                        product_type_class_name='product-type-pill-wrapper',
                        enrollment_class_name='enrollment-number') -> CourseInfo:
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
    return CourseInfo(course_title, partner, product_type, enrollment)

    return CourseInfo(course_title, partner, product_type, enrollment)


def process_page(chrome_driver, timeout=10, result_class_name='ais-InfiniteHits-list', item_class_name='card-content'):
    try:
        _ = WebDriverWait(chrome_driver, timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, result_class_name)))
    finally:
        course_content: list[WebElement] = chrome_driver.find_elements(by=By.CLASS_NAME, value=item_class_name)

        for course in course_content:
            course_info: CourseInfo = process_course_info(course)
            print(course_info)

        next_page_element: WebElement = chrome_driver.find_element(by=By.CSS_SELECTOR,
                                                                   value='button.box[data-track-component="pagination_right_arrow"]')
        ActionChains(chrome_driver).click(next_page_element).perform()
        process_page(chrome_driver)


def start_scraping():
    chrome_options: Options = Options()
    chrome_options.add_argument('--headless')
    chrome_driver: WebDriver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, options=chrome_options)

    chrome_driver.get('https://www.coursera.org/courses')
    process_page(chrome_driver)
    chrome_driver.close()


if __name__ == "__main__":
    start_scraping()