# UpdateCraft

Update craft is an easy to use tool to update your modpack to the latest version possible.
It checks what is the latest Minecraft version all your mods are compatible with and enables you to automatically download the required files.  
This tool relies on the Modrinth API to work. Visit the official Modrinth [site](https://modrinth.com/), [Github](https://github.com/modrinth) and [Discord](https://discord.modrinth.com/).

## Features

- Interacts with [Modrinth API](https://docs.modrinth.com/api/) to fetch latest mod versions
- Gets mod list automatically from mod folder

## Installation

1) Download the latest release [here](https://github.com/didas72/UpdateCraft/releases/latest)
2) Save the file `UpdateCraft.py` to a location of your choosing (you can keep it in the Downloads if you desire)

## Usage

1) Navigate to the location where you saved the file `UpdateCraft.py`
2) Open a terminal whre you saved the code
3) Run the tool with `python3 UpdateCraft.py <your_mods_folder>`
4) The program will guide you through any further action you may want to take

## Known issues

- Does not handle reaching the API rate limit

## Roadmap

v1.0.1 - Add missing handling for reaching of API rate limit
v1.1.0 - Automatic dependency check
v1.2.0 - Graphical interface
v1.3.0 - Support for other mod loaders

## Change log

v1.0.0 - Initial release. CLI only version
