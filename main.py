import re
import csv
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException

file_path = "links_to_download.xlsx"
df = pd.read_excel(file_path)

csv_file = open("output.csv", "w", newline="", encoding="utf-8")
csv_writer = csv.writer(csv_file)
csv_writer.writerow(["Title", "Price", "Availability", "Producer"])

service = ChromeService()
driver = webdriver.Chrome(service=service)

for index, row in df.iterrows():
    url = row["Links"]
    driver.get(url)

    try:
        title = driver.find_element(By.CSS_SELECTOR, "body > div.site-wrapper > h1").text
    except NoSuchElementException:
        title = "Not available"

    try:
        price_raw = driver.find_element(By.CSS_SELECTOR, "div.product-price-group > div.price-wrapper > div > div").text
        price = "".join(re.findall(r"\d+", price_raw))
    except NoSuchElementException:
        price = "Not available"

    try:
        availability = driver.find_element(By.CSS_SELECTOR, "div.product-price-group > div.product-stats > ul > "
                                                            "li.product-stock.in-stock > span").text
    except NoSuchElementException:
        availability = "Not available"

    try:
        producer_element = driver.find_element(By.CSS_SELECTOR, "div.product-price-group > div.product-stats > div > a")
        producer_page = producer_element.get_attribute("href")
        driver.get(producer_page)
        producer = driver.find_element(By.CSS_SELECTOR, "body > div.site-wrapper > h1").text
    except (NoSuchElementException, WebDriverException):
        producer = "Not available"

    csv_writer.writerow([title, price, availability, producer])
    print(f"Title: {title}, Price: {price}, Availability: {availability}, Producer: {producer}")

csv_file.close()
driver.quit()
