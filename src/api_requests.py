import requests
import json
from time import sleep
from datetime import timedelta

from difflib import SequenceMatcher

from constants import *
from data import ModData
from debug import debug, debug_wait

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
		debug("Request to "+url+" failed with code " + str(response.status_code))
		debug("Formatted url:", response.url)
		debug("Response headers:", response.headers)
		debug("Response content:", response.content)
	
	content = json.loads(response.content)
	return content
	
def api_search_mod(mod_data: ModData) -> str | None:
	searchName: str = mod_data.local_name
	content = api_request(
		MODRINTH_API_SEARCH,
		params={ "query": searchName, "facets": [["project_type:mod"], ["categories:" + mod_data.local_loader]], "limit": 5 })
	if content is None:
		return REQUEST_FAILED
	if "hits" not in content or len(content["hits"]) == 0:
		return MOD_NOT_FOUND
	
	remotes: list[tuple[dict, float]] = [(hit, api_calculate_mod_affinity(mod_data, hit)) for hit in content["hits"]]
	remotes.sort(key=lambda r: r[1], reverse=True)
	selected = remotes[0]
	selected_hit: dict = selected[0]
	selected_affinity: float = selected[1]

	debug("Selected mod", selected_hit["title"], "for search", searchName, "with affinity", selected_affinity)

	mod_data.title = selected_hit["title"]
	mod_data.slug = selected_hit["slug"]
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

def string_affinity(a: str, b: str) -> float:
	a, b = a.lower(), b.lower()
	sm_score = SequenceMatcher(None, a, b).ratio()
    
	# Boost if one is a substring of the other
	if a in b or b in a:
		sm_score = max(sm_score, SUBSTRING_BASE)

	# Token-based bonus (good for word reordering or missing middle words)
	local_tokens = set(a.split())
	remote_tokens = set(b.split())
	token_overlap = len(local_tokens & remote_tokens) / max(len(local_tokens | remote_tokens), 1)

	return (sm_score * SEQ_MATCH_WEIGHT) + (token_overlap * TOK_OVERLAP_WEIGHT)

def api_calculate_mod_affinity(local: ModData, remote: dict) -> float:
	affinity: float = 0
	name_affinity = string_affinity(local.local_name, remote["title"])
	affinity += name_affinity * NAME_AFFINITY
	#FIXME: Local is mod version, remote is minecraft version
	#if local.local_version not in remote["versions"]:
	#	debug("Remote does not have local version:", local.local_version, remote["versions"])
	#	return False
	if len(local.local_license) != 0:
		affinity += string_affinity(local.local_license, remote["license"]) * LICENSE_AFFINITY
	if remote["author"] in local.local_authors:
		affinity += AUTHOR_AFFINITY
	return affinity
