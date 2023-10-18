import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options  # Import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

array_dates = []
# today to next 10 days
import datetime

# Get today's date
today = datetime.date.today()

# Get the dates for the next 10 days
dates = [today + datetime.timedelta(days=i) for i in range(10)]




for date in dates:
    # Tạo URL cho mỗi trang
    url = (
        f"https://www.hkfa.com/en/competitions/fixtures?year=2023-2024&page=1&date={date.strftime('%Y-%m-%d')}"
    )

    driver.get(url)

    match_items = driver.find_elements(By.CSS_SELECTOR, ".container div.mb-5")

    for match_item in match_items:
        match_info_parts = match_item.text.strip().split("\n")
        date = match_info_parts[0].strip()

        match_details = driver.find_elements(
            By.CSS_SELECTOR, ".container div.mb-5 div.single-fixture"
        )
        for match_detail in match_details:
            match_detail = match_detail.text.strip().split("\n")

            if match_detail[0].strip() == "DELAY":
                match_obj = {
                    "date": match_info_parts[0].strip(),
                    "home_score": match_detail[0].strip(),
                    "away_score": match_detail[0].strip(),
                    "match_time": match_detail[1].strip(),
                    "home_team": match_detail[2].strip(),
                    "away_team": match_detail[3].strip(),
                }
            elif not match_detail[0].isnumeric():
                match_obj = {
                    "date": match_info_parts[0].strip(),
                    "home_score": "",
                    "away_score": "",
                    "match_time": match_detail[0].strip(),
                    "home_team": match_detail[1].strip(),
                    "away_team": match_detail[2].strip(),
                }
            else:
                match_obj = {
                    "date": match_info_parts[0].strip(),
                    "home_score": match_detail[0].strip(),
                    "away_score": match_detail[1].strip(),
                    "match_time": match_detail[2].strip(),
                    "home_team": match_detail[3].strip(),
                    "away_team": match_detail[4].strip(),
                }
            

            keywords = ["Park", "Training Center", "Playground", "Stadium", "Ground"]
            for i in range(4, len(match_detail)):

                contains_keyword = any(keyword in match_detail[i] for keyword in keywords)
                if contains_keyword:
                    match_obj["venue"] = match_detail[i].strip()
                    break

            keywords = ["Cup", "League", "Division"]
            for i in range(4,len(match_detail)):

                contains_keyword = any(keyword in match_detail[i] for keyword in keywords)
                if contains_keyword:
                    match_obj["tournament"] = match_detail[i].strip()
                    break
                

            keywords = ["$", "T.B.C"]
            if any(keyword in match_detail[-1].strip() for keyword in keywords):
                match_obj["ticket"] = match_detail[-1].strip()


            if date not in matchs_by_date["listMatchs"]:
                matchs_by_date["listMatchs"][date] = []

            matchs_by_date["listMatchs"][date].append(match_obj)

    print(f"Lấy dữ liệu cho ngày {date}")

# Đóng trình duyệt
driver.quit()

# Lưu dữ liệu vào file JSON
output_file = "match_data.json"

# Empty JSON file
with open(output_file, "w") as json_file:
    json_file.write("{}")

with open(output_file, "w") as json_file:
    json.dump(matchs_by_date, json_file, indent=4)

print(f"Dữ liệu đã được lưu vào file: {output_file}")
