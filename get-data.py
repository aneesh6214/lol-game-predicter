import requests
import pandas as pd
import time
from dotenv import load_dotenv
import os
from collections import deque
from datetime import datetime

load_dotenv()

# ===================================
# CONFIGURATION
# ===================================
# API_KEY = os.getenv('RIOT_API_KEY_2')
# print("Loaded Key, ", API_KEY)

REGION = "na1"
AMERICAS_REGION = "americas"
TIER = "GOLD"
DIVISION = "I"
QUEUE = "RANKED_SOLO_5x5"
REQUEST_DELAY = 1.2
MAX_SUMMONERS = 4000
MATCHES_PER_PLAYER = 30
OUTPUT_SUMMONERS_CSV = "output_files/gold_summoners.csv"
OUTPUT_SUMMONERS_PUUID_CSV = "output_files/gold_summoners_with_puuid.csv"
OUTPUT_MATCHIDS_CSV = "output_files/gold_matchids.csv"
OUTPUT_FINAL_CSV = "output_files/gold_matchdata.csv"
request_times = deque()

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
        elif resp.status_code == 404:
            # Match not found, return response to handle in main loop
            return resp
        else:
            # Other errors: print and try waiting a bit
            print(f"Error {resp.status_code}: {resp.text}")
            time.sleep(10)

def get_gold_summoners(api_key, region, queue, tier, division, max_pages=1):
    """
    Get a list of summoners in the specified tier/division.
    """
    summoner_entries = []
    for page in range(1, max_pages+1):
        url = f"https://{region}.api.riotgames.com/lol/league/v4/entries/{queue}/{tier}/{division}?page={page}&api_key={api_key}"
        resp = riot_get(url)
        data = resp.json()
        if not data:
            break
        summoner_entries.extend(data)
        time.sleep(REQUEST_DELAY)
    return pd.DataFrame(summoner_entries)

def get_summoner_info(summoner_id, api_key, region):
    """
    Get summoner info (including puuid).
    """
    url = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/{summoner_id}?api_key={api_key}"
    resp = riot_get(url)
    return resp.json()

def get_match_ids_by_puuid(puuid, api_key, region, start=0, count=20, queue=420):
    """
    Get recent match IDs for a given puuid.
    """
    url = (f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
           f"?queue={queue}&type=ranked&start={start}&count={count}&api_key={api_key}")
    resp = riot_get(url)
    return resp.json()

def get_match_info(match_id, api_key, region):
    """
    Get detailed match info.
    """
    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={api_key}"
    resp = riot_get(url)
    return resp

def initialize_csv(file_path, headers):
    """Initialize the CSV file with headers if it doesn't exist."""
    if not os.path.exists(file_path):
        df = pd.DataFrame(columns=headers)
        df.to_csv(file_path, index=False)
        print(f"Initialized {file_path} with headers.")

# ===================================
# DATA COLLECTION WORKFLOW
# ===================================

start_time = time.time()

# # Step 1: Get a set of Gold-tier summoners
# print("Fetching Gold summoners...")
# summoner_df = get_gold_summoners(API_KEY, REGION, QUEUE, TIER, DIVISION, max_pages=20)
# if summoner_df.empty:
#     raise ValueError("No summoners found. Check your API key or parameters.")
# summoner_df = summoner_df.head(MAX_SUMMONERS)
# print(f"Found {summoner_df.shape[0]} summoners.")
# summoner_df.to_csv(OUTPUT_SUMMONERS_CSV, index=False)

# # Step 2: Get PUUIDs for each summoner
# print("Fetching PUUIDs for each summoner...")
# summoner_infos = []
# total_summoners = summoner_df.shape[0]
# for i, row in summoner_df.iterrows():
#     summoner_id = row['summonerId']
#     info = get_summoner_info(summoner_id, API_KEY, REGION)
#     summoner_infos.append(info)
    
#     # Progress indicator every 100 summoners
#     if (i + 1) % 100 == 0 or (i + 1) == total_summoners:
#         elapsed = time.time() - start_time
#         print(f"Processed {i + 1}/{total_summoners} summoners, elapsed time: {elapsed:.2f} seconds")
    
#     time.sleep(REQUEST_DELAY)

# summoner_info_df = pd.DataFrame(summoner_infos)
# merged_df = summoner_df.merge(summoner_info_df, left_on='summonerId', right_on='id')
# print("Merging summoner data with PUUID...")
# merged_df.to_csv(OUTPUT_SUMMONERS_PUUID_CSV, index=False)
API_KEY = 'RGAPI-77eabccf-237f-4093-b408-25aadb9bd000'

# # Step 3: Get match IDs for each summoner’s PUUID
# merged_df = pd.read_csv(OUTPUT_SUMMONERS_PUUID_CSV)
# print("Fetching match IDs for each summoner...")

# # Read existing match IDs if the CSV exists
# if os.path.exists(OUTPUT_MATCHIDS_CSV):
#     existing_matchids_df = pd.read_csv(OUTPUT_MATCHIDS_CSV)
#     existing_matchids_set = set(existing_matchids_df['matchid'].tolist())
#     existing_count = len(existing_matchids_set)
#     print(f"Loaded {existing_count} existing match IDs from {OUTPUT_MATCHIDS_CSV}.")
# else:
#     existing_matchids_set = set()
#     existing_count = 0
#     print(f"No existing {OUTPUT_MATCHIDS_CSV} found. Starting fresh.")

# # Define the target total number of match IDs
# TARGET_TOTAL_MATCHIDS = 100000
# remaining_needed = TARGET_TOTAL_MATCHIDS - existing_count

# if remaining_needed <= 0:
#     print(f"Already have {existing_count} match IDs, which meets or exceeds the target of {TARGET_TOTAL_MATCHIDS}.")
# else:
#     print(f"Need to collect {remaining_needed} more match IDs to reach {TARGET_TOTAL_MATCHIDS}.")

#     # Initialize variables to collect new match IDs
#     new_matchids_set = set()
#     matchids_list = []
#     total_players = merged_df.shape[0]

#     for i, row in merged_df.iterrows():
#         puuid = row['puuid']
#         try:
#             match_ids = get_match_ids_by_puuid(
#                 puuid, API_KEY, AMERICAS_REGION, count=MATCHES_PER_PLAYER, queue=420
#             )
#         except Exception as e:
#             print(f"Error fetching match IDs for PUUID {puuid}: {e}")
#             continue  # Skip to the next summoner on error

#         # Filter out existing match IDs
#         unique_new_ids = [mid for mid in match_ids if mid not in existing_matchids_set and mid not in new_matchids_set]
#         new_matchids_set.update(unique_new_ids)
#         matchids_list.extend(unique_new_ids)

#         # Update the total count
#         current_total = existing_count + len(new_matchids_set)

#         # Check if target is reached
#         if current_total >= TARGET_TOTAL_MATCHIDS:
#             print(f"Target of {TARGET_TOTAL_MATCHIDS} match IDs reached.")
#             break

#         # Progress indicator every 100 players
#         if (i + 1) % 100 == 0 or (i + 1) == total_players:
#             elapsed = time.time() - start_time
#             print(f"Processed {i + 1}/{total_players} players for match IDs, elapsed time: {elapsed:.2f} seconds. Total match IDs collected so far: {existing_count + len(new_matchids_set)}")

#         # Respect API rate limits
#         time.sleep(REQUEST_DELAY)

#     # Display the number of new match IDs collected
#     print(f"Collected {len(new_matchids_set)} new unique match IDs.")

#     if new_matchids_set:
#         # Convert the set to a DataFrame
#         new_matchids_df = pd.DataFrame(list(new_matchids_set), columns=['matchid'])

#         # Append to the CSV without writing the header
#         new_matchids_df.to_csv(OUTPUT_MATCHIDS_CSV, mode='a', header=False, index=False)
#         print(f"Appended {len(new_matchids_set)} new match IDs to {OUTPUT_MATCHIDS_CSV}.")

#         # Optional: Update existing_matchids_set if you plan to use it later
#         existing_matchids_set.update(new_matchids_set)
#         existing_count += len(new_matchids_set)
#     else:
#         print("No new match IDs were collected to append.")

#     # Verify the total number of match IDs
#     final_matchids_df = pd.read_csv(OUTPUT_MATCHIDS_CSV)
#     final_count = len(final_matchids_df)
#     print(f"Final total of match IDs: {final_count}")

#     if final_count >= TARGET_TOTAL_MATCHIDS:
#         print(f"Successfully collected {final_count} match IDs.")
#     else:
#         print(f"Only collected {final_count} match IDs. Consider expanding the pool or adjusting parameters.")

df = pd.read_csv(OUTPUT_MATCHIDS_CSV)
matchids_df = df[55501:].reset_index(drop=True)
# Step 4: Get detailed match info and extract features
print(f"Fetching detailed match info... analyzing {len(matchids_df)} rows")

# Define the CSV headers
csv_headers = ['match_id', 'blue_team_champs', 'red_team_champs', 'blue_win', 'collected_at']

# Initialize the CSV file if it doesn't exist
if not os.path.exists(OUTPUT_FINAL_CSV):
    df_headers = pd.DataFrame(columns=csv_headers)
    df_headers.to_csv(OUTPUT_FINAL_CSV, index=False)
    print(f"Initialized {OUTPUT_FINAL_CSV} with headers.")

match_data_list = []
batch_size = 100  # Number of records to write at once

for i, row in matchids_df.iterrows():
    match_id = row['matchid']
    
    # Fetch match information
    response = get_match_info(match_id, API_KEY, AMERICAS_REGION)
    
    # Check for 404 error
    if response.status_code == 404:
        print(f"Row {i}: Match ID {match_id} not found (404)")
        continue  # Skip to the next match_id
    
    # Attempt to parse the JSON response
    try:
        match_data = response.json()
    except ValueError:
        print(f"Row {i}: Invalid JSON response for Match ID {match_id}. Skipping...")
        continue  # Skip to the next match_id
    
    # Extract necessary information
    info = match_data.get('info', {})
    teams = info.get('teams', [])
    participants = info.get('participants', [])

    # Determine if the blue team won
    blue_win = None
    for t in teams:
        if t['teamId'] == 100:
            blue_win = t['win']
            break  # Assuming only one team with teamId 100

    # Extract champions for both teams
    blue_team_champs = [p['championName'] for p in participants if p['teamId'] == 100]
    red_team_champs = [p['championName'] for p in participants if p['teamId'] == 200]

    # Create a match record
    match_record = {
        'match_id': match_id,
        'blue_team_champs': ",".join(blue_team_champs),
        'red_team_champs': ",".join(red_team_champs),
        'blue_win': blue_win,
        'collected_at': datetime.utcnow().isoformat()
    }

    match_data_list.append(match_record)

    # Write to CSV in batches
    if len(match_data_list) >= batch_size:
        df_batch = pd.DataFrame(match_data_list)
        df_batch.to_csv(OUTPUT_FINAL_CSV, mode='a', header=False, index=False)
        print(f"Appended {len(match_data_list)} records to {OUTPUT_FINAL_CSV}.")
        match_data_list = []  # Clear the buffer

        # Optional: Log progress every batch
        elapsed = time.time() - start_time
        print(f"Processed {i + 1}/{len(matchids_df)} matches, elapsed time: {elapsed:.2f} seconds")

    # Respect API rate limits
    time.sleep(REQUEST_DELAY)

# Write any remaining records in the buffer
if match_data_list:
    df_batch = pd.DataFrame(match_data_list)
    df_batch.to_csv(OUTPUT_FINAL_CSV, mode='a', header=False, index=False)
    print(f"Appended remaining {len(match_data_list)} records to {OUTPUT_FINAL_CSV}.")

# Step 5: Save final dataset (Already handled incrementally)
print("Data collection complete. Final dataset saved to:", OUTPUT_FINAL_CSV)


# Step 5: Save final dataset (Already handled incrementally)
print("Data collection complete. Final dataset saved to:", OUTPUT_FINAL_CSV)
