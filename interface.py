import os
import sys
from tkinter import *
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from aircraft import *
from LEBL import *

try:
    open("Airports.txt", "r").close()
except FileNotFoundError:
    messagebox.showerror("Error", "Airports.txt not found")
    sys.exit(1)

root = Tk()
root.title("Airport Management System")
root.geometry("1450x850")
root.configure(bg="#2a2a3d")

root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=5)

FONT_B = ("Segoe UI", 9, "bold")

bcn = None

# ── Placeholder helper ────────────────────────────────────────────────────
PLACEHOLDER_COLOR = "#888899"
NORMAL_COLOR      = "#ffffff"

def add_placeholder(entry, text):
    entry.insert(0, text)
    entry.config(fg=PLACEHOLDER_COLOR)

    def on_focus_in(e):
        if entry.get() == text:
            entry.delete(0, END)
            entry.config(fg=NORMAL_COLOR)

    def on_focus_out(e):
        if entry.get() == "":
            entry.insert(0, text)
            entry.config(fg=PLACEHOLDER_COLOR)

    entry.bind("<FocusIn>",  on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

def get_value(entry, placeholder):
    v = entry.get()
    return "" if v == placeholder else v

PH_ICAO     = "ICAO code  (e.g. LEBL)"
PH_LAT      = "Latitude   (e.g. N411749)"
PH_LON      = "Longitude  (e.g. E0020442)"
PH_TERMINAL = "Terminal   (e.g. T1)"
PH_AIRLINE  = "Airline ICAO  (e.g. VLG)"
PH_AIRCRAFT = "Aircraft ID   (e.g. ECMKV)"


# ═══════════════════════════════════════════════════════════════════════════
# PLOT / MAP
# ═══════════════════════════════════════════════════════════════════════════

def ShowPlot(fig, right_panel_builder=None):
    for w in frame3.winfo_children():
        w.destroy()

    frame3.rowconfigure(0, weight=1)

    if right_panel_builder:
        frame3.columnconfigure(0, weight=4)
        frame3.columnconfigure(1, weight=1)

        graph_frame = Frame(frame3, bg="#2a2a3d")
        graph_frame.grid(row=0, column=0, sticky="nsew")

        right_frame = Frame(frame3, bg="#222233", width=280)
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.pack_propagate(False)

        right_panel_builder(right_frame, graph_frame)

        if fig is not None:
            canvas = FigureCanvasTkAgg(fig, master=graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
    else:
        frame3.columnconfigure(0, weight=1)
        canvas = FigureCanvasTkAgg(fig, master=frame3)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")


selected_airlines  = []
all_airlines       = []
airline_search_var = None


def OpenAirlineSelector():
    global all_airlines

    # ── NEW: guard against missing arrivals data ──────────────────────────
    try:
        data = LoadArrivals()
    except Exception as e:
        messagebox.showerror("Error", f"Could not load arrivals data:\n{e}")
        return

    if not data:
        messagebox.showwarning("No Data", "No arrivals data found to filter by airline.")
        return

    all_airlines = sorted(list(set([d.company for d in data])))

    win = Toplevel(root)
    win.title("Airline Filter")
    win.geometry("420x520")
    win.configure(bg="#2a2a3d")

    Label(win, text="Search airline:", bg="#2a2a3d", fg="white").pack(pady=5)
    search_var = StringVar()
    Entry(win, textvariable=search_var, width=35).pack()

    listbox = Listbox(win, height=10, width=40)
    listbox.pack(pady=5)

    Label(win, text="Selected airlines:", bg="#2a2a3d", fg="#c084fc").pack()
    selected_box = Listbox(win, height=6, width=40)
    selected_box.pack(pady=5)

    def refresh_available():
        listbox.delete(0, END)
        q = search_var.get().lower()
        for a in all_airlines:
            if q in a.lower():
                listbox.insert(END, a)

    def refresh_selected():
        selected_box.delete(0, END)
        for s in selected_airlines:
            selected_box.insert(END, s)

    def add():
        try:
            val = listbox.get(listbox.curselection())
            if val not in selected_airlines:
                selected_airlines.append(val)
                refresh_selected()
        except:
            messagebox.showerror("Error", "Select an airline from the list first.")

    def remove():
        try:
            val = selected_box.get(selected_box.curselection())
            selected_airlines.remove(val)
            refresh_selected()
        except:
            messagebox.showerror("Error", "Select a selected airline to remove first.")

    def clear():
        selected_airlines.clear()
        refresh_selected()

    def apply():
        # ── NEW: warn if no airlines selected (will show all) ─────────────
        if not selected_airlines:
            if not messagebox.askyesno(
                "No Filter",
                "No airlines selected — all airlines will be shown.\nContinue?"
            ):
                return
        win.destroy()
        PlotAl()

    search_var.trace("w", lambda *args: refresh_available())
    refresh_available()
    refresh_selected()

    Button(win, text="Add →",        command=add,    width=20).pack(pady=2)
    Button(win, text="← Remove",     command=remove, width=20).pack(pady=2)
    Button(win, text="Clear",        command=clear,  width=20).pack(pady=2)
    Button(win, text="Apply Filter", command=apply,  width=25,
           bg="#7c3aed", fg="white").pack(pady=10)


def PlotAp():
    # ── NEW: guard against empty airport data ─────────────────────────────
    try:
        airports = LoadAirports()
    except Exception as e:
        messagebox.showerror("Error", f"Could not load airports:\n{e}")
        return
    if not airports:
        messagebox.showwarning("No Data", "No airports found in Airports.txt.")
        return
    ShowPlot(PlotAirports(airports))

def PlotArrRate():
    # ── NEW: guard against empty arrivals data ────────────────────────────
    try:
        arrivals = LoadArrivals()
    except Exception as e:
        messagebox.showerror("Error", f"Could not load arrivals:\n{e}")
        return
    if not arrivals:
        messagebox.showwarning("No Data", "No arrivals data found to plot.")
        return
    ShowPlot(PlotArrivals(arrivals))

def PlotFlTy():
    # ── NEW: guard against empty arrivals data ────────────────────────────
    try:
        arrivals = LoadArrivals()
    except Exception as e:
        messagebox.showerror("Error", f"Could not load arrivals:\n{e}")
        return
    if not arrivals:
        messagebox.showwarning("No Data", "No arrivals data found to plot flight types.")
        return
    ShowPlot(PlotFlightsType(arrivals))

def PlotAl():
    # ── NEW: guard against empty arrivals data ────────────────────────────
    try:
        data = LoadArrivals()
    except Exception as e:
        messagebox.showerror("Error", f"Could not load arrivals:\n{e}")
        return
    if not data:
        messagebox.showwarning("No Data", "No arrivals data found to plot airlines.")
        return
    filtered = [d for d in data if d.company in selected_airlines] if selected_airlines else data
    # ── NEW: warn if filter produced zero results ─────────────────────────
    if not filtered:
        messagebox.showwarning(
            "No Results",
            "The selected airline filter returned no flights.\n"
            "Try removing some airlines from the filter."
        )
        return
    ShowPlot(PlotAirlines(filtered), right_panel_builder=BuildAirlineFilter)

def MapAp():
    # ── NEW: guard against empty airport data ─────────────────────────────
    try:
        airports = LoadAirports()
    except Exception as e:
        messagebox.showerror("Error", f"Could not load airports:\n{e}")
        return
    if not airports:
        messagebox.showwarning("No Data", "No airports found in Airports.txt.")
        return
    try:
        MapAirports(airports)
        os.system("start Airports.kml")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate airport map:\n{e}")

def MapFl():
    # ── NEW: guard against empty arrivals data ────────────────────────────
    try:
        arrivals = LoadArrivals()
    except Exception as e:
        messagebox.showerror("Error", f"Could not load arrivals:\n{e}")
        return
    if not arrivals:
        messagebox.showwarning("No Data", "No arrivals data found to map.")
        return
    try:
        MapFlights(arrivals)
        os.system("start Flights.kml")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate flights map:\n{e}")

def MapFlLong():
    # ── NEW: guard against empty arrivals/long-distance data ──────────────
    try:
        arrivals = LoadArrivals()
    except Exception as e:
        messagebox.showerror("Error", f"Could not load arrivals:\n{e}")
        return
    if not arrivals:
        messagebox.showwarning("No Data", "No arrivals data found.")
        return
    long_flights = LongDistanceArrivals(arrivals)
    if not long_flights:
        messagebox.showwarning("No Results", "No long-distance arrivals found in the data.")
        return
    try:
        MapFlights(long_flights)
        os.system("start Flights.kml")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate long-distance flights map:\n{e}")


# ═══════════════════════════════════════════════════════════════════════════
# ADD / SAVE / REMOVE
# ═══════════════════════════════════════════════════════════════════════════

def Save():
    icao_val = get_value(icao, PH_ICAO)
    lat      = get_value(latitude,  PH_LAT)
    lon      = get_value(longitude, PH_LON)

    # ── NEW: validate all three fields ────────────────────────────────────
    if icao_val == "":
        messagebox.showerror("Error", "ICAO code is required.")
        return
    if lat == "" or lon == "":
        messagebox.showerror("Error", "Both latitude and longitude are required.")
        return

    try:
        a = Airport()
        a.icao      = icao_val
        a.latitude  = ConvertCoordinates(lat)
        a.longitude = ConvertCoordinates(lon)
        SetSchengen(a)
        SaveSchengenAirports(a)
        # ── NEW: success confirmation ──────────────────────────────────────
        messagebox.showinfo("Saved", f"Airport '{icao_val}' saved successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save airport:\n{e}")

def Add():
    icao_val = get_value(icao,      PH_ICAO)
    lat      = get_value(latitude,  PH_LAT)
    lon      = get_value(longitude, PH_LON)

    # ── NEW: validate all fields before adding ────────────────────────────
    if icao_val == "":
        messagebox.showerror("Error", "ICAO code is required.")
        return
    if lat == "":
        messagebox.showerror("Error", "Latitude is required.")
        return
    if lon == "":
        messagebox.showerror("Error", "Longitude is required.")
        return

    try:
        a = Airport()
        a.icao      = icao_val
        a.latitude  = ConvertCoordinates(lat)
        a.longitude = ConvertCoordinates(lon)
        SetSchengen(a)
        AddAirport(a)
        # ── NEW: success confirmation ──────────────────────────────────────
        if lat != "" and lon != "":
            messagebox.showinfo("Added", f"Airport '{icao_val}' added successfully.")
        else:
            messagebox.showerror("Error", "Latitude and longitude are required.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to add airport:\n{e}")

def Remove():
    icao_val = get_value(icao, PH_ICAO)

    # ── NEW: validate ICAO field ──────────────────────────────────────────
    if icao_val == "":
        messagebox.showerror("Error", "Enter an ICAO code to remove.")
        return

    # ── NEW: confirm before deleting ─────────────────────────────────────
    if not messagebox.askyesno(
        "Confirm Removal",
        f"Are you sure you want to remove airport '{icao_val}'?"
    ):
        return

    try:
        airports = LoadAirports()
        # ── NEW: check the airport actually exists ────────────────────────
        exists = any(a.icao == icao_val for a in airports)
        if not exists:
            messagebox.showerror("Not Found", f"Airport '{icao_val}' not found in Airports.txt.")
            return
        RemoveAirport(airports, icao_val)
        # ── NEW: success confirmation ──────────────────────────────────────
        messagebox.showinfo("Removed", f"Airport '{icao_val}' removed successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to remove airport:\n{e}")


# ═══════════════════════════════════════════════════════════════════════════
# AIRPORT OPERATIONS
# ═══════════════════════════════════════════════════════════════════════════

def LoadAP():
    global bcn
    result = LoadAirportStructure()
    if result == -1:
        messagebox.showerror("Error", "Terminals.txt not found")
        return
    bcn = result
    messagebox.showinfo("Success", "Airport structure loaded successfully")


# ═══════════════════════════════════════════════════════════════════════════
# OCCUPANCY PANEL
# ═══════════════════════════════════════════════════════════════════════════

def RenderOccupancyChart(graph_frame, terminal_filter, area_filter,
                          airline_filter, status_filter, search_text):
    """Build and draw the occupancy bar chart into graph_frame."""
    for w in graph_frame.winfo_children():
        w.destroy()

    # ── NEW: guard against bcn not loaded ────────────────────────────────
    if bcn is None:
        messagebox.showerror("Error", "Airport structure is not loaded.")
        return

    try:
        occupancy = GateOccupancy(bcn)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to retrieve gate occupancy:\n{e}")
        return

    # ── apply filters ──────────────────────────────────────────────────────
    filtered = []
    for row in occupancy:
        gate_name = row[0]   # e.g. "T1a3"
        status    = row[1]   # "free" or "occupied"
        aircraft  = row[2]   # aircraft ID or ""

        # terminal filter: gate name starts with terminal name
        if terminal_filter != "All":
            if not gate_name.startswith(terminal_filter):
                continue

        # area filter: letter after terminal prefix
        if area_filter != "All":
            prefix_len = len(terminal_filter) if terminal_filter != "All" else 2
            area_letter = ""
            for ch in gate_name:
                if ch.isalpha() and gate_name.index(ch) >= 1:
                    area_letter = ch
                    break
            # simpler: find the first lowercase letter in gate_name
            for ch in gate_name:
                if ch.islower():
                    area_letter = ch
                    break
            if area_letter != area_filter.lower():
                continue

        # status filter
        if status_filter != "All":
            if status != status_filter.lower():
                continue

        # airline filter — match aircraft ID prefix against arrivals
        if airline_filter != "All" and status == "occupied":
            arrivals = LoadArrivals()
            match = next((a for a in arrivals
                          if a.id == aircraft and a.company == airline_filter), None)
            if match is None:
                continue

        # search text
        if search_text:
            if search_text.lower() not in gate_name.lower() and \
               search_text.lower() not in aircraft.lower():
                continue

        filtered.append(row)

    # ── draw chart ─────────────────────────────────────────────────────────
    if not filtered:
        Label(graph_frame, text="No gates match the current filters.",
              bg="#2a2a3d", fg="#c084fc", font=("Segoe UI", 13)).pack(expand=True)
        return

    names   = [row[0] for row in filtered]
    statuses= [row[1] for row in filtered]
    ids     = [row[2] for row in filtered]
    colors  = ["#4ade80" if s == "free" else "#f87171" for s in statuses]

    fig, ax = plt.subplots(figsize=(10, max(3, len(names) * 0.32)))
    fig.patch.set_facecolor("#2a2a3d")
    ax.set_facecolor("#1e1e2e")

    ax.barh(names, [1] * len(names), color=colors, edgecolor="#2a2a3d", height=0.72)

    for i, (status, aid) in enumerate(zip(statuses, ids)):
        label = "Free" if status == "free" else f"Occupied  ·  {aid}"
        ax.text(0.015, i, label, va="center", ha="left",
                fontsize=7.5, color="white", fontweight="bold")

    total   = len(filtered)
    n_free  = sum(1 for s in statuses if s == "free")
    n_occ   = total - n_free

    ax.set_xlim(0, 1)
    ax.set_title(
        f"Gate Occupancy — LEBL Barcelona\n"
        f"{total} gates  ·  {n_free} free  ·  {n_occ} occupied",
        color="#c084fc", fontsize=11, fontweight="bold", pad=10
    )
    ax.tick_params(colors="#a0a0c0", labelsize=7.5)
    ax.spines[:].set_visible(False)
    ax.xaxis.set_visible(False)

    free_p = mpatches.Patch(color="#4ade80", label=f"Free ({n_free})")
    occ_p  = mpatches.Patch(color="#f87171", label=f"Occupied ({n_occ})")
    ax.legend(handles=[free_p, occ_p], loc="lower right",
              facecolor="#313244", labelcolor="white", fontsize=8)

    plt.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
    plt.close(fig)


def BuildOccupancyPanel(right_frame, graph_frame):
    """Side panel with all filters for the occupancy view."""

    PANEL_BG  = "#222233"
    CTRL_BG   = "#2e2e44"
    FG        = "#c084fc"
    FG2       = "#ffffff"
    FONT_LBL  = ("Segoe UI", 8, "bold")
    FONT_CTRL = ("Segoe UI", 9)

    # ── collect filter options from bcn ────────────────────────────────────
    terminals = ["All"] + [t.name for t in bcn.terminals]

    areas_set = set()
    for t in bcn.terminals:
        for a in t.areas:
            areas_set.add(a.name.upper())
    areas = ["All"] + sorted(areas_set)

    airlines_set = set()
    try:
        data = LoadArrivals()
        for d in data:
            airlines_set.add(d.company)
    except:
        pass
    airlines = ["All"] + sorted(airlines_set)

    statuses = ["All", "Free", "Occupied"]

    # ── state variables ────────────────────────────────────────────────────
    terminal_var = StringVar(value="All")
    area_var     = StringVar(value="All")
    airline_var  = StringVar(value="All")
    status_var   = StringVar(value="All")
    search_var   = StringVar()

    def refresh(*_):
        RenderOccupancyChart(
            graph_frame,
            terminal_var.get(),
            area_var.get(),
            airline_var.get(),
            status_var.get(),
            search_var.get().strip()
        )

    # ── scrollable panel ───────────────────────────────────────────────────
    canvas_p  = Canvas(right_frame, bg=PANEL_BG, highlightthickness=0, bd=0)
    scroll_p  = Scrollbar(right_frame, orient=VERTICAL, command=canvas_p.yview)
    canvas_p.configure(yscrollcommand=scroll_p.set)
    scroll_p.pack(side=RIGHT, fill=Y)
    canvas_p.pack(side=LEFT, fill=BOTH, expand=True)

    inner = Frame(canvas_p, bg=PANEL_BG)
    win_id = canvas_p.create_window((0, 0), window=inner, anchor="nw")

    def on_configure(e):
        canvas_p.configure(scrollregion=canvas_p.bbox("all"))
        canvas_p.itemconfig(win_id, width=canvas_p.winfo_width())
    inner.bind("<Configure>", on_configure)
    canvas_p.bind("<Configure>", on_configure)

    def on_mouse(e):
        canvas_p.yview_scroll(int(-1 * (e.delta / 120)), "units")
    canvas_p.bind_all("<MouseWheel>", on_mouse)

    # ── helper to add a section ────────────────────────────────────────────
    def section(title):
        Label(inner, text=title, bg=PANEL_BG, fg=FG,
              font=FONT_LBL).pack(anchor="w", padx=10, pady=(12, 2))
        Frame(inner, bg="#3a3a5c", height=1).pack(fill=X, padx=8, pady=(0, 4))

    def dropdown(var, options):
        om = OptionMenu(inner, var, *options, command=refresh)
        om.config(bg=CTRL_BG, fg=FG2, font=FONT_CTRL, relief=FLAT,
                  activebackground="#3a3a5c", activeforeground=FG2,
                  highlightthickness=0, width=18)
        om["menu"].config(bg=CTRL_BG, fg=FG2, font=FONT_CTRL,
                          activebackground="#7c3aed")
        om.pack(padx=10, pady=2, fill=X)

    def listbox_filter(var, options, height=5):
        """Listbox that updates var and triggers refresh on select."""
        lb = Listbox(inner, bg=CTRL_BG, fg=FG2, font=FONT_CTRL,
                     selectbackground="#7c3aed", selectforeground="white",
                     height=height, relief=FLAT, bd=0,
                     exportselection=False)
        for o in options:
            lb.insert(END, o)
        lb.select_set(0)   # default "All"
        lb.pack(padx=10, pady=2, fill=X)

        def on_select(e):
            try:
                val = lb.get(lb.curselection())
                var.set(val)
                refresh()
            except:
                pass
        lb.bind("<<ListboxSelect>>", on_select)
        return lb

    # ── title ──────────────────────────────────────────────────────────────
    Label(inner, text="Gate Occupancy", bg=PANEL_BG, fg=FG,
          font=("Segoe UI", 11, "bold")).pack(pady=(14, 2))
    Label(inner, text="Filters", bg=PANEL_BG, fg="#888899",
          font=("Segoe UI", 8)).pack()
    Frame(inner, bg="#3a3a5c", height=1).pack(fill=X, padx=8, pady=6)

    # ── search ─────────────────────────────────────────────────────────────
    section("🔍  Search gate / aircraft")
    search_entry = Entry(inner, textvariable=search_var, bg=CTRL_BG, fg=FG2,
                         insertbackground=FG2, relief=FLAT, font=FONT_CTRL)
    search_entry.pack(padx=10, pady=2, fill=X, ipady=4)
    search_var.trace_add("write", refresh)
    add_placeholder(search_entry, "Gate name or aircraft ID…")

    # ── status ─────────────────────────────────────────────────────────────
    section("◉  Status")
    status_frame = Frame(inner, bg=PANEL_BG)
    status_frame.pack(padx=10, pady=4, fill=X)
    for s in statuses:
        color = "#4ade80" if s == "Free" else "#f87171" if s == "Occupied" else "#888899"
        rb = Radiobutton(status_frame, text=s, variable=status_var, value=s,
                         command=refresh, bg=PANEL_BG, fg=color,
                         selectcolor=PANEL_BG, activebackground=PANEL_BG,
                         font=FONT_CTRL, cursor="hand2")
        rb.pack(side=LEFT, padx=6)

    # ── terminal ───────────────────────────────────────────────────────────
    section("🏢  Terminal")
    listbox_filter(terminal_var, terminals, height=min(6, len(terminals)))

    # ── area ───────────────────────────────────────────────────────────────
    section("🚪  Boarding area")
    listbox_filter(area_var, areas, height=min(6, len(areas)))

    # ── airline ────────────────────────────────────────────────────────────
    section("✈  Airline (occupied gates)")

    # search inside airlines listbox
    al_search_var = StringVar()
    al_search = Entry(inner, textvariable=al_search_var, bg=CTRL_BG, fg=FG2,
                      insertbackground=FG2, relief=FLAT, font=FONT_CTRL)
    al_search.pack(padx=10, pady=(2, 1), fill=X, ipady=3)
    add_placeholder(al_search, "Search airline…")

    al_lb = Listbox(inner, bg=CTRL_BG, fg=FG2, font=FONT_CTRL,
                    selectbackground="#7c3aed", selectforeground="white",
                    height=7, relief=FLAT, bd=0, exportselection=False)
    al_lb.pack(padx=10, pady=2, fill=X)

    def populate_airlines(q=""):
        al_lb.delete(0, END)
        for a in airlines:
            if q.lower() in a.lower():
                al_lb.insert(END, a)
        al_lb.select_set(0)

    def on_al_select(e):
        try:
            val = al_lb.get(al_lb.curselection())
            airline_var.set(val)
            refresh()
        except:
            pass

    def on_al_search(*_):
        q = al_search_var.get()
        if q == "Search airline…":
            q = ""
        populate_airlines(q)

    al_lb.bind("<<ListboxSelect>>", on_al_select)
    al_search_var.trace_add("write", on_al_search)
    populate_airlines()

    # ── reset button ───────────────────────────────────────────────────────
    Frame(inner, bg="#3a3a5c", height=1).pack(fill=X, padx=8, pady=10)

    def reset_filters():
        terminal_var.set("All")
        area_var.set("All")
        airline_var.set("All")
        status_var.set("All")
        search_var.set("")
        al_search_var.set("")
        populate_airlines()
        refresh()

    Button(inner, text="↺  Reset all filters", command=reset_filters,
           bg="#3a3a5c", fg=FG2, font=FONT_CTRL, relief=FLAT,
           activebackground="#7c3aed", activeforeground="white",
           cursor="hand2").pack(padx=10, pady=4, fill=X, ipady=5)

    Frame(inner, bg=PANEL_BG, height=20).pack()

    # ── initial render ─────────────────────────────────────────────────────
    refresh()


def ShowOccupancy():
    if bcn is None:
        messagebox.showerror("Error", "Load airport structure first")
        return

    for w in frame3.winfo_children():
        w.destroy()

    frame3.rowconfigure(0, weight=1)
    frame3.columnconfigure(0, weight=4)
    frame3.columnconfigure(1, weight=1)

    graph_frame = Frame(frame3, bg="#2a2a3d")
    graph_frame.grid(row=0, column=0, sticky="nsew")

    right_frame = Frame(frame3, bg="#222233", width=280)
    right_frame.grid(row=0, column=1, sticky="nsew")
    right_frame.pack_propagate(False)

    BuildOccupancyPanel(right_frame, graph_frame)


def SearchAirline():
    if bcn is None:
        messagebox.showerror("Error", "Load airport structure first")
        return
    name = get_value(airline_entry, PH_AIRLINE)
    if name == "":
        messagebox.showerror("Error", "Enter an airline ICAO code to search.")
        return
    # ── NEW: wrap in try/except ───────────────────────────────────────────
    try:
        res = SearchTerminal(bcn, name)
    except Exception as e:
        messagebox.showerror("Error", f"Search failed:\n{e}")
        return
    if res == "":
        messagebox.showinfo("Not Found", f"'{name}' was not found in any terminal.")
    else:
        messagebox.showinfo("Terminal Found", f"'{name}' boards at terminal {res}.")

def CheckIsAirlineInTerminal():
    if bcn is None:
        messagebox.showerror("Error", "Load airport structure first")
        return
    t_name  = get_value(terminal_entry, PH_TERMINAL)
    airline = get_value(airline_entry,  PH_AIRLINE)

    # ── NEW: validate both fields ─────────────────────────────────────────
    if t_name == "":
        messagebox.showerror("Error", "Enter a terminal name (e.g. T1).")
        return
    if airline == "":
        messagebox.showerror("Error", "Enter an airline ICAO code.")
        return

    t_obj = next((t for t in bcn.terminals if t.name == t_name), None)
    if t_obj is None:
        messagebox.showerror("Not Found", f"Terminal '{t_name}' does not exist in the loaded structure.")
        return

    # ── NEW: wrap in try/except ───────────────────────────────────────────
    try:
        res = IsAirlineInTerminal(t_obj, airline)
    except Exception as e:
        messagebox.showerror("Error", f"Check failed:\n{e}")
        return

    if res:
        messagebox.showinfo("Result", f"'{airline}' IS assigned to terminal {t_name}.")
    else:
        messagebox.showinfo("Result", f"'{airline}' is NOT assigned to terminal {t_name}.")

def AssignGateUI():
    if bcn is None:
        messagebox.showerror("Error", "Load airport structure first")
        return
    aircraft_id = get_value(aircraft_entry, PH_AIRCRAFT)
    if aircraft_id == "":
        messagebox.showerror("Error", "Enter an aircraft ID.")
        return

    # ── NEW: guard against arrivals load failure ──────────────────────────
    try:
        arrivals = LoadArrivals()
    except Exception as e:
        messagebox.showerror("Error", f"Could not load arrivals:\n{e}")
        return

    target = next((a for a in arrivals if a.id == aircraft_id), None)
    if target is None:
        messagebox.showerror("Not Found", f"Aircraft '{aircraft_id}' was not found in Arrivals.txt.")
        return

    # ── NEW: wrap AssignGate in try/except ────────────────────────────────
    try:
        result = AssignGate(bcn, target)
    except Exception as e:
        messagebox.showerror("Error", f"Gate assignment failed:\n{e}")
        return

    if result == -1:
        messagebox.showerror("No Gate Available",
            f"No free gate could be assigned to aircraft '{aircraft_id}'.\n"
            "All compatible gates may be occupied.")
        return

    gate_name = ""
    for t in bcn.terminals:
        for a in t.areas:
            for g in a.gates:
                if g.ID == aircraft_id:
                    gate_name = g.name
                    break

    # ── NEW: handle edge case where gate was assigned but name not found ──
    if gate_name == "":
        messagebox.showwarning(
            "Gate Assigned",
            f"Aircraft '{aircraft_id}' was assigned a gate, but the gate name could not be retrieved."
        )
        return

    messagebox.showinfo("Gate Assigned",
        f"Aircraft:  {aircraft_id}\n"
        f"Airline:   {target.company}\n"
        f"Origin:    {target.origin}\n"
        f"Gate:      {gate_name}")


# ═══════════════════════════════════════════════════════════════════════════
# AIRLINE FILTER PANEL (for PlotAl)
# ═══════════════════════════════════════════════════════════════════════════

def BuildAirlineFilter(right_frame, graph_frame):
    global airline_search_var

    Label(right_frame, text="Airline Filter", bg="#222233", fg="#c084fc",
          font=("Segoe UI", 11, "bold")).pack(pady=10)

    airline_search_var = StringVar()

    search_entry = Entry(right_frame, textvariable=airline_search_var, width=25,
                         fg=PLACEHOLDER_COLOR, bg="#2e2e44",
                         insertbackground="white", relief=FLAT)
    search_entry.pack(pady=5, padx=8, fill=X, ipady=4)
    add_placeholder(search_entry, "Search airline…")

    available_box = Listbox(right_frame, bg="#2e2e44", fg="white",
                            selectbackground="#7c3aed", relief=FLAT,
                            height=10, exportselection=False)
    available_box.pack(padx=8, pady=4, fill=X)

    Label(right_frame, text="Selected", bg="#222233", fg="white",
          font=("Segoe UI", 8, "bold")).pack()

    selected_box = Listbox(right_frame, bg="#2e2e44", fg="#c084fc",
                           selectbackground="#7c3aed", relief=FLAT,
                           height=6, exportselection=False)
    selected_box.pack(padx=8, pady=4, fill=X)

    # ── NEW: guard against arrivals load failure ──────────────────────────
    try:
        data = LoadArrivals()
    except Exception as e:
        messagebox.showerror("Error", f"Could not load arrivals for airline filter:\n{e}")
        return

    airlines = sorted(set(d.company for d in data))

    def refresh_available():
        available_box.delete(0, END)
        q = airline_search_var.get().lower()
        if q == "search airline…":
            q = ""
        for a in airlines:
            if q in a.lower():
                available_box.insert(END, a)

    def refresh_selected():
        selected_box.delete(0, END)
        for a in selected_airlines:
            selected_box.insert(END, a)

    def add():
        try:
            val = available_box.get(available_box.curselection())
            if val not in selected_airlines:
                selected_airlines.append(val)
            refresh_selected()
        except:
            messagebox.showerror("Error", "Select an airline from the list first.")

    def remove():
        try:
            val = selected_box.get(selected_box.curselection())
            selected_airlines.remove(val)
            refresh_selected()
        except:
            messagebox.showerror("Error", "Select a selected airline to remove first.")

    def clear():
        selected_airlines.clear()
        refresh_selected()

    airline_search_var.trace_add("write", lambda *args: refresh_available())

    btn_cfg = dict(bg="#3a3a5c", fg="white", relief=FLAT,
                   activebackground="#7c3aed", activeforeground="white",
                   font=("Segoe UI", 8), cursor="hand2")

    Button(right_frame, text="Add →",    command=add,   **btn_cfg).pack(padx=8, pady=2, fill=X, ipady=3)
    Button(right_frame, text="← Remove", command=remove,**btn_cfg).pack(padx=8, pady=2, fill=X, ipady=3)
    Button(right_frame, text="Clear",    command=clear, **btn_cfg).pack(padx=8, pady=2, fill=X, ipady=3)
    Button(right_frame, text="Apply", bg="#7c3aed", fg="white", relief=FLAT,
           activebackground="#6d28d9", font=("Segoe UI", 9, "bold"),
           command=PlotAl, cursor="hand2").pack(padx=8, pady=8, fill=X, ipady=5)

    refresh_available()
    refresh_selected()


# ═══════════════════════════════════════════════════════════════════════════
# LAYOUT
# ═══════════════════════════════════════════════════════════════════════════

left = Frame(root, bg="#2a2a3d")
left.grid(row=0, column=0, sticky="nsew")

Label(left, text="AIRPORT CONTROL", bg="#2a2a3d", fg="#c084fc",
      font=("Segoe UI", 16, "bold")).grid(row=0, column=0, pady=10)

BTN = {
    "bg": "#7c3aed", "fg": "white", "font": FONT_B,
    "width": 24, "height": 1, "relief": "flat"
}

Label(left, text="Graphs", bg="#2a2a3d", fg="#c084fc").grid()

Button(left, text="Airports",      command=PlotAp,      **BTN).grid(pady=2)
Button(left, text="Show Airlines", command=PlotAl,      **BTN).grid(pady=2)
Button(left, text="Arrivals",      command=PlotArrRate, **BTN).grid(pady=2)
Button(left, text="Flight Types",  command=PlotFlTy,    **BTN).grid(pady=2)
Button(left, text="Map Airports",  command=MapAp,       **BTN).grid(pady=2)
Button(left, text="Map Flights",   command=MapFl,       **BTN).grid(pady=2)
Button(left, text="Long Flights",  command=MapFlLong,   **BTN).grid(pady=2)

Label(left, text="Airports", bg="#2a2a3d", fg="#c084fc").grid(pady=5)

icao      = Entry(left, width=30, bg="#3a3a5c", fg=PLACEHOLDER_COLOR, insertbackground="white")
latitude  = Entry(left, width=30, bg="#3a3a5c", fg=PLACEHOLDER_COLOR, insertbackground="white")
longitude = Entry(left, width=30, bg="#3a3a5c", fg=PLACEHOLDER_COLOR, insertbackground="white")
icao.grid(pady=1);      add_placeholder(icao,      PH_ICAO)
latitude.grid(pady=1);  add_placeholder(latitude,  PH_LAT)
longitude.grid(pady=1); add_placeholder(longitude, PH_LON)

Button(left, text="Save",   command=Save,   **BTN).grid(pady=2)
Button(left, text="Add",    command=Add,    **BTN).grid(pady=2)
Button(left, text="Remove", command=Remove, **BTN).grid(pady=2)

Label(left, text="Operations", bg="#2a2a3d", fg="#c084fc").grid(pady=5)

Button(left, text="Load Structure", command=LoadAP,        **BTN).grid(pady=2)
Button(left, text="Occupancy",      command=ShowOccupancy, **BTN).grid(pady=2)

terminal_entry = Entry(left, width=30, bg="#3a3a5c", fg=PLACEHOLDER_COLOR, insertbackground="white")
airline_entry  = Entry(left, width=30, bg="#3a3a5c", fg=PLACEHOLDER_COLOR, insertbackground="white")
aircraft_entry = Entry(left, width=30, bg="#3a3a5c", fg=PLACEHOLDER_COLOR, insertbackground="white")
terminal_entry.grid(pady=1); add_placeholder(terminal_entry, PH_TERMINAL)
airline_entry.grid(pady=1);  add_placeholder(airline_entry,  PH_AIRLINE)

Button(left, text="Check Airline",  command=CheckIsAirlineInTerminal, **BTN).grid(pady=2)
Button(left, text="Search Airline", command=SearchAirline,            **BTN).grid(pady=2)

aircraft_entry.grid(pady=1); add_placeholder(aircraft_entry, PH_AIRCRAFT)

Button(left, text="Assign Gate", command=AssignGateUI, **BTN).grid(pady=2)


# ── Right visualiser panel ────────────────────────────────────────────────
frame3 = Frame(root, bg="#2a2a3d")
frame3.grid(row=0, column=1, sticky="nsew")
frame3.rowconfigure(0, weight=1)
frame3.columnconfigure(0, weight=1)

Label(frame3, text="Select a function", bg="#2a2a3d", fg="#c084fc",
      font=("Segoe UI", 14)).grid()

root.mainloop()
