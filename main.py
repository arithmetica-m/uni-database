import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path


# DATABASE SETUP
DB_PATH = Path(__file__).with_name("universities1.db")
connection = sqlite3.connect(DB_PATH)
connection.execute("PRAGMA foreign_keys = ON")

connection.executescript("""
CREATE TABLE IF NOT EXISTS City (
    city_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    country TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS University (
    university_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    city_id INTEGER NOT NULL,
    FOREIGN KEY (city_id) REFERENCES City(city_id)
);

CREATE TABLE IF NOT EXISTS Course (
    course_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    university_id INTEGER NOT NULL,
    language TEXT NOT NULL,
    FOREIGN KEY (university_id) REFERENCES University(university_id)
);
""")


connection.commit()

# IDs in the same order as the universities displayed in the list.
university_ids = []


# FUNCTIONS
def get_selected_id(combobox):
    """Extract the ID from a choice such as '3: Munich'."""
    return int(combobox.get().split(":")[0])


def refresh():
    """Read the database and update the lists and dropdowns."""
    city_list.delete(0, tk.END)
    university_list.delete(0, tk.END)
    course_list.delete(0, tk.END)
    university_ids.clear()

    cities = connection.execute("""
        SELECT city_id, name, country
        FROM City
        ORDER BY name, city_id
    """).fetchall()

    city_choices = []
    for city_id, name, country in cities:
        city_list.insert(tk.END, f"{name}, {country}")
        city_choices.append(f"{city_id}: {name}")

    city_dropdown["values"] = city_choices
    if city_dropdown.get() not in city_choices:
        city_dropdown.set("")

    universities = connection.execute("""
        SELECT University.university_id, University.name, City.name
        FROM University
        JOIN City ON University.city_id = City.city_id
        ORDER BY University.name, University.university_id
    """).fetchall()

    university_choices = []
    for university_id, name, city in universities:
        university_ids.append(university_id)
        university_list.insert(tk.END, f"{name} — {city}")
        university_choices.append(f"{university_id}: {name}")

    university_dropdown["values"] = university_choices
    if university_dropdown.get() not in university_choices:
        university_dropdown.set("")

    courses = connection.execute("""
        SELECT Course.name, University.name, Course.language
        FROM Course
        JOIN University
            ON Course.university_id = University.university_id
        ORDER BY Course.name, Course.course_id
    """).fetchall()

    for name, university, language in courses:
        course_list.insert(
            tk.END, f"{name} — {university} — {language}"
        )
def add_city():
    name = city_name.get().strip()
    country = country_name.get().strip()

    if not name or not country:
        messagebox.showwarning(
            "Missing information", "Enter a city and country."
        )
        return

    connection.execute(
        "INSERT INTO City (name, country) VALUES (?, ?)",
        (name, country)
    )
    connection.commit()

    city_name.delete(0, tk.END)
    country_name.delete(0, tk.END)
    refresh()


def add_university():
    name = university_name.get().strip()

    if not name or not city_dropdown.get():
        messagebox.showwarning(
            "Missing information", "Enter a name and choose a city."
        )
        return

    city_id = get_selected_id(city_dropdown)

    connection.execute(
        "INSERT INTO University (name, city_id) VALUES (?, ?)",
        (name, city_id)
    )
    connection.commit()

    university_name.delete(0, tk.END)
    refresh()


def add_course():
    name = course_name.get().strip()
    language = language_name.get().strip()

    if not name or not language or not university_dropdown.get():
        messagebox.showwarning(
            "Missing information", "Enter a name, language and choose a university."
        )
        return


    university_id = get_selected_id(university_dropdown)

    connection.execute(
        "INSERT INTO Course (name, university_id, language) VALUES (?, ?, ?)",
        (name, university_id, language)
    )
    connection.commit()

    course_name.delete(0, tk.END)
    language_name.delete(0, tk.END)
    refresh()


def delete_university():
    selected = university_list.curselection()

    if not selected:
        messagebox.showwarning(
            "No selection", "Select a university from the list."
        )
        return

    university_id = university_ids[selected[0]]

    try:
        connection.execute(
            "DELETE FROM University WHERE university_id = ?",
            (university_id,)
        )
        connection.commit()
    except sqlite3.IntegrityError:
        connection.rollback()
        messagebox.showwarning(
            "Cannot delete",
            "This university has courses. Delete its courses first."
        )
        return

    refresh()


def close_app():
    connection.close()
    root.destroy()


# WINDOW SETUP
root = tk.Tk()
root.title("University Database")
root.geometry("600x500")
root.protocol("WM_DELETE_WINDOW", close_app)

tabs = ttk.Notebook(root)
tabs.pack(fill="both", expand=True, padx=10, pady=10)

city_tab = ttk.Frame(tabs, padding=15)
university_tab = ttk.Frame(tabs, padding=15)
course_tab = ttk.Frame(tabs, padding=15)

tabs.add(city_tab, text="Cities")
tabs.add(university_tab, text="Universities")
tabs.add(course_tab, text="Courses")


# CITY TAB
ttk.Label(city_tab, text="City name").pack(anchor="w")
city_name = ttk.Entry(city_tab)
city_name.pack(fill="x")

ttk.Label(city_tab, text="Country").pack(anchor="w", pady=(10, 0))
country_name = ttk.Entry(city_tab)
country_name.pack(fill="x")

ttk.Button(
    city_tab, text="Add city", command=add_city
).pack(pady=10)

city_list = tk.Listbox(city_tab)
city_list.pack(fill="both", expand=True)


# UNIVERSITY TAB
ttk.Label(university_tab, text="University name").pack(anchor="w")
university_name = ttk.Entry(university_tab)
university_name.pack(fill="x")

ttk.Label(university_tab, text="City").pack(anchor="w", pady=(10, 0))
city_dropdown = ttk.Combobox(university_tab, state="readonly")
city_dropdown.pack(fill="x")

ttk.Button(
    university_tab, text="Add university", command=add_university
).pack(pady=10)

ttk.Button(
    university_tab,
    text="Delete selected university",
    command=delete_university
).pack(pady=(0, 10))

university_list = tk.Listbox(university_tab, exportselection=False)
university_list.pack(fill="both", expand=True)


# COURSE TAB
ttk.Label(course_tab, text="Course name").pack(anchor="w")
course_name = ttk.Entry(course_tab)
course_name.pack(fill="x")

ttk.Label(
    course_tab, text="Language of instruction"
).pack(anchor="w", pady=(10, 0))

language_name = ttk.Entry(course_tab)
language_name.pack(fill="x")

ttk.Label(
    course_tab, text="University"
).pack(anchor="w", pady=(10, 0))

university_dropdown = ttk.Combobox(course_tab, state="readonly")
university_dropdown.pack(fill="x")

ttk.Button(
    course_tab, text="Add course", command=add_course
).pack(pady=10)

course_list = tk.Listbox(course_tab)
course_list.pack(fill="both", expand=True)


# START THE APP
refresh()
root.mainloop()