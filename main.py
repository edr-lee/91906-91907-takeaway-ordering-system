"""Takeaway system GUI."""

import abc
from pathlib import Path
from tkinter import END, Listbox, Tk, Toplevel, messagebox
from tkinter import Button as TkButton
from tkinter import Label as TkLabel
from tkinter.ttk import Button as TtkButton
from tkinter.ttk import Entry, Frame, Label

from PIL import Image, ImageTk

from takeaway import Item
from takeaway.cart import Cart
from takeaway.data import Data
from takeaway.dishes import ITEMS, DRINKS, DISHES


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


data: Data = Data()
cart: Cart
tabs: list[Tab] = []
root: Tk


def main() -> None:
    """Takeaway system GUI."""

    global root
    root = Tk()
    root.title(f"{data.name} Ordering System")

    show_greet_window(root)
    root.withdraw()  # greet window will unhide root window

    tabs.append(get_ordering_tab(root, ITEMS))

    root.mainloop()


def show_main_window() -> None:
    root.deiconify()
    switch_tabs(0)  # Show the first frame (ordering frame)


def show_checkout_window() -> Toplevel:
    root.withdraw()  # can't destroy main window because it'll kill toplevel
    toplevel = Toplevel(root)
    # don't leave the main window hanging if user closes toplevel
    # https://stackoverflow.com/questions/111155/how-do-i-handle-the-window-close-event-in-tkinter
    toplevel.protocol("WM_DELETE_WINDOW", root.destroy)

    Label(toplevel, text=f"Thank you for ordering at {data.name}!").grid(
        row=0, column=0, columnspan=2
    )
    Label(
        toplevel,
        text=f"""Price of items: ${cart.total_price_without_tax():.2f}
GST: ${cart.tax_amount():.2f}
Total price: ${cart.total_price_with_tax():.2f}""",  # noqa: F821
    ).grid(row=1, column=0)

    TtkButton(toplevel, text="Exit", command=root.destroy).grid(
        row=2, column=0, columnspan=2
    )

    return toplevel


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
    toplevel.protocol("WM_DELETE_WINDOW", root.destroy)

    Label(toplevel, text=f"Welcome to the {data.name} ordering system!").grid(
        row=0, column=0, columnspan=2
    )
    Label(toplevel, text="Please enter your name:").grid(row=1, column=0)
    name_entry = Entry(toplevel)
    name_entry.grid(row=1, column=1)

    TtkButton(toplevel, text="Start ordering", command=start_ordering).grid(
        row=2, column=0, columnspan=2
    )

    return toplevel


def get_ordering_tab(root: Tk, items: list[Item]) -> Tab:
    # Destroy ordering frame if it already exists
    try:
        root.children["ordering_frame"].destroy()
    except KeyError:
        pass

    cart_display = Listbox(root, width=50, height=10)
    max_column = 0

    def remove_selected_item_from_cart(event) -> None:
        """Remove one quantity of the selected cart item."""

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

    def get_items_frame(parent: Frame, width: int, items: list[Item]) -> Frame:
        """Get an item frame that shows a $(width)x? grid of items
        and lets the user add them to the cart.
        """

        def add_to_cart(item: Item) -> None:
            """Add an item to the cart and repaint the display."""
            cart.add_item(item, 1)
            update_cart_display(cart)

        def load_item_image(item: Item) -> ImageTk.PhotoImage:
            image_path = Path(__file__).parent / "assets" / "img" / item.image_filename
            image = Image.open(image_path)
            image = image.resize((100, 100), Image.LANCZOS)
            return ImageTk.PhotoImage(image)



        nonlocal max_column
        frame = Frame(parent)

        for i, item in enumerate(items):
            row = (i // width) + 1
            # wrap over if we already have $(width) in the current row
            col = i % width
            max_column = max(max_column, col)
            # Yes, we are using unstyled tkinter button.
            # Ttk/themed tkinter button does not allow us to change the width/height,
            # at least on macOS.
            item_frame = Frame(frame)

            # have to set it twice for some reason, otherwise the image won't show up :/
            image = load_item_image(item)
            image_label = TkLabel(item_frame, image=image)
            image_label.image = image
            image_label.grid(row=0, column=0, padx=5, pady=5)

            TkButton(
                item_frame,
                width=20,
                height=3,
                text=str(item),
                command=lambda item=item: add_to_cart(item),
            ).grid(row=0, column=1, padx=5, pady=5)
            item_frame.grid(row=row, column=col, padx=5, pady=5)

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
            show_checkout_window()

    frame = Frame(root, name="ordering_frame")
    frame.grid(row=0, column=0, sticky="nsew")

    Label(
        frame,
        text=f"""Ordering at {data.name}!
Select an item below to add it to your cart.
Select an item in your cart (right side) to remove 1x of it from the cart.""",
    ).grid(row=0, column=0, columnspan=5)

    # Show all items in a 2x? grid
    get_items_frame(frame, 2, items).grid(row=1, column=0, padx=10, pady=10)

    # Filtering items
    filter_button_frames = Frame(frame)
    # All dishes
    TtkButton(
        filter_button_frames, text="Dishes", command=lambda: update_ordering_tab(root, DISHES)
    ).pack()
    # All drinks
    TtkButton(
        filter_button_frames, text="Drinks", command=lambda: update_ordering_tab(root, DRINKS)
    ).pack()
    # All items
    TtkButton(
        filter_button_frames, text="All Items", command=lambda: update_ordering_tab(root, ITEMS)
    ).pack()

    filter_button_frames.grid(row=1, column=1, padx=10, pady=10)
    checkout_button = TtkButton(
        frame, text="Checkout", command=lambda: ask_go_to_checkout()
    )
    checkout_button.grid(row=4, column=1, padx=10, pady=10)
    # https://www.geeksforgeeks.org/python/binding-function-with-double-click-with-tkinter-listbox/
    # https://stackoverflow.com/questions/6554805/getting-a-callback-when-a-tkinter-listbox-selection-is-changed
    cart_display.bind("<<ListboxSelect>>", remove_selected_item_from_cart)

    # Build cart display
    # At this point, cart may be undefined.
    try:
        cart_to_use = cart
    except NameError:
        # This dummy cart is used to build the initial cart display,
        # which will be updated using the proper cart once the user enters their name.
        cart_to_use = Cart("")
    update_cart_display(cart_to_use)

    return Tab(frame)


def update_ordering_tab(root: Tk, items: list[Item]) -> None:
    tabs[0] = get_ordering_tab(root, items)

if __name__ == "__main__":
    main()
