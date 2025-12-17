import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import requests
from io import StringIO

CSV_URL = "https://datos.madrid.es/egob/catalogo/211549-1-juegos-deportivos-actual.csv"
TARGET_COMPETITION = "8979"
TARGET_GROUP = "29514"

def load_and_filter():
    try:
        resp = requests.get(CSV_URL)
        resp.raise_for_status()
    except Exception as e:
        messagebox.showerror("Error", f"Could not download CSV:\n{e}")
        return

    # parse CSV
    data = pd.read_csv(StringIO(resp.text), sep=";", encoding="UTF-8", dtype=str)
    print(data.columns)
    print(data.head())

    # filter
    df = data[(data["Codigo_competicion"].str.strip() == TARGET_COMPETITION) & (data["Codigo_grupo"].str.strip() == TARGET_GROUP)
              ].copy()
    print(df.columns)
    print(df.head())
    if df.empty:
        messagebox.showinfo("No data", f"No rows with Codigo_competicion={TARGET_COMPETITION}")
        return

    # sort by position (if numeric)
    df["Posicion"] = pd.to_numeric(df["Posicion"], errors="ignore")
    df["Puntos"] = pd.to_numeric(df["Puntos"], errors="ignore", downcast="integer")
    df.sort_values("Posicion", inplace=True)

    # clear previous
    for r in tree.get_children():
        tree.delete(r)

    # insert rows
    for _, row in df.iterrows():
        tree.insert("", "end", values=(
            row["Posicion"],
            row["Nombre_equipo"],
            row["Puntos"],
            row["Partidos_ganados"],
            row["Partidos_empatados"],
            row["Partidos_perdidos"],
            row["Goles_favor"],
            row["Goles_contra"],
        ))

# build UI
root = tk.Tk()
root.title(f"Clasificación - Competición {TARGET_COMPETITION} ({TARGET_GROUP})")
# root.geometry("800x400") # Old fixed size
root.geometry("600x400")  # New smaller size

# table
cols = [
    "Posición",
    "Equipo",
    "Puntos",
    "G",
    "E",
    "P",
    "GF",
    "GC",
]
tree = ttk.Treeview(root, columns=cols, show="headings")
for c in cols:
    tree.heading(c, text=c)
    tree.column(c, width=60, anchor="center", stretch=False)
    tree.column("Equipo", width=130, anchor="w")

    for c in ["G", "E", "P", "GF", "GC"]:
        tree.column(c, width=40, anchor="center", stretch=False)

tree.pack(fill="both", expand=True)

# load button
btn = ttk.Button(root, text="Cargar clasificación", command=load_and_filter)
btn.pack(pady=10)

root.mainloop()
