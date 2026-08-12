"""Takeaway system GUI."""
from takeaway import Item

from tkinter import Tk
from tkinter.ttk import Button, Label, Entry, Frame
import tkinter.messagebox as messagebox

from takeaway.cart import Cart
from takeaway.dishes import ITEMS

cart: Cart
frames: list[Frame] = []

def main() -> None:
    root = Tk()
    root.title("Takeaway Ordering System")

    greet_frame = get_greet_frame(root)
    frames.append(greet_frame)
    frames.append(get_ordering_frame(root))

    greet_frame.tkraise()
    root.mainloop()


def switch_frames(index: int) -> None:
    frames[index].tkraise()

def get_greet_frame(root: Tk) -> Frame:
    frame = Frame(root)
    frame.grid(row=0, column=0, sticky="nsew")

    Label(frame, text="Welcome to the Takeaway Ordering System!").grid(
        row=0, column=0, columnspan=2
    )
    Label(frame, text="Please enter your name:").grid(row=1, column=0)
    name_entry = Entry(frame)
    name_entry.grid(row=1, column=1)

    def start_ordering() -> None:
        name = name_entry.get().strip()
        if name == "":
            messagebox.showerror("Invalid name", "Name cannot be empty.")
            return

        # valid input: create cart and switch to ordering frame
        global cart
        cart = Cart(name)
        switch_frames(1) # TODO: this is terrible


    Button(frame, text="Start ordering", command=start_ordering).grid(
        row=2, column=0, columnspan=2
    )

    return frame

def get_ordering_frame(root: Tk) -> Frame:
    def add_to_cart(item: Item) -> None:
        pass

    frame = Frame(root)
    frame.grid(row=0, column=0, sticky="nsew")

    Label(frame, text="Takeaway Ordering System!").grid(
        row=0, column=0, columnspan=5
    )

    # Show all items in a 5x5 grid
    for i, item in enumerate(ITEMS):
        row = (i // 5) + 1
        col = i % 5
        Button(frame, text=str(item), command=lambda item=item: add_to_cart(item)).grid(
            row=row, column=col, width=10, height=10, padx=5, pady=5
        )

    return frame

if __name__ == "__main__":
    main()
