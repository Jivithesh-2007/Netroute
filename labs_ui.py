"""Module 5: labs_ui.py - Searching, Sorting, and Hash Table UI."""
import tkinter as tk
from tkinter import ttk
from theme import BG_CARD, PRIMARY, SUCCESS, DANGER, FONT_BOLD, FONT_NORMAL, FONT_SMALL
from algorithms import linear_search, binary_search, bubble_sort, selection_sort, insertion_sort, HashTable

class LabsFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG_CARD)
        self.ht = HashTable(size=7)

        s1 = tk.LabelFrame(self, text="Searching & Sorting Lab", bg=BG_CARD, font=FONT_BOLD, padx=6, pady=4)
        s1.pack(fill="x", padx=10, pady=4)
        f1 = tk.Frame(s1, bg=BG_CARD)
        f1.pack(fill="x")
        tk.Label(f1, text="Array:", bg=BG_CARD, font=FONT_SMALL).pack(side="left")
        self.arr_entry = tk.Entry(f1, width=20, font=FONT_NORMAL)
        self.arr_entry.insert(0, "45, 12, 89, 34, 23, 7")
        self.arr_entry.pack(side="left", padx=4)

        tk.Label(f1, text="Target:", bg=BG_CARD, font=FONT_SMALL).pack(side="left", padx=(6, 0))
        self.tgt_entry = tk.Entry(f1, width=5, font=FONT_NORMAL)
        self.tgt_entry.insert(0, "34")
        self.tgt_entry.pack(side="left", padx=4)

        self.alg_choice = ttk.Combobox(f1, values=["Linear Search", "Binary Search", "Bubble Sort", "Selection Sort", "Insertion Sort"], width=13, state="readonly")
        self.alg_choice.set("Bubble Sort")
        self.alg_choice.pack(side="left", padx=4)
        tk.Button(f1, text="Run", bg=PRIMARY, fg="white", font=FONT_SMALL, command=self.run_algo).pack(side="left", padx=4)
        self.algo_res = tk.Label(s1, text="Result will appear here.", bg=BG_CARD, font=FONT_NORMAL, fg=PRIMARY)
        self.algo_res.pack(anchor="w", pady=(2, 0))

        s2 = tk.LabelFrame(self, text="Hash Table Lab (Separate Chaining - Size 7)", bg=BG_CARD, font=FONT_BOLD, padx=6, pady=4)
        s2.pack(fill="both", expand=True, padx=10, pady=4)
        f2 = tk.Frame(s2, bg=BG_CARD)
        f2.pack(fill="x")
        tk.Label(f2, text="Key:", bg=BG_CARD, font=FONT_SMALL).pack(side="left")
        self.key_entry = tk.Entry(f2, width=6, font=FONT_NORMAL)
        self.key_entry.pack(side="left", padx=4)
        tk.Button(f2, text="Insert", bg=PRIMARY, fg="white", font=FONT_SMALL, command=lambda: self.ht_action("insert")).pack(side="left", padx=2)
        tk.Button(f2, text="Search", bg=SUCCESS, fg="white", font=FONT_SMALL, command=lambda: self.ht_action("search")).pack(side="left", padx=2)
        tk.Button(f2, text="Delete", bg=DANGER, fg="white", font=FONT_SMALL, command=lambda: self.ht_action("delete")).pack(side="left", padx=2)
        self.ht_status = tk.Label(s2, text="Ready", bg=BG_CARD, font=FONT_NORMAL, fg=PRIMARY)
        self.ht_status.pack(anchor="w", pady=(2, 2))

        self.bucket_list = tk.Listbox(s2, font=FONT_NORMAL, height=7)
        self.bucket_list.pack(fill="both", expand=True, pady=2)
        for k in [10, 24, 15, 31, 8]: self.ht.insert(k)
        self.refresh_ht()

    def run_algo(self):
        try:
            arr = [int(x.strip()) for x in self.arr_entry.get().split(",") if x.strip()]
            c = self.alg_choice.get()
            if "Search" in c:
                t = int(self.tgt_entry.get().strip())
                if c == "Binary Search":
                    arr.sort()
                    idx, s = binary_search(arr, t)
                    self.algo_res.config(text=f"Binary Search on sorted {arr}: Index={idx}, Steps={s}")
                else:
                    idx, s = linear_search(arr, t)
                    self.algo_res.config(text=f"Linear Search: Target={t}, Index={idx}, Comparisons={s}")
            else:
                fn = bubble_sort if c == "Bubble Sort" else (selection_sort if c == "Selection Sort" else insertion_sort)
                res, s = fn(arr)
                self.algo_res.config(text=f"{c} Output: {res} (Steps/Comparisons: {s})")
        except Exception as e: self.algo_res.config(text=f"Error: {e}")

    def ht_action(self, action):
        v = self.key_entry.get().strip()
        if not v.lstrip('-').isdigit():
            self.ht_status.config(text="Enter integer key"); return
        k = int(v)
        fn = getattr(self.ht, action)
        _, msg = fn(k)
        self.ht_status.config(text=msg)
        if action != "search": self.refresh_ht()

    def refresh_ht(self):
        self.bucket_list.delete(0, tk.END)
        for i, b in enumerate(self.ht.buckets):
            self.bucket_list.insert(tk.END, f"Bucket [{i}] (hash {i}) -> {b}")
