import requests
import time
from models.brig_member import BrigMember
from models.brigade import Brigade


def request_rankings_data(brigade):

    rankings_data = {
        "members": [],
        "brigs": [],
        "full": [],
    }
    members_urls = [
        "https://oldschoolrivals.com/action/ranking/players/Fame/b",
        "https://oldschoolrivals.com/action/ranking/players/Fame/i",
        "https://oldschoolrivals.com/action/ranking/players/Fame/a",
        "https://oldschoolrivals.com/action/ranking/players/Fame/m",
    ]

    brig_url = "https://oldschoolrivals.com/action/ranking/brig/MonthlyFame"

    total_start = time.perf_counter()

    for url in members_urls:
        request_start = time.perf_counter()
        response = requests.get(
            url,
            params={"limit": 10},
            timeout=10
        )
        response.raise_for_status()
        request_time = time.perf_counter() - request_start
        print(f"  → {url.split('/')[-1]} request completed in {request_time:.2f}s")

        brig_members = [BrigMember(member["Name"], member["Level"], member["Gear"], member["Fame"]) for member in response.json()["ranking"]["players"] if member["Guild"] == brigade]
        rankings_data["members"].extend(brig_members)

    brig_start = time.perf_counter()
    brig_response = requests.get(
        brig_url,
        params={"limit": 10},
        timeout=10
    )
    brig_response.raise_for_status()
    brig_time = time.perf_counter() - brig_start
    print(f"  → brig request completed in {brig_time:.2f}s")

    # instantiate all brigades as Brigade objects
    all_brigs = [Brigade(brig["Name"], brig["MonthlyFame"], brig.get("Nation", 0), brig.get("TotalFame", 0)) for brig in brig_response.json()["ranking"]["brig"]]
    rankings_data["brigs"] = all_brigs[:10]
    rankings_data["full"] = all_brigs

    total_time = time.perf_counter() - total_start
    print(f"Total API call time: {total_time:.2f}s")

    return rankings_data