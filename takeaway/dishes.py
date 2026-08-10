from . import Dish, Drink, Item

DISHES: list[Dish] = [
    Dish("Fish and Chips", 13.99),
    Dish("Chicken Katsu Curry", 14.99),
    Dish("Beef Burger and Fries", 12.49),
    Dish("Vegetable Stir Fry", 11.50),
]

DRINKS: list[Drink] = [
    Drink("Coca Cola", 2.50, "1.5L"),
    Drink("Lemonade", 2.50, "1.5L"),
    Drink("Orange Juice", 2.20, "500ml"),
    Drink("Sparkling Water", 1.80, "500ml"),
]

ITEMS: list[Item] = [*DISHES, *DRINKS]
