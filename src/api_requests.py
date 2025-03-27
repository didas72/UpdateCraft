import requests
import json
from time import sleep
from datetime import timedelta
from os import environ
from sys import stderr

from constants import *
from data import ModData

DEBUG = "DEBUG" in environ

def api_check() -> str | None:
	url = MODRINTH_API_CHECK
	response = requests.get(url=url)
	if not response.ok:
		return "ERROR: Failed to get response"
	content = json.loads(response.content)
	if "version" not in content:
		return "ERROR: Bad API response format"
	if not str(content["version"]).startswith(MODRINTH_API_VERSION_REQUIRED):
		return "ERROR: Incompatible API version. Please report this to the developer at https://github.com/didas72/UpdateCraft/issues"
	return None

def api_request(path: str, params: dict[str, object] = {}, retry_attempts: int = 0, retry_delay: timedelta = timedelta(seconds=1)) -> dict | None:
	url = MODRINTH_API_BASE + path
	formatted_params = { key: json.dumps(params[key]) for key in params }

	response = requests.get(url=url, params=formatted_params, headers=HEADERS)
	while retry_attempts > 0 and not response.ok:
		sleep(retry_delay.total_seconds())
		response = requests.get(url=url, params=formatted_params, headers=HEADERS)
		retry_attempts -= 1
	if not response.ok:
		if DEBUG:
			print("DEBUG: Request to "+url+" failed with code " + str(response.status_code), file=stderr)
			print("DEBUG: Formatted url:", response.url, file=stderr)
			print("DEBUG: Response headers:", response.headers, file=stderr)
			print("DEBUG: Response content:", response.content, file=stderr)
		return None
	
	content = json.loads(response.content)
	return content
	
def api_search_mod(mod_data: ModData) -> str | None:
	content = api_request(
		MODRINTH_API_SEARCH,
		params={ "query": mod_data.local_name, "facets": [["project_type:mod"]], "limit": 1 })
	if content is None:
		return REQUEST_FAILED
	if "hits" not in content or len(content["hits"]) == 0:
		return MOD_NOT_FOUND
	
	#TODO: Match author, version, etc
	mod_data.title = content["hits"][0]["title"]
	mod_data.slug = content["hits"][0]["slug"]
	return None

def api_get_mod_versions(mod_data: ModData) -> str | None:
	content = api_request(
		MODRINTH_API_PROJECT+"/"+mod_data.slug+"/"+MODRINTH_API_VERSION,
		params={ "loaders": "[\""+mod_data.local_loader+"\"]" })
	
	if content is None:
		return REQUEST_FAILED
	if len(content) == 0:
		return NO_COMPATIBLE_VERSION
	
	versions = list(map(lambda v: v["game_versions"], content))
	version_list = [x for xs in versions for x in xs]
	#TODO: Only optionally force only stable
	version_list = list(filter(lambda v: v.startswith("1.") and "-" not in v, version_list))
	version_list.sort(reverse=True)

	mod_data.highest_game_version = version_list[0]
	mod_data.compatible_game_versions = set(version_list)
	return None

def api_choose_mod_version(mod_data: ModData, game_version: str) -> str | None:
	content = api_request(
		MODRINTH_API_PROJECT+"/"+mod_data.slug+"/"+MODRINTH_API_VERSION,
		params={ "loaders": "[\""+mod_data.local_loader+"\"]", "game_versions": "[\"" + game_version + "\"]" })

	if content is None:
		return REQUEST_FAILED
	if len(content) == 0:
		return NO_COMPATIBLE_VERSION
	
	mod_data.chosen_version_id = content[0]["id"]
	mod_data.chosen_version_name = content[0]["name"]
	mod_data.chosen_version_number = content[0]["version_number"]
	mod_data.chosen_url = content[0]["files"][0]["url"] #REVIEW: Arbitrary choice?
	return None
