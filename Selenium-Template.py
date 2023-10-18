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


results = []

for page_num in range(array_pages[0], array_pages[-1] + 1):
    # Tạo URL cho mỗi trang
    url = (
        f"https://www.hkfa.com/en/competitions/fixtures?year=2023-2024&page={page_num}"
    )

    driver.get(url)

    match_items = driver.find_elements(By.CSS_SELECTOR, ".container div.mb-5")

    for match_item in match_items:
        match_info_parts = match_item.text.strip().split("\n")
        date_name= driver.find_element(By.CSS_SELECTOR, ".container div.mb-5 div.strong-title")
        date_name = date_name.text

        match_details = driver.find_elements(
            By.XPATH, f'//div[@class="mb-5"]/div[text()="{date_name}"]/parent::div/div[@class="items"]'
        )

        for match_detail in match_details:
            match = match_detail.text.strip().split("\n")


            if match[0].strip() == "DELAY":
                match_obj = {
                    "date": date_name,
                    "home_score": match[0].strip(),
                    "away_score": match[0].strip(),
                    "match_time": match[1].strip(),
                    "home_team": match[2].strip(),
                    "away_team": match[3].strip(),
                }
            elif not match[0].isnumeric():
                match_obj = {
                    "date": date_name,
                    "home_score": "",
                    "away_score": "",
                    "match_time": match[0].strip(),
                    "home_team": match[1].strip(),
                    "away_team": match[2].strip(),
                }
            else:
                match_obj = {
                    "date": date_name,
                    "home_score": match[0].strip(),
                    "away_score": match[1].strip(),
                    "match_time": match[2].strip(),
                    "home_team": match[3].strip(),
                    "away_team": match[4].strip(),
                }  

            keywords = ["Park", "Training Center", "Playground", "Stadium", "Ground"]
            for i in range(4, len(match)):
                contains_keyword = any(
                    keyword in match[i] for keyword in keywords
                )
                if contains_keyword:
                    match_obj["venue"] = match[i].strip()
                    break

            keywords = ["Cup", "League", "Division"]
            for i in range(4, len(match)):
                contains_keyword = any(
                    keyword in match[i] for keyword in keywords
                )
                if contains_keyword:
                    match_obj["tournament"] = match[i].strip()
                    break

            keywords = ["$", "T.B.C"]
            if any(keyword in match[-1].strip() for keyword in keywords):
                match_obj["ticket"] = match[-1].strip()

            results.append(match_obj)

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
