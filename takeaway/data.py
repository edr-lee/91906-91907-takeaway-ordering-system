from __future__ import annotations

import os
from json import loads
from pathlib import Path
from typing import Any

from takeaway import Dish, Drink, Item

takeaway_json_path = Path(os.path.realpath(__file__)).parent.parent / "takeaway.json"
items_json_path = Path(os.path.realpath(__file__)).parent.parent / "items.json"


class TakeawayData:
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


class ItemsData:
    items: list[Item]

    _raw: dict[str, Any]

    def __init__(self, path_to_data_json: str | os.PathLike[str] | None = None):
        if path_to_data_json is None:
            path_to_data_json = items_json_path

        try:
            with open(path_to_data_json, "r") as file:
                self._raw = loads(file.read())
            # deserialize into our item classes
            self.items = []
            for item in self._raw["items"]:
                if item["type"] == "dish":
                    self.items.append(
                        Dish(
                            item["name"],
                            item["price_without_tax"],
                            item["image_filename"],
                        )
                    )
                elif item["type"] == "drink":
                    self.items.append(
                        Drink(
                            item["name"],
                            item["price_without_tax"],
                            item["size"],
                            item["image_filename"],
                        )
                    )
                else:
                    raise ValueError(f"Invalid item type: {item['type']}")
        except (KeyError, FileNotFoundError):
            self.create_template(path_to_data_json)
            self.__init__(path_to_data_json)

    def create_template(self, path_to_data_json: str | os.PathLike[str]) -> None:
        with open(path_to_data_json, "w") as file:
            file.write("""{
  "items": [
    {
      "name": "Fish and Chips",
      "price_without_tax": 13.99,
      "image_filename": "fishandchips.jpg",
      "type": "dish"
    },
    {
      "name": "Chicken Katsu Curry",
      "price_without_tax": 14.99,
      "image_filename": "katsucurry.jpg",
      "type": "dish"
    },
    {
      "name": "Beef Burger and Fries",
      "price_without_tax": 12.49,
      "image_filename": "burger.jpg",
      "type": "dish"
    },
    {
      "name": "Vegetable Stir Fry",
      "price_without_tax": 11.50,
      "image_filename": "stirfry.jpg",
      "type": "dish"
    },
    {
      "name": "Coca Cola",
      "price_without_tax": 2.50,
      "size": "1.5L",
      "image_filename": "cocacola.jpg",
      "type": "drink"
    },
    {
      "name": "Lemonade",
      "price_without_tax": 2.50,
      "size": "1.5L",
      "image_filename": "lemonade.jpg",
      "type": "drink"
    },
    {
      "name": "Orange Juice",
      "price_without_tax": 2.20,
      "size": "500ml",
      "image_filename": "orangejuice.jpg",
      "type": "drink"
    },
    {
      "name": "Sparkling Water",
      "price_without_tax": 1.80,
      "size": "500ml",
      "image_filename": "sparklingwater.jpg",
      "type": "drink"
    }
  ]
}""")
