"""Takeaway system TUI."""

from takeaway.cart import Cart
from takeaway.dishes import ITEMS

if __name__ == "__main__":
    print("Welcome to the takeaway ordering system!")
    name = input("Please enter your name: ")
    cart = Cart(name)
    print(f"Hello {name}!")

    while True:
        print()
        print("Please select an item from the menu:")

        for i, item in enumerate(ITEMS):
            print(f"{i + 1}. {item}")

        print("-----")
        print("l. List items in cart")
        print("c. Checkout")

        print()
        choice: str = input("Enter your choice: ")

        # Cannot use match statement here, as we are using Python 3.9 :/
        if choice == "l":
            if len(cart.items) == 0:
                print("Your cart is empty.")
            else:
                print("Items in your cart:")
                for cart_item in cart.items:
                    print(
                        f"{cart_item.quantity} x {cart_item.item.name} (total ${cart_item.total_price_without_tax():.2f})"
                    )
        elif choice == "c":
            break
        else:
            try:
                choice_int = int(choice)
                if not (0 <= choice_int < len(ITEMS)):
                    print("Invalid choice. Please try again.")
                    continue

                item = ITEMS[choice_int - 1]
                cart.add_item(item, 1)
                print(f"Added {item.name} to cart!")
            except ValueError:
                print("Invalid choice. Please try again.")
                continue

    if len(cart.items) > 0:
        print(f"{cart.name}, thank you for ordering!")
        print("Items you have purchased:")
        for cart_item in cart.items:
            print(
                f"{cart_item.quantity} x {cart_item.item.name} (total ${cart_item.total_price_without_tax():.2f})"
            )
        print(f"Your total is: ${cart.total_price():.2f}")
