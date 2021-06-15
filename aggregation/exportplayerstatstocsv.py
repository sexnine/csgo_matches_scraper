import pickle
from csgoscraper.csgodataclasses.csgodataclasses import *
import yaml
import csv


config = None

def load_config():
    print("Loading config")
    with open("../config.yml", "r") as f:
        global config
        config = yaml.safe_load(f)
    print("Loaded config!")


def write_csv(data, file_name):
    with open("../csgodist/" + file_name, "w", encoding="utf8", newline="") as f:
        fc = csv.DictWriter(f, fieldnames=data[0].keys())
        fc.writeheader()
        fc.writerows(data)


def get_my_data(matches):
    my_data = []

    for match in matches:
        # players = [team.players for team in match.teams]
        # print(players)

        found = False
        for team in match.teams:
            if found:
                break
            for player in team.players:
                print(player)
                if found:
                    break
                if player.name == config.get("my_username"):
                    print("a")
                    print(vars(player.stats))
                    my_data.append(vars(player.stats))
                    found = True

    return my_data


def main():
    load_config()

    with open("../csgodist/comp.pkl", "rb") as f:
        competitive_matches = pickle.load(f)

    with open("../csgodist/wingman.pkl", "rb") as f:
        wingman_matches = pickle.load(f)

    with open("../csgodist/scrim.pkl", "rb") as f:
        scrimmage_matches = pickle.load(f)

    write_csv(get_my_data(competitive_matches), "comp.csv")
    write_csv(get_my_data(wingman_matches), "wingman.csv")
    write_csv(get_my_data(scrimmage_matches), "scrim.csv")


if __name__ == "__main__":
    main()
