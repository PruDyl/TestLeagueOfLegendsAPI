# Script to have the last 2 months' matches in discord

## Requirements:
```
python3.5
```

## Usage:
### Main usage:
```
python lol_stats.discord.py -h
python lol_stats.discord.py --key <API_KEY> --token <DISCORD_BOT_TOKEN>
```

### Module usage:
```
import lol_stat

lol_stat.run(api_key="", summoner="")
```

## Improvements
* Use a db for data instead of files
* Stylish discord embed message
* Logging
* Discord bot more friendly (add communication with user)
