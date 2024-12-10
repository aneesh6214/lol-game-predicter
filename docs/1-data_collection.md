# Data Collection & Preparation (Step 1)

## Overview
The first stage of the project focused on collecting, cleansing, and preparing match data from the Riot API. This data serves as the foundation for all subsequent analysis and modeling efforts.

## Key Activities
1. **Summoner Identification:**  
   - Identified a cohort of Gold-tier ranked players to ensure data consistency and relevance.
   - Used the Riot API’s League-V4 endpoints to retrieve a list of qualified summoners.

2. **Summoner Data Retrieval:**  
   - For each identified summoner, retrieved their unique identifiers (PUUIDs) required to access match histories.
   - Ensured compliance with Riot API usage policies and rate limits during data retrieval.

3. **Match ID Extraction:**  
   - Utilized the Match-V5 endpoints to obtain recent ranked match IDs for each summoner’s account.
   - Focused exclusively on RANKED_SOLO_5x5 (queue=420) matches to maintain a uniform dataset.

4. **Match Data Download:**  
   - For each match ID, fetched detailed match-level information, including all participating champions and the resulting outcome.
   - Extracted team compositions (champion names) and stored the result of the match (win/loss).

5. **Data Cleansing & Structuring:**  
   - Removed duplicate records and ensured all match IDs were unique.
   - Organized champion picks into a structured format (e.g., separate columns for each team’s champions).
   - Stored the final dataset in a CSV file, ready for feature engineering and modeling.

## Deliverables
- **Summoner List CSV:** A file containing information on selected Gold-tier summoners and their corresponding PUUIDs.
- **Match IDs CSV:** A list of unique match IDs associated with the summoners.
- **Final Match Data CSV:** A structured dataset containing champion picks and match outcomes.

## Lessons Learned
- **API Rate Limits:** Implemented backoff and retry logic to handle 429 (rate limit) responses.
- **Data Quality Checks:** Ensured that only completed and relevant matches were included. Matches that ended prematurely or were outside the desired queue were excluded.

## Next Steps
With the data now prepared, I will proceed to:
- Perform feature engineering to represent champion picks as meaningful numerical features.
- Evaluate different modeling approaches to predict match outcomes based on champion composition alone.

This completed step ensures I have a strong, reliable starting point for all subsequent modeling efforts.
