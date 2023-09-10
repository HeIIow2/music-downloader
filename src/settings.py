from pathlib import Path
import tomllib


data = tomllib.load(Path("/home/lars/music-kraken.conf").open("r"))
print(data)