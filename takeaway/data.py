from __future__ import annotations

import os
from json import loads
from pathlib import Path
from typing import Any

takeaway_json_path = Path(os.path.realpath(__file__)).parent.parent / "takeaway.json"


class Data:
    name: str
    """Name of the takeaway."""

    _raw: dict[str, Any]

    def __init__(self, path_to_data_json: str | os.PathLike[str] | None = None):
        if path_to_data_json is None:
            path_to_data_json = takeaway_json_path

        try:
            with open(path_to_data_json, "r") as file:
                self._raw = loads(file.read())
            # deserialize into our class
            self.name = self._raw["name"]
        except (KeyError, FileNotFoundError):
            self.create_template(path_to_data_json)
            self.__init__(path_to_data_json)

    def create_template(self, path_to_data_json: str | os.PathLike[str]) -> None:
        with open(path_to_data_json, "w") as file:
            file.write("""{
  "name": "Takeaway Name"
}""")
