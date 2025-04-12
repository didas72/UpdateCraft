#Version and banner
VERSION_STRING = "v1.0.1"
CLI_BANNER = "UpdateCraft " + VERSION_STRING + " by Didas72"

#Error messages
NO_COMMON_VERSION = "No common version"
NO_MODS = "No mods found"
REQUEST_FAILED = "Request failed"
MOD_NOT_FOUND = "Mod not found"
NO_COMPATIBLE_VERSION = "No compatible version"

#API
MODRINTH_API_CHECK = "https://api.modrinth.com/"
MODRINTH_API_BASE = "https://api.modrinth.com/v2/"
MODRINTH_API_VERSION_REQUIRED = "2."
HEADERS = {"User-Agent": "didas72/UpdateCraft/"+VERSION_STRING+" (diogocruzdiniz@gmail.com)"}
MODRINTH_API_SEARCH = "search"
MODRINTH_API_PROJECT = "project"
MODRINTH_API_VERSION = "version"

#Affinity
NAME_AFFINITY = 5.0
AUTHOR_AFFINITY = 2.0
LICENSE_AFFINITY = 1.0
SUBSTRING_BASE = 0.9
SEQ_MATCH_WEIGHT = 0.7
TOK_OVERLAP_WEIGHT = 0.3
