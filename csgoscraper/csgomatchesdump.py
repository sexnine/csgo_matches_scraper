# from dataclasses import dataclass
# from typing import List
import yaml
import pickle
from selenium import webdriver
import time
import math
from datetime import timedelta
from csgodataclasses.csgodataclasses import *
from selenium.webdriver.remote.webelement import WebElement

config = None
competitive_matches = []
scrimmage_matches = []
wingman_matches = []


def convert_to_seconds(string: str) -> int:
    x = time.strptime(string, "%M:%S")
    return int(timedelta(minutes=x.tm_min, seconds=x.tm_sec).total_seconds())


def get_player_info_from_element(element: WebElement) -> Player:
    data = element.find_elements_by_tag_name("td")
    player_profile_el = element.find_element_by_class_name("linkTitle")

    mvps = data[5].text
    if mvps == " ":
        mvps_total = 0
    elif mvps == "★":
        mvps_total = 1
    else:
        mvps_total = int(mvps.replace("★", ""))

    return Player(
        name=player_profile_el.text,
        link=player_profile_el.get_attribute("href"),
        stats=PlayerStats(
            ping=int(data[1].text) if data[1] != " " else 0,
            kills=int(data[2].text) if data[2] != " " else 0,
            assists=int(data[3].text) if data[3] != " " else 0,
            deaths=int(data[4].text) if data[4] != " " else 0,
            mvps=mvps_total,
            headshot_rate=int(data[6].text.replace("%", "")) if data[6].text != " " else 0,
            score=int(data[7].text) if data[7] != " " else 0,
        )
    )


def process_scoreboard_from_elements(elements, score_element: int, team_one_elements: list, team_two_elements: list):
    team_one_score = None
    team_one_players = []
    team_two_score = None
    team_two_players = []

    i = 0
    for row in elements:
        if i == 0:
            i += 1
            continue
        elif i == score_element:
            score = row.find_element_by_tag_name("td").text
            score_split = score.split(" ")
            team_one_score = score_split[0]
            team_two_score = score_split[2]
        elif i in team_one_elements:
            team_one_players.append(get_player_info_from_element(row))
        elif i in team_two_elements:
            team_two_players.append(get_player_info_from_element(row))
        i += 1

    return [
        Team(
            players=team_one_players,
            score=team_one_score
        ),
        Team(
            players=team_two_players,
            score=team_two_score
        )
    ]


def get_comp_teams_info_from_elements(elements):
    return process_scoreboard_from_elements(elements=elements, score_element=6, team_one_elements=[1, 2, 3, 4, 5], team_two_elements=[7, 8, 9, 10, 11])


def get_wingman_teams_info_from_elements(elements):
    return process_scoreboard_from_elements(elements=elements, score_element=3, team_one_elements=[1, 2], team_two_elements=[4, 5])


def get_match_info_from_element(element: WebElement, match_type: str) -> Match:
    match_info_element = element.find_element_by_class_name("csgo_scoreboard_inner_left")
    scoreboard_element = element.find_element_by_class_name("csgo_scoreboard_inner_right")

    match_info_data = match_info_element.find_elements_by_tag_name("td")

    get_teams_info_func = get_comp_teams_info_from_elements if match_type != "wingman" else get_wingman_teams_info_from_elements

    teams = get_teams_info_func(scoreboard_element.find_elements_by_tag_name("tr"))

    return Match(
        name=match_info_data[0].text,
        time=match_info_data[1].text,
        ranked=match_info_data[2].text.split("Ranked: ")[1].startswith("Yes") if match_type != "scrimmage" else False,
        wait_time=convert_to_seconds(match_info_data[3].text.split("Wait Time: ")[1]) if match_type != "scrimmage" else convert_to_seconds(match_info_data[2].text.split("Wait Time: ")[1]),
        duration=convert_to_seconds(match_info_data[4].text.split("Match Duration: ")[1]) if match_type != "scrimmage" else convert_to_seconds(match_info_data[3].text.split("Match Duration: ")[1]),
        teams=teams
    )


def go_to_page_and_compile_data(driver, link: str, match_type: str):
    print(f"Starting to scrape {match_type} matches...")
    res = []

    driver.get(link)

    while True:
        try:
            if driver.find_element_by_id("load_more_button").get_attribute("style") != "display: none;":
                print("Clicking button to load more matches")
                driver.find_element_by_id("load_more_button").click()
                time.sleep(2)
            else:
                print("No more matches to load")
                break
        except:
            break

    match_info_elements = driver.find_elements_by_css_selector("table.csgo_scoreboard_root > tbody > tr")
    match_info_elements.pop(0)

    print(f"Found {str(len(match_info_elements))} {match_type} matches")

    i = 1
    for element in match_info_elements:
        print(f"Processing {match_type} match info {str(i)}/{str(len(match_info_elements))}")
        res.append(get_match_info_from_element(element, match_type))
        i += 1

    print(f"Finished scraping all {match_type} matches!")

    return res


def load_config():
    print("Loading config")
    with open("../config.yml", "r") as f:
        global config
        config = yaml.safe_load(f)
    print("Loaded config!")


def main():
    global competitive_matches, scrimmage_matches, wingman_matches

    start_time = time.time()
    load_config()
    driver = webdriver.Chrome(config.get("driver_file_path", "chromedriver.exe"))

    print("Loading home page")
    driver.get("https://steamcommunity.com")
    print("Adding cookies and refreshing page")
    try:
        cookies = pickle.load(open("../data/cookies.pkl", "rb"))
    except FileNotFoundError:
        print("Couldn't find cookies, was it deleted?  Run login.py to login before running this file.")
        driver.quit()
        exit(0)

    for cookie in cookies:
        driver.add_cookie(cookie)
    driver.get("https://steamcommunity.com")

    print("Checking if logged in...")
    try:
        driver.get(driver.find_elements_by_xpath("//*[contains(text(), 'View profile')]")[0].get_attribute("href") + "gcpd/730/")
    except:
        print("Couldn't navigate to your game data...  Are you logged in?  Make sure to log in using login.py")
        driver.quit()
        exit(0)

    base_link = driver.current_url

    try:
        competitive_matches = go_to_page_and_compile_data(driver, base_link + "?tab=matchhistorycompetitive", "competitive")
        wingman_matches = go_to_page_and_compile_data(driver, base_link + "?tab=matchhistorywingman", "wingman")
        scrimmage_matches = go_to_page_and_compile_data(driver, base_link + "?tab=matchhistoryscrimmage", "scrimmage")
    except Exception as e:
        print(e)

    pickle.dump(competitive_matches, open("../csgodist/comp.pkl", "wb"))
    pickle.dump(wingman_matches, open("../csgodist/wingman.pkl", "wb"))
    pickle.dump(scrimmage_matches, open("../csgodist/scrim.pkl", "wb"))

    byebye = f"""

Done! Completed in {math.floor(time.time() - start_time)}s
    """

    print(byebye)


if __name__ == "__main__":
    main()
