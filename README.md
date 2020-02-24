# afl_team_scraper
Scraper to return team selections for AFL matches

To use:

```
from afl_team_scraper import afl_team_scraper

scraper = afl_team_scraper.AFLTeamSelectionScraper(season='2019',competition_id=1)
round_selected_players = scraper.run_scraper_for_round(27)
```

This returns a dictionary with keys equal to the match ids. Accessing the dictionary for a match gives an object with home and away objects. These objects have keys for the team id, name and selected players.

Note: To scrape:
- AFL: Set competition_id = 1
- AFL Pre season: Set competition_id = 2
- AFLW: Set competition_id = 3
