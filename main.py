"""Takeaway system GUI."""

from abc import ABC
from datetime import date
from pathlib import Path
from tkinter import Button as TkButton
from tkinter import Label as TkLabel
from tkinter import Tk, Toplevel, messagebox
from tkinter.ttk import Button as TtkButton
from tkinter.ttk import Entry, Frame, Label, Treeview

from PIL import Image, ImageDraw, ImageTk

from takeaway import Dish, Drink, Item
from takeaway.cart import Cart
from takeaway.data import TakeawayData
from takeaway.dishes import DISHES, DRINKS, ITEMS


class Tab(ABC):
    """A tab in the GUI."""

    frame: Frame
    active: bool = False

    def __init__(self, frame: Frame) -> None:
        self.frame = frame

    def show(self) -> None:
        """Show the tab."""
        self.active = True
        self.frame.tkraise()


data: TakeawayData
cart: Cart
tabs: list[Tab] = []
root: Tk


def save_receipt() -> None:
    """Save the checkout receipt."""
    date_str = date.today().isoformat()
    checkout_path = Path(__file__).resolve().parent / f"{date_str}_receipt.txt"
    checkout_path.write_text(
        f"Date: {date_str}\n{cart.get_receipt()}\n",
        encoding="utf-8",
    )


def main() -> None:
    """Takeaway system GUI."""

    global data, root
    root = Tk()
    data = TakeawayData(root)
    root.title(f"{data.name} Ordering System")

    show_greet_window(root)
    root.withdraw()  # greet window will unhide root window

    tabs.append(get_ordering_tab(root, ITEMS))

    root.mainloop()


def show_main_window() -> None:
    root.deiconify()
    switch_tabs(0)  # Show the first frame (ordering frame)


def show_checkout_window() -> Toplevel:
    save_receipt()
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

    Label(toplevel, text=f"Welcome to {data.name} ordering system!").grid(
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

    frame = Frame(root, name="ordering_frame")
    frame.grid(row=0, column=0, sticky="nsew")
    items_per_page = 8
    current_page = 0

    cart_display = Treeview(
        frame,
        columns=("quantity", "price_for_one", "total_price"),
        show="tree headings",
        height=25,
    )
    cart_display.heading("#0", text="Item name")
    cart_display.heading("quantity", text="Quantity")
    cart_display.heading("price_for_one", text="Price for one")
    cart_display.heading("total_price", text="Total price")
    cart_display.column("#0", anchor="w", width=150, stretch=False)
    cart_display.column("quantity", anchor="center", width=60, stretch=False)
    cart_display.column("price_for_one", anchor="e", width=90, stretch=False)
    cart_display.column("total_price", anchor="e", width=90, stretch=False)
    cart_row_items: dict[str, Item] = {}

    def remove_selected_item_from_cart(event) -> None:
        """Remove one quantity of the selected cart item."""

        selection = event.widget.selection()
        if len(selection) == 0:
            return

        selected_iid = selection[0]
        selected_item = cart_row_items.get(selected_iid)
        if selected_item is None:
            return

        cart.remove_item(selected_item)
        update_cart_display(cart)

    def update_cart_display(cart: Cart) -> None:
        """Update the cart display with new items."""
        cart_display.delete(*cart_display.get_children())
        cart_row_items.clear()

        dishes_group_iid = cart_display.insert(
            "", "end", iid="group_dishes", text="Dishes", open=True
        )
        drinks_group_iid = cart_display.insert(
            "", "end", iid="group_drinks", text="Drinks", open=True
        )

        # Rebuild the cart display with new items grouped by category.
        for i, cart_item in enumerate(cart.items):
            if isinstance(cart_item.item, Dish):
                parent_iid = dishes_group_iid
            elif isinstance(cart_item.item, Drink):
                parent_iid = drinks_group_iid
            else:
                raise TypeError(f"Unknown item type: {type(cart_item.item)}")
            item_iid = f"item_{i}"
            cart_row_items[item_iid] = cart_item.item
            cart_display.insert(
                parent_iid,
                "end",
                iid=item_iid,
                text=cart_item.item.name,
                values=(
                    cart_item.quantity,
                    f"${cart_item.item.price_without_tax:.2f}",
                    f"${cart_item.total_price_without_tax():.2f}",
                ),
            )

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

            # make the image a rounded rectangle, because it looks nicer
            # docs: https://pc-pillow.readthedocs.io/en/latest/ImageDraw/ImageDraw_rounded_rectangle.html
            mask_image = Image.new("L", image.size, 0)
            mask_draw = ImageDraw.Draw(mask_image)
            mask_draw.rounded_rectangle(
                [(0, 0), (image.size[0], image.size[1])],
                radius=25,
                fill="white",
                outline=None,
                width=100,
            )
            image.putalpha(
                mask_image
            )  # fill has 00 transparency, outside has FF transparency

            return ImageTk.PhotoImage(image)

        frame = Frame(parent)

        for i, item in enumerate(items):
            row = (i // width) + 1
            # wrap over if we already have $(width) in the current row
            col = i % width
            # Yes, we are using unstyled tkinter button.
            # Ttk/themed tkinter button does not allow us to change the width/height,
            # at least on macOS.
            item_frame = Frame(frame)

            # have to set it twice for some reason, otherwise the image won't show up :/
            image = load_item_image(item)
            image_label = TkLabel(item_frame, image=image)
            image_label.image = image
            image_label.grid(row=0, column=0, padx=5, pady=5)

            # bg and activebg do not work on macOS TkButton,
            # and TtkButton does not allow us to change the width/height...
            item_button = TkButton(
                item_frame,
                width=20,
                height=3,
                text=str(item),
                font=data.style.lookup(
                    "TButton", "font"
                ),  # need to manually grab TTk style because this is Tk object
                command=lambda item=item: add_to_cart(item),
            )
            item_button.grid(row=0, column=1, padx=5, pady=5)
            item_frame.grid(row=row, column=col, padx=5, pady=5)

        return frame

    def render_items_page() -> None:
        nonlocal current_page
        for child in item_grid_frame.winfo_children():
            child.destroy()

        total_pages = max(1, (len(items) + items_per_page - 1) // items_per_page)
        current_page = max(0, min(current_page, total_pages - 1))
        start_index = current_page * items_per_page
        end_index = start_index + items_per_page
        current_items = items[start_index:end_index]

        get_items_frame(item_grid_frame, 2, current_items).grid(
            row=0, column=0, padx=10, pady=10
        )

        # don't show page buttons if there is only one page
        if total_pages > 1:
            pagination_frame.grid(row=2, column=0, padx=10, pady=(0, 10))
            page_label.config(text=f"Page {current_page + 1} / {total_pages}")
            # disable buttons if we can't move backwards/forwards.
            if current_page == 0:
                previous_page_button.state(["disabled"])
            else:
                previous_page_button.state(["!disabled"])
            if current_page >= total_pages - 1:
                next_page_button.state(["disabled"])
            else:
                next_page_button.state(["!disabled"])
        else:
            pagination_frame.grid_remove()

    def go_to_previous_page() -> None:
        nonlocal current_page
        current_page -= 1
        render_items_page()

    def go_to_next_page() -> None:
        nonlocal current_page
        current_page += 1
        render_items_page()

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

    Label(
        frame,
        text=f"""Ordering at {data.name}!
Select an item below to add it to your cart.
Select an item in your cart (right side) to remove 1x of it from the cart.""",
    ).grid(row=0, column=0, columnspan=5)

    item_grid_frame = Frame(frame)
    item_grid_frame.grid(row=1, column=0, padx=10, pady=10)

    pagination_frame = Frame(frame)
    previous_page_button = TtkButton(
        pagination_frame, text="Previous", command=go_to_previous_page
    )
    previous_page_button.pack(side="left", padx=5)
    page_label = Label(pagination_frame, text="")
    page_label.pack(side="left", padx=5)
    next_page_button = TtkButton(pagination_frame, text="Next", command=go_to_next_page)
    next_page_button.pack(side="left", padx=5)

    # Filtering items
    filter_button_frames = Frame(frame)
    # All dishes
    TtkButton(
        filter_button_frames,
        text="Dishes",
        command=lambda: update_ordering_tab(root, DISHES),
    ).pack()
    # All drinks
    TtkButton(
        filter_button_frames,
        text="Drinks",
        command=lambda: update_ordering_tab(root, DRINKS),
    ).pack()
    # All items
    TtkButton(
        filter_button_frames,
        text="All Items",
        command=lambda: update_ordering_tab(root, ITEMS),
    ).pack()

    filter_button_frames.grid(row=1, column=1, padx=10, pady=10)
    checkout_button = TtkButton(
        frame, text="Checkout", command=lambda: ask_go_to_checkout()
    )
    checkout_button.grid(row=4, column=1, padx=10, pady=10)
    cart_display.grid(row=1, column=2, rowspan=4, padx=5, pady=10, sticky="ns")
    cart_display.bind("<<TreeviewSelect>>", remove_selected_item_from_cart)

    # Build cart display
    # At this point, cart may be undefined.
    try:
        cart_to_use = cart
    except NameError:
        # This dummy cart is used to build the initial cart display,
        # which will be updated using the proper cart once the user enters their name.
        cart_to_use = Cart("")
    update_cart_display(cart_to_use)
    render_items_page()

    return Tab(frame)


def update_ordering_tab(root: Tk, items: list[Item]) -> None:
    tabs[0] = get_ordering_tab(root, items)
    tabs[0].show()
    # we need to repaint UI at this point otherwise
    # the rest of the UI will not be visible until user moves their mouse
    root.update_idletasks()


if __name__ == "__main__":
    main()
