import random
from tkinter import *
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from tkinter import filedialog
from tkinter import messagebox
#import tkinter as tk
from PIL import Image, ImageTk
import pymupdf

buttondict = {
    "Oracle":13,
    "Rumour":14,
    "Twists":15,
    "Names":16,
    "Bestiary":19,
    "Action":45,
    "Items":46
}

#Function to roll an N-sided die and report result
def rolldice(dicelist):
    alloutcomes = {}
    for sides,num in dicelist.items():
        outcomes = []
        for i in range(num):
            outcomes.append(random.randint(1,sides))
        alloutcomes[sides] = outcomes
    return(alloutcomes)

#Function to draw a card from a deck, subsetting options, replacement options
class Deck:
    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
    jokers = ['Black Joker', 'Red Joker']

    def __init__(self, include_jokers=False):
        self.include_jokers = include_jokers
        self._create_deck()
        self.drawn_cards = []

    def _create_deck(self):
        self.deck = [f"{rank} of {suit}" for suit in self.suits for rank in self.ranks]
        if self.include_jokers:
            self.deck.extend(self.jokers)
        random.shuffle(self.deck)

    def get_deck(self):
        """Return all cards currently in the deck (not drawn)."""
        return list(self.deck)

    def get_drawn_cards(self):
        """Return all cards that have been drawn."""
        return list(self.drawn_cards)

    def draw(self, n=1, suit=None):
        """Draw n random cards, optionally specifying a suit."""
        available_cards = self.deck if suit is None else [card for card in self.deck if suit in card]
        if n > len(available_cards):
            raise ValueError("Not enough cards available to draw.")
        drawn = random.sample(available_cards, n)
        for card in drawn:
            self.deck.remove(card)
            self.drawn_cards.append(card)
        return drawn

    def reshuffle(self):
        """Return all drawn cards to the deck and reshuffle."""
        self.deck.extend(self.drawn_cards)
        self.drawn_cards.clear()
        random.shuffle(self.deck)

    def return_to_deck(self, cards):
        """Return specific drawn cards to the deck."""
        for card in cards:
            if card not in self.drawn_cards:
                raise ValueError(f"Card '{card}' was not drawn from the deck.")
            self.drawn_cards.remove(card)
            self.deck.append(card)
        random.shuffle(self.deck)

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Playspace")
        self.root.state("zoomed")  # Maximize window
        self.deck = Deck()
        self.dsides = StringVar()
        self.suit = StringVar()
        self.dnumb = StringVar()
        self.page_buttons = buttondict

        # Configure grid layout
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_rowconfigure(1, weight=1)

        # Top-left and top-right: Button areas
        self.text_buttons_frame = self.create_scrollable_button_frame(root)
        self.text_buttons_frame.grid(row=0, column=0, sticky="nsew")

        self.pdf_buttons_frame = self.create_scrollable_button_frame(root)
        self.pdf_buttons_frame.grid(row=0, column=1, sticky="nsew")

        # Add buttons
        btn_load_notes = Button(self.text_buttons_frame.scrollable_inner, text="Load", command=self.load_notes)
        btn_load_notes.pack(side="left", padx=5, pady=5)

        btn_save_notes = Button(self.text_buttons_frame.scrollable_inner, text="Save", command=self.save_notes)
        btn_save_notes.pack(side="left", padx=5, pady=5)

        #btn_clear_notes = Button(self.text_buttons_frame.scrollable_inner, text="Clear Notes", command=self.clear_notes)
        #btn_clear_notes.pack(side="left", padx=5)

        entry_die_numb = ttk.Combobox(self.text_buttons_frame.scrollable_inner, textvariable=self.dnumb, width=2)
        entry_die_numb['values'] = ('1','2','3','4')
        entry_die_numb.pack(side="left", padx=(5,0))

        entry_die_sides = ttk.Combobox(self.text_buttons_frame.scrollable_inner, textvariable=self.dsides, width=3)
        entry_die_sides['values'] = ('4','6','8','10','12','20','100')
        entry_die_sides.pack(side="left", padx=(1,0))

        btn_roll_die = Button(self.text_buttons_frame.scrollable_inner, text="Roll Dice", command=self.roll_dice)
        btn_roll_die.pack(side="left", padx=(1,5))

        entry_suit = ttk.Combobox(self.text_buttons_frame.scrollable_inner, textvariable=self.suit, width=10)
        entry_suit['values'] = ('Clubs','Diamonds','Hearts','Spades','Any')
        entry_suit.pack(side="left", padx=(5,1))

        btn_draw_card = Button(self.text_buttons_frame.scrollable_inner, text="Draw Card", command=self.draw_card)
        btn_draw_card.pack(side="left", padx=5)

        btn_return_card = Button(self.text_buttons_frame.scrollable_inner, text="Return Card", command=self.return_card)
        btn_return_card.pack(side="left", padx=5)

        btn_shuffle = Button(self.text_buttons_frame.scrollable_inner, text="Shuffle", command=self.shuffle)
        btn_shuffle.pack(side="left", padx=5)

        btn_add_img = Button(self.text_buttons_frame.scrollable_inner, text="Add Image", command=self.add_image)
        btn_add_img.pack(side="left", padx=5)

        btn_pdf_next = Button(self.pdf_buttons_frame.scrollable_inner, text="<", command=self.prev_page)
        btn_pdf_next.pack(side='left', padx=5, pady=5)

        btn_open_pdf = Button(self.pdf_buttons_frame.scrollable_inner, text="Open PDF", command=self.load_pdf)
        btn_open_pdf.pack(side='left', padx=5)

        btn_pdf_next = Button(self.pdf_buttons_frame.scrollable_inner, text=">", command=self.next_page)
        btn_pdf_next.pack(side='right', padx=5)

        # Bottom-left: Notepad
        self.text_area = ScrolledText(root, wrap="word", font=("Consolas", 12), height = 1, width = 1)
        self.text_area.grid(row=1, column=0, sticky="nsew")

        # Bottom-right: PDF viewer
        self.pdf_frame = Frame(root)
        self.pdf_frame.grid(row=1, column=1, sticky="nsew")
        self.pdf_frame.grid_rowconfigure(0, weight=1)
        self.pdf_frame.grid_columnconfigure(0, weight=1)
        self.canvas = Canvas(self.pdf_frame, bg="white")
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # PDF state
        self.pdf_doc = None
        self.current_page = 0
        self.pdf_image = None

        self.add_page_buttons()

    #Adds all the buttons from the dictionary
    def add_page_buttons(self):
        for text, page in self.page_buttons.items():
            Button(self.pdf_buttons_frame.scrollable_inner, text=text, command=lambda p=page-1: self.set_pdf_page(p)).pack(side="left", padx=5, pady=5)

    #I don't have a better solution for the frame, tried to implement some wrapping but ended up with ugly scroll bars, defines the top frames
    def create_scrollable_button_frame(self, parent):
        container = Frame(parent)
        canvas = Canvas(container, height=60)
        x_scroll = Scrollbar(container, orient="horizontal", command=canvas.xview)
        y_scroll = Scrollbar(container, orient="vertical", command=canvas.yview)

        scrollable_frame = Frame(canvas)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set)

        canvas.pack(side="left", fill="both", expand=True)
        y_scroll.pack(side="right", fill="y")
        x_scroll.pack(side="bottom", fill="x")

        container.scrollable_inner = scrollable_frame
        return container

    def load_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            try:
                self.pdf_doc = pymupdf.open(file_path)
                self.current_page = 0
                self.render_pdf_page()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load PDF:\n{e}")

    def set_pdf_page(self,page):
        self.current_page = page
        self.render_pdf_page()

    def render_pdf_page(self):
        if not self.pdf_doc:
            return
        try:
            page = self.pdf_doc.load_page(self.current_page)
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            canvas_width = self.canvas.winfo_width() or 800
            canvas_height = self.canvas.winfo_height() or 600
            img = img.resize((canvas_width, canvas_height))
            self.pdf_image = ImageTk.PhotoImage(img)
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor="nw", image=self.pdf_image)
        except Exception as e:
            messagebox.showerror("Error", f"Could not render page:\n{e}")

    def next_page(self):
        if self.pdf_doc and self.current_page < len(self.pdf_doc) - 1:
            self.current_page += 1
            self.render_pdf_page()

    def prev_page(self):
        if self.pdf_doc and self.current_page > 0:
            self.current_page -= 1
            self.render_pdf_page()

    def save_notes(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(self.text_area.get("1.0", "end-1c"))
                messagebox.showinfo("Saved", "Notes saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save notes:\n{e}")

    def clear_notes(self):
        self.text_area.delete("1.0", END)

    def roll_dice(self):
        sides = int(self.dsides.get())
        dnumber = int(self.dnumb.get())
        input = {sides:dnumber}
        output = rolldice(input)[sides]
        if dnumber == 1:
            self.text_area.insert(END, '\nYou rolled a d' + str(sides) + ' and got a ' + str(output)[1:-1] + '.')
        else:
            self.text_area.insert(END, '\nYou rolled ' + str(dnumber)+' d' + str(sides) + 's and got ' + str(output)[1:-1] + '.')
        
    def draw_card(self):
        suit = self.suit.get()
        if suit == 'Any':
            suit = None
        drawn = self.deck.draw(suit=suit)[0]
        self.text_area.insert(END, '\nYou drew the ' + drawn + '.')

    def return_card(self):
        prev_drawn_card = self.deck.drawn_cards[-1]
        self.deck.return_to_deck([prev_drawn_card])
        self.text_area.insert(END, '\nYou returned the ' + prev_drawn_card + ' to the deck.')

    def shuffle(self):
        self.deck.reshuffle()
        self.text_area.insert(END, '\nDeck shuffled')

    def add_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            #img = Image.open(file_path)
            self.tkimg = PhotoImage(file=file_path)
            #lbimg = Label(self.root,image=tkimg)
            self.text_area.image_create(END,image=self.tkimg)

    def load_notes(self):
        self.clear_notes()
        file_path = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    toin = f.read()
                    self.text_area.insert(END, toin)
            except Exception as e:
                messagebox.showerror("Error", f"Could not render page:\n{e}")

if __name__ == "__main__":
    root = Tk()
    app = App(root)
    root.mainloop()
