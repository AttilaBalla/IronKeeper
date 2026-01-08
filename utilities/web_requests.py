import requests
from features.brig_member import BrigMember


def request_rankings_data():

    rankings_data = {
        "members": [],
        "brigs": []
    }
    members_urls = [
        "https://oldschoolrivals.com/action/ranking/players/Fame/b",
        "https://oldschoolrivals.com/action/ranking/players/Fame/i",
        "https://oldschoolrivals.com/action/ranking/players/Fame/a",
        "https://oldschoolrivals.com/action/ranking/players/Fame/m",
    ]

    brig_url = "https://oldschoolrivals.com/action/ranking/brig/TotalFame"

    for url in members_urls:
        response = requests.get(
            url,
            params={"limit": 10},
            timeout=10
        )
        response.raise_for_status()
        # might as well filter out IT members here since we don't care about the rest
        brig_members = [BrigMember(member["Name"], member["Level"], member["Gear"], member["Fame"]) for member in response.json()["ranking"]["players"] if member["Guild"] == "IronTempest"]
        rankings_data["members"].extend(brig_members)

    brig_response = requests.get(
        brig_url,
        params={"limit": 10},
        timeout=10
    )
    # output the first 10 brigades
    rankings_data["brigs"] = brig_response.json()["ranking"]["brig"][:10]

    return rankings_data