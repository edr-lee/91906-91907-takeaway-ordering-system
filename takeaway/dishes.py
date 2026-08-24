from . import Dish, Drink, Item

DISHES: list[Dish] = [
    Dish("Fish and Chips", 13.99, "fishandchips.jpg"),
    Dish("Chicken Katsu Curry", 14.99, "katsucurry.jpg"),
    Dish("Beef Burger and Fries", 12.49, "burger.jpg"),
    Dish("Vegetable Stir Fry", 11.50, "stirfry.jpg"),
]

DRINKS: list[Drink] = [
    Drink("Coca Cola", 2.50, "1.5L", "cocacola.jpg"),
    Drink("Lemonade", 2.50, "1.5L", "lemonade.jpg"),
    Drink("Orange Juice", 2.20, "500ml", "orangejuice.jpg"),
    Drink("Sparkling Water", 1.80, "500ml", "sparklingwater.jpg"),
]

ITEMS: list[Item] = [*DISHES, *DRINKS]
