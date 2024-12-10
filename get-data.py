import requests
import pandas as pd
import time
from dotenv import load_dotenv
import os

load_dotenv()

# ===================================
# CONFIGURATION
# ===================================
API_KEY = os.getenv('RIOT_API_KEY')
REGION = "na1"
AMERICAS_REGION = "americas"
TIER = "GOLD"
DIVISION = "I"
QUEUE = "RANKED_SOLO_5x5"
REQUEST_DELAY = 1
MAX_SUMMONERS = 2000
MATCHES_PER_PLAYER = 20
OUTPUT_SUMMONERS_CSV = "output_files/gold_summoners.csv"
OUTPUT_SUMMONERS_PUUID_CSV = "output_files/gold_summoners_with_puuid.csv"
OUTPUT_MATCHIDS_CSV = "output_files/gold_matchids.csv"
OUTPUT_FINAL_CSV = "output_files/gold_matchdata.csv"

# ===================================
# HELPER FUNCTIONS
# ===================================
def riot_get(url):
    """A helper function to handle GET requests with Riot API rate limit retries."""
    while True:
        resp = requests.get(url)
        if resp.status_code == 200:
            return resp
        elif resp.status_code == 429:
            # Rate limit exceeded, wait and retry
            print("429 rate limit hit, waiting 10 seconds...")
            time.sleep(10)
        else:
            # Other errors: print and try waiting a bit
            print(f"Error {resp.status_code}: {resp.text}")
            time.sleep(10)

def get_gold_summoners(api_key, region, queue, tier, division, max_pages=1):
    """
    Get a list of summoners in the specified tier/division.
    This uses the League-V4 entries endpoint.
    Adjust max_pages to fetch more summoners.
    """
    summoner_entries = []
    for page in range(1, max_pages+1):
        url = f"https://{region}.api.riotgames.com/lol/league/v4/entries/{queue}/{tier}/{division}?page={page}&api_key={api_key}"
        resp = riot_get(url)
        data = resp.json()
        if not data:
            break
        summoner_entries.extend(data)
        # Sleep to respect rate limits
        time.sleep(REQUEST_DELAY)
    return pd.DataFrame(summoner_entries)

def get_summoner_info(summoner_id, api_key, region):
    """
    Get summoner info (including puuid) from encryptedSummonerId using Summoner-V4.
    """
    url = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/{summoner_id}?api_key={api_key}"
    resp = riot_get(url)
    return resp.json()

def get_match_ids_by_puuid(puuid, api_key, region, start=0, count=20, queue=420):
    """
    Get recent match IDs for a given puuid from Match-V5.
    """
    url = (f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
           f"?queue={queue}&type=ranked&start={start}&count={count}&api_key={api_key}")
    resp = riot_get(url)
    return resp.json()

def get_match_info(match_id, api_key, region):
    """
    Get detailed match info for a given match_id from Match-V5.
    """
    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={api_key}"
    resp = riot_get(url)
    return resp.json()

# ===================================
# DATA COLLECTION WORKFLOW
# ===================================

# Step 1: Get a set of Gold-tier summoners
print("Fetching Gold summoners...")
summoner_df = get_gold_summoners(API_KEY, REGION, QUEUE, TIER, DIVISION, max_pages=5)
if summoner_df.empty:
    raise ValueError("No summoners found. Check your API key or parameters.")
summoner_df = summoner_df.head(MAX_SUMMONERS)
print(f"Found {summoner_df.shape[0]} summoners.")
summoner_df.to_csv(OUTPUT_SUMMONERS_CSV, index=False)

# Step 2: Get PUUIDs for each summoner
print("Fetching PUUIDs for each summoner...")
summoner_infos = []
for i, row in summoner_df.iterrows():
    summoner_id = row['summonerId']
    info = get_summoner_info(summoner_id, API_KEY, REGION)
    summoner_infos.append(info)
    time.sleep(REQUEST_DELAY)

summoner_info_df = pd.DataFrame(summoner_infos)
merged_df = summoner_df.merge(summoner_info_df, left_on='summonerId', right_on='id')
print("Merging summoner data with PUUID...")
merged_df.to_csv(OUTPUT_SUMMONERS_PUUID_CSV, index=False)

# Step 3: Get match IDs for each summoner’s PUUID
print("Fetching match IDs for each summoner...")
matchids_list = []
for i, row in merged_df.iterrows():
    puuid = row['puuid']
    match_ids = get_match_ids_by_puuid(puuid, API_KEY, AMERICAS_REGION, count=MATCHES_PER_PLAYER)
    for mid in match_ids:
        matchids_list.append(mid)
    time.sleep(REQUEST_DELAY)

matchids_df = pd.DataFrame(list(set(matchids_list)), columns=['matchid'])  # Unique match IDs
print(f"Collected {matchids_df.shape[0]} unique match IDs.")
matchids_df.to_csv(OUTPUT_MATCHIDS_CSV, index=False)

# Step 4: Get detailed match info and extract features
print("Fetching detailed match info...")
match_data_list = []
for i, row in matchids_df.iterrows():
    match_id = row['matchid']
    match_data = get_match_info(match_id, API_KEY, AMERICAS_REGION)
    # Extract relevant info:
    # We want champion picks and outcome. The info key: match_data['info']
    # 'participants' is a list of 10 players. 'teams' gives who won.
    info = match_data.get('info', {})
    teams = info.get('teams', [])
    participants = info.get('participants', [])

    # Determine who won (True/False) for the blue team (teamId=100)
    # Normally, teamId=100 is "Blue", teamId=200 is "Red".
    blue_win = None
    red_win = None
    for t in teams:
        if t['teamId'] == 100:
            blue_win = t['win']
        elif t['teamId'] == 200:
            red_win = t['win']

    # Extract champion picks
    # Participants are listed in a fixed order. Typically first 5 are team 100, next 5 are team 200
    # Just get their champion names or IDs
    blue_team_champs = [p['championName'] for p in participants if p['teamId'] == 100]
    red_team_champs = [p['championName'] for p in participants if p['teamId'] == 200]

    match_record = {
        'match_id': match_id,
        'blue_team_champs': blue_team_champs,
        'red_team_champs': red_team_champs,
        'blue_win': blue_win
    }

    match_data_list.append(match_record)
    print(f'{i} - added entry {match_record}')
    time.sleep(REQUEST_DELAY)

final_df = pd.DataFrame(match_data_list)
# Convert champ lists to csv
final_df['blue_team_champs'] = final_df['blue_team_champs'].apply(lambda x: ",".join(x))
final_df['red_team_champs'] = final_df['red_team_champs'].apply(lambda x: ",".join(x))

# Step 5: Save final dataset
final_df.to_csv(OUTPUT_FINAL_CSV, index=False)
print("Data collection complete. Final dataset saved to:", OUTPUT_FINAL_CSV)
