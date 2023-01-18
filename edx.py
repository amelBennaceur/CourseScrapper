import re
from urllib.request import urlopen, Request

from bs4 import BeautifulSoup, PageElement
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from coursera_scrapper_categories import CourseInfo, CHROME_DRIVER_PATH, process_pages


def process_course_info(card_content: WebElement,
                        class_link_class_name: str = "discovery-card-link") -> CourseInfo:
    course_url: str = card_content.find_element(by=By.CLASS_NAME, value=class_link_class_name).get_property("href")

    request: Request = Request(course_url, headers={'User-Agent': 'Mozilla/5.0'})
    course_as_html = urlopen(request)

    beautiful_soup: BeautifulSoup = BeautifulSoup(course_as_html.read(), 'html.parser')

    headers: list[PageElement] = list(beautiful_soup.findAll("h1"))
    course_title: str = headers[0].getText()

    course_descriptions: list[PageElement] = list(beautiful_soup.select("div.at-a-glance li"))
    partner: str = course_descriptions[0].getText().split(":")[1]
    product_type: str = course_descriptions[1].getText().split(":")[1]

    enrollment_element: PageElement = list(beautiful_soup.select("#enroll div.small"))[0]
    enrollment: str = enrollment_element.getText().replace(",", "")
    enrollment: str = re.findall(r'\d+', enrollment)[0]

    return CourseInfo(course_title, partner, product_type, enrollment)


def main():
    chrome_options: Options = Options()
    chrome_driver: WebDriver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, options=chrome_options)
    chrome_driver.get('https://www.edx.org/search?q=%22%22&tab=course')

    result_class_name: str = "static-card-list"
    item_class_name: str = "discovery-card"
    next_page_selector: str = "button.next.page-link"
    process_pages(chrome_driver, result_class_name=result_class_name, item_class_name=item_class_name,
                  process_course_function=process_course_info,
                  next_page_selector=next_page_selector)

    chrome_driver.close()


if __name__ == "__main__":
    main()
