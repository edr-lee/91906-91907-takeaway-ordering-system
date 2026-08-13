"""Classes for the Cart system."""

from . import Item


class CartItem:
    """Represents an item in the cart."""

    item: Item
    """The item being added to the cart."""
    quantity: int
    """The quantity of the item."""

    def __init__(self, item: Item, quantity: int):
        self.item = item
        self.quantity = quantity

    def total_price_without_tax(self) -> float:
        """Calculate the total price of the item (without tax)
        with the quantity chosen.
        """
        return self.item.price_without_tax * self.quantity

    def __str__(self) -> str:
        return f"{self.item.name} x {self.quantity} (${self.total_price_without_tax():.2f})"


class Cart:
    """Represents a cart containing items."""

    name: str
    """Name of the customer who owns the cart."""
    items: list[CartItem]
    """Items in the cart."""
    tax_rate: float
    """Tax rate applied to the cart on checkout."""

    def __init__(self, name: str):
        """Create a new cart with the customer's name."""
        self.name = name
        self.items = []
        self.tax_rate = 1.15  # GST in New Zealand: 15%

    def add_item(self, item: Item, quantity: int) -> None:
        """Add an item to the cart."""
        # If the user has this item already, increase the quantity.
        # Otherwise, add it to the cart.
        for cart_item in self.items:
            if cart_item.item == item:
                cart_item.quantity += quantity
                break
        else:
            self.items.append(CartItem(item, quantity))

    def remove_item(self, item: Item) -> None:
        """Remove an item from the cart."""
        # If the user has more than one of this item, remove one of the quantity
        # Otherwise remove it outright.
        for cart_item in self.items:
            if cart_item.item == item:
                if cart_item.quantity > 1:
                    cart_item.quantity -= 1
                else:
                    self.items.remove(cart_item)
                break

    def total_price(self) -> float:
        """Calculate the total price of all items in the cart with tax."""
        return (
            sum(item.total_price_without_tax() for item in self.items) * self.tax_rate
        )
