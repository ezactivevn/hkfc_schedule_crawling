import datetime
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options  # Import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import re

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

# get current season
# if current month >= 7 then current season is current year - current year + 1
# else current season is current year - current year - 1
# example: current month is 8 then current season is 2024-2025
# example: current month is 6 then current season is 2023-2024
currentYear = datetime.datetime.now().year
currentMonth = datetime.datetime.now().month
if currentMonth >= 7:
    current_season = f"{currentYear}-{currentYear+1}"
else:
    current_season = f"{currentYear-1}-{currentYear}"

print(f"Current season: {current_season}")

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


# Function to extract group information from team name or tournament name
# Example: HKFC U18, HKFC U18 Girls, Lucky Mile U18
def extract_group(team_name, tournament_name):
    group_match = re.search(r"\b[Uu]\d{2}\b", team_name)
    if group_match:
        return group_match.group()
    group_match = re.search(r"\b[Uu]\d{2}\b", tournament_name)
    if group_match:
        return group_match.group()
    return None


for page_num in range(array_pages[0], array_pages[-1] + 1):
    # Tạo URL cho mỗi trang
    url = f"https://www.hkfa.com/en/competitions/fixtures?year={current_season}&page={page_num}"

    driver.get(url)

    match_items = driver.find_elements(By.CSS_SELECTOR, ".container div.mb-5")

    for match_item in match_items:
        date_of_match = match_item.find_element(
            By.CSS_SELECTOR, "div.strong-title"
        ).text

        break_out_flag = False

        matchs_by_date = match_item.find_element(By.CSS_SELECTOR, "div.items")

        for match in matchs_by_date.find_elements(
            By.CSS_SELECTOR, "div.single-fixture"
        ):

            # We need GA (grassroot app), Premier Youth League,
            # Women league, Jockey Club League
            # and need for both team: Hong Kong Football Club and Lucky Mile
            tournament_required = [
                "BOC Life Hong Kong Premier League",
                "Jockey Club Women's Football League",
                "Jockey Club Futsal League",
                "2nd Division",
                "JC Sapling Cup",
                "FA Cup",
            ]
            team_required = ["HKFC", "Lucky Mile", "Hong Kong Football Club"]

            data = {
                "date": date_of_match,
                "home_team": "",
                "away_team": "",
                "match_time": "",
                "venue": "",
                "home_score": "",
                "away_score": "",
            }

            try:

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
            except Exception:
                break_out_flag = True
                break

            home_team_stripped = data["home_team"].strip()
            away_team_stripped = data["away_team"].strip()
            tournament_stripped = data["tournament"].strip()

            group = (
                extract_group(home_team_stripped, tournament_stripped)
                and extract_group(home_team_stripped, tournament_stripped)
                or extract_group(away_team_stripped, tournament_stripped)
            )

            if group:
                data["group"] = group
            else:
                data["group"] = ""

            if not any(
                required in tournament_stripped for required in tournament_required
            ):
                if any(required in home_team_stripped for required in team_required):
                    results.append(data)
                elif any(required in away_team_stripped for required in team_required):
                    results.append(data)
                else:
                    print(
                        f"Skipped match {home_team_stripped} vs {away_team_stripped} [{tournament_stripped}]"
                    )
            else:
                print(
                    f"Skipped tournament [{tournament_stripped}]"
                )

        if break_out_flag:
            break
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
