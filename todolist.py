import tkinter as tk
from tkinter import ttk
import json
from pathlib import Path

# Fișier pentru salvarea datelor
SAVE_FILE = Path("weekly_planner.json")

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
colors = {
    "Monday": "#FFB6C1", "Tuesday": "#FFDAB9", "Wednesday": "#FFFFE0",
    "Thursday": "#CCCCCC", "Friday": "#D8BFD8", "Saturday": "#B0E0E6",
    "Sunday": "#99FFCC", "Notes": "#FFFACD"
}

# Funcții pentru salvarea și încărcarea datelor
def load_data():
    if SAVE_FILE.exists():
        with open(SAVE_FILE, "r") as file:
            return json.load(file)
    return {day: [] for day in days + ["Notes"]}

def save_data():
    for day in days:
        data[day] = [{"task": entry.get().strip(), "completed": var.get(), "color": entry.cget("fg")}
                     for entry, var in task_widgets[day] if entry.winfo_exists()]
    data["Notes"] = notes_text.get("1.0", tk.END).strip()
    with open(SAVE_FILE, "w") as file:
        json.dump(data, file)

def add_task(day):
    # Adăugăm un task nou, cu valori implicite
    data[day].append({"task": "", "completed": False, "color": "black"})
    update_task_list(day)
    save_data()  # Salvare automata

def clear_all_tasks(day):
    data[day] = []
    update_task_list(day)
    save_data()  # Salvare automata

def update_task_list(day):
    # Ștergem widget-urile vechi
    for widget in task_frames[day].winfo_children():
        widget.destroy()
    task_widgets[day] = []

    # Re-creăm widget-urile pentru fiecare task
    for idx, task in enumerate(data[day]):
        frame = tk.Frame(task_frames[day], bg=colors[day])
        frame.pack(fill="x", pady=2)

        var = tk.BooleanVar(value=task.get("completed", False))

        # Checkbox pentru completare
        def on_checkbox_change(*args):
            save_data()  # Salvăm automat la schimbarea stării

        var.trace_add("write", on_checkbox_change)

        tk.Checkbutton(frame, variable=var, bg=colors[day]).pack(side="left", padx=5)

        # Casetă de text
        entry = tk.Entry(frame, font=("Arial", 12), width=22, fg=task.get("color", "black"))
        entry.insert(0, task.get("task", ""))  # Textul task-ului
        entry.pack(side="left", padx=5)

        # Salvăm automat când textul din Entry se modifică
        def on_text_change(event):
            save_data()

        entry.bind("<FocusOut>", on_text_change)  # Salvăm când se pierde focusul
        entry.bind("<KeyRelease>", on_text_change)  # Salvăm la fiecare modificare

        # Menú contextual pentru alegerea culorii
        menu = tk.Menu(root, tearoff=0)
        menu.add_command(label="Important (Red)", command=lambda e=entry: set_task_color(e, "red"))
        menu.add_command(label="Medium (Orange)", command=lambda e=entry: set_task_color(e, "orange"))
        menu.add_command(label="Low (Green)", command=lambda e=entry: set_task_color(e, "green"))

        def show_color_menu(event):
            menu.post(event.x_root, event.y_root)

        entry.bind("<Button-3>", show_color_menu)  # Clic dreapta pentru meniu contextual

        # Buton pentru ștergerea unui task specific
        tk.Button(frame, text="X", command=lambda f=frame, i=idx: delete_task(day, f, i),
                  bg="#d9534f", fg="white", font=("Arial", 8)).pack(side="left", padx=5)

        task_widgets[day].append((entry, var))

def set_task_color(entry, color):
    entry.config(fg=color)
    save_data()  # Salvăm automat când se schimbă culoarea

def delete_task(day, frame, index):
    # Ștergem task-ul specific
    if index < len(data[day]):
        del data[day][index]
    frame.destroy()
    update_task_list(day)  # Reactualizăm lista de widget-uri
    save_data()  # Salvăm automat

# Configurare date și interfață grafică
data = load_data()
root = tk.Tk()
root.title("Weekly Planner")
root.geometry("1200x800")
root.config(bg="#2c2c2c")

task_frames = {}
task_widgets = {day: [] for day in days}

# Creare secțiuni zile
for i, day in enumerate(days):
    x_offset = (i % 4) * 290 + 10  # Offset pentru zilele din primul rând
    y_offset = (i // 4) * 260 + 20
    if i >= 4:  # Offset suplimentar pentru centrare în al doilea rând
        x_offset += 145

    frame = tk.Frame(root, bg=colors[day], bd=2, relief="groove")
    frame.place(x=x_offset, y=y_offset, width=280, height=240)

    tk.Label(frame, text=day, font=("Arial", 16, "bold"), bg=colors[day]).pack(pady=5)

    # Container pentru butoane
    button_frame = tk.Frame(frame, bg=colors[day])
    button_frame.pack(pady=5)

    tk.Button(button_frame, text="Add Task", command=lambda d=day: add_task(d),
              bg="#d4a5a5", fg="white", font=("Arial", 10)).pack(side="left", padx=5)
    tk.Button(button_frame, text="Clear All", command=lambda d=day: clear_all_tasks(d),
              bg="#f0ad4e", fg="white", font=("Arial", 10)).pack(side="left", padx=5)

    task_frames[day] = tk.Frame(frame, bg=colors[day])
    task_frames[day].pack(fill="both", expand=True, pady=5)

    update_task_list(day)

# Secțiunea Notes
notes_frame = tk.Frame(root, bg=colors["Notes"], bd=2, relief="groove")
notes_frame.place(x=10, y=540, width=1160, height=200)

tk.Label(notes_frame, text="Notes", font=("Arial", 16, "bold"), bg=colors["Notes"]).pack(pady=5)

notes_text = tk.Text(notes_frame, font=("Arial", 12), height=8, width=110)
notes_text.pack(pady=5)

# Salvăm automat notițele când se modifică
def on_notes_change(event):
    save_data()

notes_text.bind("<FocusOut>", on_notes_change)
notes_text.bind("<KeyRelease>", on_notes_change)
notes_text.insert("1.0", data.get("Notes", ""))

# Rulare aplicație
root.mainloop()
