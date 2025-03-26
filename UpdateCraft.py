import requests
import json
import glob
import zipfile
import sys
from os import path
import webbrowser

CLI_BANNER = "UpdateCraft v1.0.0 by Didas72"
MODRINTH_API = "https://api.modrinth.com/v2/"
NO_VERSION = "No common version"
NO_MODS = "No mods found"

class LocalModData:
	name: str
	version: str
	title: str
	slug: str
	chosen_version_id: str
	chosen_version_name: str
	chosen_version_number: str
	chosen_url: str

	def __init__(self, name: str, version: str):
		self.name = name
		self.version = version
		self.title = ""
		self.slug = ""
		self.chosen_version_id = ""
		self.chosen_version_name = ""
		self.chosen_version_number = ""
		self.chosen_url = ""

def main(args: list[str]) -> None:
	if len(args) == 1:
		mod_dir: str = args[0]
		check_directory(mod_dir)
	else:
		print_usage()

def print_usage() -> None:
	print("UpdateCraft usage:\n\t" + sys.argv[0] + " <mod_dir> - Scan the directory `mod_dir` for mods")

def check_directory(mod_dir: str):
	mod_paths = glob.glob("*.jar", root_dir=mod_dir)
	mod_list: list[LocalModData] = []
	for mod_path in mod_paths:
		mod_path = path.join(mod_dir, mod_path)
		mod_data = get_mod_data(mod_path)
		if mod_data is not None:
			mod_list.append(mod_data)

	if len(mod_list) == 0:
		print(NO_MODS)
		return

	print("Mods found: " + ", ".join(map(lambda m: m.name+" ("+m.version+")", mod_list)))
	version = find_highest_common_version(mod_list)
	print("Highest common verison:", version)
	print("Suggested actions:")
	has_updates = False
	for mod in mod_list:
		get_mod_latest_compatible(mod, version)
		if mod.version != mod.chosen_version_number:
			print("Update", mod.title, "to version", mod.chosen_version_number, "at", mod.chosen_url)
			has_updates = True
		else:
			print("Mod", mod.title, "is already compatible with version", version)
	if has_updates:
		print("Download suggested versions? [Y/n]")
		choice = input()
		if choice.lower() != "y" and len(choice) != 0:
			return
		print("Downloading in browser")
		for mod in mod_list:
			webbrowser.open_new_tab(mod.chosen_url)

def find_highest_common_version(local_mods: list[LocalModData]) -> str:
	version_sets: list[set[str]] = [get_mod_versions(mod) for mod in local_mods]
	common_versions: list[str] = intersect_mod_verions(version_sets)
	if len(common_versions) == 0:
		return NO_VERSION
	common_versions.sort(reverse=True)
	return common_versions[0]

def get_mod_versions(mod: LocalModData) -> set[str]:
	facets = [["project_type:mod"]]
	response = requests.get(MODRINTH_API+"search", params={ "query": mod.name, "facets": json.dumps(facets), "limit": "1" }) #TODO: Match author, version, etc
	if not response.ok:
		print("Failed search for mod " + mod.name + ": " + str(response.status_code))
		return set()
	mod_data = json.loads(response.content)
	mod.title = mod_data["hits"][0]["title"]
	mod.slug = mod_data["hits"][0]["slug"]
	response = requests.get(MODRINTH_API+"project/"+mod.slug+"/version", params={ "loaders": "[\"fabric\"]" }) #Force only fabric
	if not response.ok:
		print("Failed to get versions for mod " + mod.title + ": " + str(response.status_code))
		return set()
	content = json.loads(response.content)
	versions = list(map(lambda v: v["game_versions"], content))
	version_list = [x for xs in versions for x in xs]
	version_list = list(filter(lambda v: v.startswith("1.") and "-" not in v, version_list)) #Force only stable
	version_set = set(version_list)
	version_list.sort(reverse=True)
	print("Highest version for", mod.title, "is", version_list[0])
	return version_set

def intersect_mod_verions(version_sets: list[set[str]]) -> list[str]:
	if len(version_sets) == 0:
		return []
	intersect = version_sets[0]
	for version_set in version_sets:
		intersect = intersect & version_set
	return list(intersect)

def get_mod_data(mod_path: str) -> LocalModData | None:
	# Assumes fabric mod, later add support for more loaders
	with zipfile.ZipFile(mod_path, "r") as file:
		if "fabric.mod.json" in file.namelist():
			mod_info_bytes = file.read("fabric.mod.json")
			mod_info = json.loads(mod_info_bytes)
			mod_data = LocalModData(mod_info["name"], mod_info["version"])
			return mod_data
		else:
			return None

def get_mod_latest_compatible(mod: LocalModData, game_version: str) -> None:
	response = requests.get(MODRINTH_API+"project/"+mod.slug+"/version", params={ "loaders": "[\"fabric\"]", "game_versions": "[\"" + game_version + "\"]" }) #Force only fabric
	if not response.ok:
		print("Failed to get version for mod " + mod.name + ": " + str(response.status_code))
		return
	content = json.loads(response.content)
	if len(content) == 0:
		print("No compatible versions found for mod " + mod.name)
		return
	mod.chosen_version_id = content[0]["id"]
	mod.chosen_version_name = content[0]["name"]
	mod.chosen_version_number = content[0]["version_number"]
	mod.chosen_url = content[0]["files"][0]["url"] #REVIEW: Arbitrary choice?

if __name__ == "__main__":
	print(CLI_BANNER)
	main(sys.argv[1:])
