import json
import glob
import zipfile
import sys
from os import path
import webbrowser

from constants import NO_MODS, NO_COMMON_VERSION, CLI_BANNER
from data import ModData
from api_requests import api_check, api_search_mod, api_get_mod_versions, api_choose_mod_version
from debug import debug, debug_wait


def main(args: list[str]) -> int:
	if len(args) == 1:
		mod_dir: str = args[0]
		api_status = api_check()
		if api_status is not None:
			print(api_status)
			return 1
		check_directory(mod_dir)
	else:
		print_usage()
		return 0
	print("Done")
	return 0

def print_usage() -> None:
	print("UpdateCraft usage:\n\t" + sys.argv[0] + " <mod_dir> - Scan the directory `mod_dir` for mods")

def check_directory(mod_dir: str) -> int:
	print("\n=== Checking mods folder ===\n")
	mod_list: list[ModData] = get_local_mod_list(mod_dir)
	if len(mod_list) == 0:
		print(NO_MODS)
		return 0

	print("\n=== Mods found ===\n\n" + "\n".join(map(lambda m: m.local_name+" ("+m.local_version+")", mod_list)))
	print("\n=== Checking compatible versions ===\nNOTE: May take some time, the code is not frozen\n")
	game_version = find_highest_common_version(mod_list)
	if game_version == NO_COMMON_VERSION:
		print("=== Could not find a common version ===")
		print("This likely means that the code misidentified at least one of the mods")
		print("Please report this, together with the list of mods detected")
		return 1
	print("\t=> Highest common verison:", game_version)

	print("\n=== Suggested actions ===\n")
	update_count = 0
	for mod in mod_list:
		if len(mod.slug) == 0:
			print("Skipping unidentified mod "+mod.local_name)
			continue
		error = api_choose_mod_version(mod, game_version)
		if error is not None:
			print("WARN: Could not choose version for mod "+mod.title+": "+error+". Skipping...")
			continue
		if mod.local_version != mod.chosen_version_number:
			print("Update", mod.title, "to version", mod.chosen_version_number, "at", mod.chosen_url)
			update_count += 1
		else:
			print("No action for mod", mod.title, "as it is already compatible with", game_version)
	
	if update_count != 0:
		print("\n"+str(update_count)+" suggested updates found")
		print("Download suggested versions? [Y/n]")
		choice = input()
		if choice.lower() != "y" and len(choice) != 0:
			return 0
		print("Downloading "+str(update_count)+" mods in browser...")
		for mod in mod_list:
			if len(mod.chosen_url) == 0:
				continue
			webbrowser.open_new_tab(mod.chosen_url)
	return 0

def find_highest_common_version(local_mods: list[ModData]) -> str:
	version_sets: list[set[str] | None] = [(mod.compatible_game_versions.union({mod.local_name, mod.title}) if get_mod_versions(mod) else None) for mod in local_mods]
	unidentified_count = sum(len(mod.compatible_game_versions) == 0 for mod in local_mods)
	if unidentified_count != 0:
		print("WARN: Could not find", unidentified_count, "mods")
	filtered = list(filter(None, version_sets))
	common_versions: list[str] = intersect_mod_verions(filtered)
	debug("Filtered:", filtered)
	debug("Common:", common_versions)
	debug_wait()
	if len(common_versions) == 0:
		return NO_COMMON_VERSION
	common_versions.sort(reverse=True)
	return common_versions[0]

def get_mod_versions(mod: ModData) -> bool:
	error = api_search_mod(mod)
	if error is not None:
		print("WARN: Failed search for mod "+mod.local_name+": "+error+". Skipping...")
		return False
	error = api_get_mod_versions(mod)
	if error is not None:
		print("WARN: Failed to get versions for mod "+mod.title+": "+error+". Skipping...")
		return False
	return True

def intersect_mod_verions(version_sets: list[set[str]]) -> list[str]:
	if len(version_sets) == 0:
		return []
	intersect = version_sets[0]
	for version_set in version_sets:
		intersect = intersect & version_set
	return list(intersect)

def get_local_mod_list(mod_dir: str) -> list[ModData]:
	mod_paths = glob.glob("*.jar", root_dir=mod_dir)
	mod_list: list[ModData] = []
	for mod_filename in mod_paths:
		mod_path = path.join(mod_dir, mod_filename)
		mod_data = get_local_mod_data(mod_path)
		if mod_data is None:
			print("WARN: Unrecognized jar "+mod_filename+". Skipping...")
			continue
		mod_list.append(mod_data)
	return mod_list

def get_local_mod_data(mod_path: str) -> ModData | None:
	# Assumes fabric mod, later add support for more loaders
	with zipfile.ZipFile(mod_path, "r") as file:
		if "fabric.mod.json" in file.namelist():
			mod_info_bytes = file.read("fabric.mod.json")
			mod_info = json.loads(mod_info_bytes)
			mod_data = ModData(mod_info["name"],\
						mod_info["version"],\
						"fabric",\
						license_name=mod_info["license"] if "license" in mod_info else "license",\
						authors=mod_info["authors"] if "authors" in mod_info else [])
			return mod_data
		else:
			return None

if __name__ == "__main__":
	print(CLI_BANNER)
	exit(main(sys.argv[1:]))
