import signal
import sys
import re
import csv
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
import os
from datetime import datetime


def sigterm_handler(signum, frame):
    print("SIGTERM received, stopping script...")
    driver.quit()
    sys.exit(0)


signal.signal(signal.SIGTERM, sigterm_handler)

script_dir = os.path.dirname(os.path.abspath(__file__))

output_dir = os.path.join(script_dir, "scraped_results")

os.makedirs(output_dir, exist_ok=True)

file_path = os.path.join(script_dir, "links_to_download.xlsx")
df = pd.read_excel(file_path)

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
csv_file_name = f"result{timestamp}.csv"
csv_file_path = os.path.join(output_dir, csv_file_name)

with open(csv_file_path, "w", newline="", encoding="utf-8") as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["Title", "Price", "Availability", "Producer"])

    service = ChromeService()
    driver = webdriver.Chrome(service=service)

    for index, row in df.iterrows():
        url = row["Links"]
        driver.get(url)

        try:
            title = driver.find_element(
                By.CSS_SELECTOR, "body > div.site-wrapper > h1"
            ).text
        except NoSuchElementException:
            title = "Not available"

        try:
            price_raw = driver.find_element(
                By.CSS_SELECTOR,
                "div.product-price-group > div.price-wrapper > div > div",
            ).text
            price = "".join(re.findall(r"\d+", price_raw))
        except NoSuchElementException:
            price = "Not available"

        try:
            availability = driver.find_element(
                By.CSS_SELECTOR,
                "div.product-price-group > div.product-stats > ul > li.product-stock.in-stock > span",
            ).text
        except NoSuchElementException:
            availability = "Not available"

        try:
            producer_element = driver.find_element(
                By.CSS_SELECTOR, "div.product-price-group > div.product-stats > div > a"
            )
            producer_page = producer_element.get_attribute("href")
            driver.get(producer_page)
            producer = driver.find_element(
                By.CSS_SELECTOR, "body > div.site-wrapper > h1"
            ).text
        except (NoSuchElementException, WebDriverException):
            producer = "Not available"

        csv_writer.writerow([title, price, availability, producer])
        print(
            f"Title: {title}, Price: {price}, Availability: {availability}, Producer: {producer}"
        )

    driver.quit()
