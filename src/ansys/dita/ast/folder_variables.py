class AutogeneratedFolder:
    def __init__(self, terms) -> None:
        self.autogenerated_folder_name = "ansys.dita.generatedcommands"
        self.version = terms["ansys_internal_version"]
        self.base_url = f"https://ansyshelp.ansys.com/Views/Secured/corp/v{self._version}/en/"
        self.cmd_base_url = f"{self.base_url}/ans_cmd/"

    @property
    def autogenerated_folder_name(self):
        return self._autogenerated_folder_name

    @property
    def version(self):
        return self._version

    @property
    def base_url(self):
        return self._base_url

    @property
    def cmd_base_url(self):
        return self._cmd_base_url

    @autogenerated_folder_name.setter
    def autogenerated_folder_name(self, folder_name):
        self._autogenerated_folder_name = folder_name

    @version.setter
    def version(self, version_value):
        self._version = version_value
        self._base_url = f"https://ansyshelp.ansys.com/Views/Secured/corp/v{self._version}/en/"

    @base_url.setter
    def base_url(self, url):
        self._base_url = url
        self._cmd_base_url = f"{self._base_url}/ans_cmd/"

    @cmd_base_url.setter
    def cmd_base_url(self, base_url):
        self._cmd_base_url = base_url
