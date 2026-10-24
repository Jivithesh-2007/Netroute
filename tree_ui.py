"""Module 4: tree_ui.py - Binary Search Tree (BST) Logic & Visualization."""
import tkinter as tk
from theme import BG_CARD, PRIMARY, SUCCESS, TEXT_DARK, FONT_BOLD, FONT_NORMAL, FONT_SMALL

class BSTNode:
    def __init__(self, val):
        self.val, self.left, self.right = val, None, None

class BST:
    def __init__(self):
        self.root = None

    def insert(self, val):
        if not self.root:
            self.root = BSTNode(val)
            return True
        c = self.root
        while True:
            if val == c.val: return False
            if val < c.val:
                if not c.left: c.left = BSTNode(val); return True
                c = c.left
            else:
                if not c.right: c.right = BSTNode(val); return True
                c = c.right

    def search(self, val):
        c = self.root
        while c:
            if val == c.val: return True
            c = c.left if val < c.val else c.right
        return False

    def traversals(self):
        ino, pre, post = [], [], []
        def _trav(n):
            if not n: return
            pre.append(n.val); _trav(n.left); ino.append(n.val); _trav(n.right); post.append(n.val)
        _trav(self.root)
        return ino, pre, post

class TreeFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG_CARD)
        self.bst = BST()
        ctrl = tk.Frame(self, bg=BG_CARD)
        ctrl.pack(fill="x", padx=10, pady=5)
        tk.Label(ctrl, text="Node Value:", bg=BG_CARD, font=FONT_BOLD).pack(side="left")
        self.val_entry = tk.Entry(ctrl, width=6, font=FONT_NORMAL)
        self.val_entry.pack(side="left", padx=4)
        tk.Button(ctrl, text="Insert", bg=PRIMARY, fg="white", font=FONT_SMALL, command=self.on_insert).pack(side="left", padx=2)
        tk.Button(ctrl, text="Search", bg=SUCCESS, fg="white", font=FONT_SMALL, command=self.on_search).pack(side="left", padx=2)
        tk.Button(ctrl, text="Clear", bg="#64748B", fg="white", font=FONT_SMALL, command=self.on_clear).pack(side="left", padx=2)
        self.status = tk.Label(ctrl, text="Ready", bg=BG_CARD, fg=PRIMARY, font=FONT_NORMAL)
        self.status.pack(side="left", padx=6)

        self.trav_lbl = tk.Label(self, text="", bg=BG_CARD, font=FONT_SMALL, fg=TEXT_DARK)
        self.trav_lbl.pack(fill="x", padx=10, pady=2)
        self.canvas = tk.Canvas(self, bg="#F8FAFC", height=320, highlightthickness=1, highlightbackground="#CBD5E1")
        self.canvas.pack(fill="both", expand=True, padx=10, pady=4)
        for v in [50, 30, 70, 20, 40, 60, 80]: self.bst.insert(v)
        self.draw_tree()

    def on_insert(self):
        v = self.val_entry.get().strip()
        if v.lstrip('-').isdigit():
            ok = self.bst.insert(int(v))
            self.status.config(text=f"Inserted {v}" if ok else f"{v} exists")
            self.draw_tree()

    def on_search(self):
        v = self.val_entry.get().strip()
        if v.lstrip('-').isdigit():
            found = self.bst.search(int(v))
            self.status.config(text=f"Key {v} found!" if found else f"Key {v} not found")

    def on_clear(self):
        self.bst = BST()
        self.draw_tree()
        self.status.config(text="Tree cleared")

    def draw_tree(self):
        self.canvas.delete("all")
        ino, pre, post = self.bst.traversals()
        self.trav_lbl.config(text=f"Inorder: {ino} | Preorder: {pre} | Postorder: {post}")
        def _draw(n, x, y, dx):
            if not n: return
            if n.left:
                self.canvas.create_line(x, y, x - dx, y + 45, fill="#94A3B8", width=2)
                _draw(n.left, x - dx, y + 45, max(dx // 2, 20))
            if n.right:
                self.canvas.create_line(x, y, x + dx, y + 45, fill="#94A3B8", width=2)
                _draw(n.right, x + dx, y + 45, max(dx // 2, 20))
            self.canvas.create_oval(x-14, y-14, x+14, y+14, fill="#3B82F6", outline="#1D4ED8", width=2)
            self.canvas.create_text(x, y, text=str(n.val), fill="white", font=FONT_BOLD)
        _draw(self.bst.root, 340, 25, 140)
