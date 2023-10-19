import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options  # Import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

from bs4 import BeautifulSoup

# Create ChromeOptions and set it to run in headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode

# Khởi tạo trình duyệt (ví dụ: Google Chrome) in headless mode
driver = webdriver.Chrome(options=chrome_options)

matchs_by_date = {"listMatchs": {}}


numberofpage = []

url = "https://www.hkfa.com/en/competitions/fixtures"
driver.get(url)

numberofpage = driver.find_elements(By.CSS_SELECTOR, "ul.el-pager li.number")
soup = BeautifulSoup(driver.page_source, "html.parser")

array_pages = []
for number in numberofpage:
    # lấy không trùng
    number = int(number.text)
    if number not in array_pages:
        # parse to number
        array_pages.append(number)


results = []

for page_num in range(array_pages[0], array_pages[-1] + 1):
    # Tạo URL cho mỗi trang
    url = (
        f"https://www.hkfa.com/en/competitions/fixtures?year=2023-2024&page={page_num}"
    )

    driver.get(url)

    match_items = driver.find_elements(By.CSS_SELECTOR, ".container div.mb-5")

    for match_item in match_items:
        date_of_match = match_item.find_element(
            By.CSS_SELECTOR, "div.strong-title"
        ).text
        
        matchs_by_date = match_item.find_element(
            By.CSS_SELECTOR, "div.items"
        )

        for match in matchs_by_date.find_elements(By.CSS_SELECTOR, "div.single-fixture"):

            # We need GA (grassroot app), Premier Youth League,  
            # Women league, Jockey Club League 
            # and need for both team: Hong Kong Football Club and Lucky Mile
            tournament_required = ["Premier", "Youth", "Women's Football League", "Jockey Club", "Hong Kong"]

            # if not in tournament_required continue

            try:
                tournament_element = match.find_element(By.CSS_SELECTOR, "div.league-wrapper")
                tournament = tournament_element.text.strip()

                # Check if tournament contains any of the required strings
                if not any(required in tournament for required in tournament_required):
                    print(f"Skip {tournament}")
                    continue

            except NoSuchElementException:
                pass


            data = {
                "date": date_of_match,
                "home_team": "",
                "away_team": "",
                "match_time": "",
                "venue": "",
                "home_score": "",
                "away_score": ""
            }

            try:
                data["home_team"] = match.find_element(
                    By.CSS_SELECTOR, "div.home-team"
                ).text
            except NoSuchElementException:
                pass

            try:
                data["away_team"] = match.find_element(
                    By.CSS_SELECTOR, "div.guest-team"
                ).text
            except NoSuchElementException:
                pass

            try:
                data["match_time"] = match.find_element(
                    By.CSS_SELECTOR, "div.clock"
                ).text
            except NoSuchElementException:
                pass

            try:
                data["venue"] = match.find_element(
                    By.CSS_SELECTOR, "div.venue-wrapper"
                ).text
            except NoSuchElementException:
                pass

            try:
                data["tournament"] = match.find_element(
                    By.CSS_SELECTOR, "div.league-wrapper"
                ).text
            except NoSuchElementException:
                pass

            try:
                data["home_score"] = match.find_element(
                    By.CSS_SELECTOR, "div.score:nth-child(1)"
                ).text
            except NoSuchElementException:
                pass

            try:
                data["away_score"] = match.find_element(
                    By.CSS_SELECTOR, "div.score:nth-child(2)"
                ).text
            except NoSuchElementException:
                pass

            results.append(data)
                

            




        
       
    print(f"Lấy dữ liệu từ trang {page_num}")

# Đóng trình duyệt
driver.quit()

# Lưu dữ liệu vào file JSON
output_file = "match_data.json"

# Empty JSON file
with open(output_file, "w") as json_file:
    json_file.write("{}")

with open(output_file, "w") as json_file:
    json.dump(results, json_file, indent=4)

print(f"Dữ liệu đã được lưu vào file: {output_file}")
