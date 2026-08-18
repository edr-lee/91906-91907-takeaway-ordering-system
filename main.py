"""Takeaway system GUI."""

from tkinter import END, Listbox, Tk, Toplevel, messagebox
from tkinter import Button as TkButton
from tkinter.ttk import Button as TtkButton
from tkinter.ttk import Entry, Frame, Label

from takeaway import Item
from takeaway.cart import Cart
from takeaway.dishes import ITEMS

cart: Cart
frames: list[Frame] = []
root: Tk


def main() -> None:
    """Takeaway system GUI."""

    global root
    root = Tk()
    root.title("Takeaway Ordering System")

    show_greet_window(root)
    root.withdraw()

    frames.append(get_ordering_frame(root))

    root.mainloop()


def show_main_window() -> None:
    root.deiconify()
    switch_frames(0)  # Show the first frame (ordering frame)


def switch_frames(index: int) -> None:
    frames[index].tkraise()


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


def get_ordering_frame(root: Tk) -> Frame:
    cart_display = Listbox(root, width=50, height=10)
    max_column = 0

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

    frame = Frame(root)
    frame.grid(row=0, column=0, sticky="nsew")

    Label(frame, text="Takeaway Ordering System!").grid(row=0, column=0, columnspan=5)

    # Show all items in a 4x? grid
    get_items_frame(frame, 4).grid(row=1, column=0, padx=10, pady=10)

    # Build initial cart display
    # At this point, cart will be undefined.
    # This dummy cart is used to build the initial cart display,
    # which will be updated using the proper cart once the user enters their name.
    update_cart_display(Cart(""))

    return frame


if __name__ == "__main__":
    main()
