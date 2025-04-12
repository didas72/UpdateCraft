class ModData:
	local_name: str
	local_version: str
	local_loader: str
	local_license: str
	local_authors: list[str]
	title: str
	slug: str
	compatible_game_versions: set[str]
	chosen_version_id: str
	chosen_version_name: str
	chosen_version_number: str
	chosen_url: str
	highest_game_version: str

	def __init__(self, name: str, version: str, loader: str, license_name: str, authors: list[str]):
		self.local_name = name
		self.local_version = version
		self.local_loader = loader
		self.local_license = license_name
		self.local_authors = authors
		self.title = ""
		self.slug = ""
		self.compatible_game_versions = set()
		self.chosen_version_id = ""
		self.chosen_version_name = ""
		self.chosen_version_number = ""
		self.chosen_url = ""
		self.highest_game_version = ""
