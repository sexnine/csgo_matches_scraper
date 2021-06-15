import pickle
from csgoscraper.csgodataclasses.csgodataclasses import *

def calculate_total_time(matches: list, match_type: str) -> int:
    total_time = 0
    for match in matches:
        total_time += match.duration

    minutes, seconds = divmod(total_time, 60)
    hours, minutes = divmod(minutes, 60)
    print(f"Total time spent playing {match_type} is {str(hours) + ' hours ' if hours else ''}{str(minutes) + ' minutes ' if minutes else ''}{str(seconds) + ' seconds' if seconds else ''}")

    return total_time


def main():

    with open("../csgodist/comp.pkl", "rb") as f:
        competitive_matches = pickle.load(f)

    with open("../csgodist/wingman.pkl", "rb") as f:
        wingman_matches = pickle.load(f)

    with open("../csgodist/scrim.pkl", "rb") as f:
        scrimmage_matches = pickle.load(f)

    calculate_total_time(competitive_matches, "competitive")
    calculate_total_time(wingman_matches, "wingman")
    calculate_total_time(scrimmage_matches, "scrimmage")


if __name__ == "__main__":
    main()