"""Takeaway system GUI."""

import abc
from tkinter import END, Listbox, Tk, Toplevel, messagebox
from tkinter import Button as TkButton
from tkinter.ttk import Button as TtkButton
from tkinter.ttk import Entry, Frame, Label

from takeaway import Item
from takeaway.cart import Cart
from takeaway.dishes import ITEMS


class Tab(abc.ABC):
    """A tab in the GUI."""

    frame: Frame
    active: bool = False

    def __init__(self, frame: Frame) -> None:
        self.frame = frame

    def show(self) -> None:
        """Show the tab."""
        self.active = True
        self.frame.tkraise()


class CheckoutTab(Tab):
    def show(self) -> None:
        """Show the tab."""
        global cart

        Label(self.frame, text="Takeaway Ordering System!").grid(row=0, column=0, columnspan=5)
        Label(self.frame, text=f"{cart.name}, thank you for ordering!").grid(row=1, column=0, columnspan=5)
        Label(
            self.frame,
            text=f"Your total order comes to: ${cart.total_price():.2f}",
        ).grid(row=2, column=0)

        TkButton(self.frame, text="Exit", command=root.quit).grid(row=3, column=0, columnspan=5, padx=10, pady=10)

        super().show()


cart: Cart
tabs: list[Tab] = []
root: Tk


def main() -> None:
    """Takeaway system GUI."""

    global root
    root = Tk()
    root.title("Takeaway Ordering System")

    show_greet_window(root)
    root.withdraw()  # greet window will unhide root window

    tabs.append(get_ordering_tab(root))
    tabs.append(get_checkout_tab(root))

    root.mainloop()


def show_main_window() -> None:
    root.deiconify()
    switch_tabs(0)  # Show the first frame (ordering frame)


def switch_tabs(index: int) -> None:
    for tab in tabs:
        tab.active = False
    tabs[index].show()


def show_greet_window(root: Tk) -> Toplevel:
    def start_ordering() -> None:
        name = name_entry.get().strip()
        if name == "":
            messagebox.showerror("Invalid name", "Name cannot be empty.")
            return

        # valid input: create cart and switch to ordering frame
        global cart
        cart = Cart(name)
        show_main_window()
        toplevel.destroy()

    toplevel = Toplevel(root)

    Label(toplevel, text="Welcome to the Takeaway Ordering System!").grid(
        row=0, column=0, columnspan=2
    )
    Label(toplevel, text="Please enter your name:").grid(row=1, column=0)
    name_entry = Entry(toplevel)
    name_entry.grid(row=1, column=1)

    TtkButton(toplevel, text="Start ordering", command=start_ordering).grid(
        row=2, column=0, columnspan=2
    )

    return toplevel


def get_ordering_tab(root: Tk) -> Tab:
    cart_display = Listbox(root, width=50, height=10)
    max_column = 0

    def remove_selected_item_from_cart(event) -> None:
        """Remove one quantity of the selected cart item."""

        # Do not remove items if we are in the checkout tab
        if tabs[-1].active:
            return

        selection = event.widget.curselection()
        if len(selection) == 0:
            return

        selected_index = selection[0]
        if selected_index >= len(cart.items):
            return

        cart.remove_item(cart.items[selected_index].item)
        update_cart_display(cart)

    def update_cart_display(cart: Cart) -> None:
        """Update the cart display with new items."""
        # Destroy the old cart display...
        cart_display.grid_forget()
        cart_display.delete(0, END)

        # Rebuild the cart display with new items
        for item in cart.items:
            cart_display.insert(END, str(item))

        # Repack
        # We need to forcefully repaint the UI otherwise the cart display will be empty
        # until next update, leading to a flash.
        cart_display.grid(row=0, column=max_column)
        root.update_idletasks()

    def get_items_frame(parent: Frame, width: int) -> Frame:
        """Get an item frame that shows a $(width)x? grid of items
        and lets the user add them to the cart.
        """

        def add_to_cart(item: Item) -> None:
            """Add an item to the cart and repaint the display."""
            cart.add_item(item, 1)
            update_cart_display(cart)

        nonlocal max_column
        frame = Frame(parent)

        for i, item in enumerate(ITEMS):
            row = (i // width) + 1
            # wrap over if we already have $(width) in the current row
            col = i % width
            max_column = max(max_column, col)
            # Yes, we are using unstyled tkinter button.
            # Ttk/themed tkinter button does not allow us to change the width/height,
            # at least on macOS.
            TkButton(
                frame,
                width=20,
                height=3,
                text=str(item),
                command=lambda item=item: add_to_cart(item),
            ).grid(row=row, column=col, padx=5, pady=5)

        return frame

    def ask_go_to_checkout() -> None:
        if len(cart.items) == 0:
            messagebox.showerror(
                "Empty cart", "You cannot go to checkout with an empty cart."
            )
            return

        if messagebox.askyesno(
            "Go to checkout", "Are you sure you want to go to checkout?"
        ):
            switch_tabs(-1)  # Show the last frame (checkout frame)

    frame = Frame(root)
    frame.grid(row=0, column=0, sticky="nsew")

    Label(frame, text="Takeaway Ordering System!\nSelect an item to remove 1x of it from the cart.").grid(row=0, column=0, columnspan=5)

    # Show all items in a 4x? grid
    get_items_frame(frame, 4).grid(row=1, column=0, padx=10, pady=10)

    checkout_button = TtkButton(
        frame, text="Checkout", command=lambda: ask_go_to_checkout()
    )
    checkout_button.grid(row=2, column=0, padx=10, pady=10)
    # https://www.geeksforgeeks.org/python/binding-function-with-double-click-with-tkinter-listbox/
    # https://stackoverflow.com/questions/6554805/getting-a-callback-when-a-tkinter-listbox-selection-is-changed
    cart_display.bind("<<ListboxSelect>>", remove_selected_item_from_cart)

    # Build initial cart display
    # At this point, cart will be undefined.
    # This dummy cart is used to build the initial cart display,
    # which will be updated using the proper cart once the user enters their name.
    update_cart_display(Cart(""))

    return Tab(frame)


def get_checkout_tab(root: Tk) -> Tab:
    frame = Frame(root)
    frame.grid(row=0, column=0, sticky="nsew")

    return CheckoutTab(frame)


if __name__ == "__main__":
    main()
