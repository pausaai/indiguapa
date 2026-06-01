class Gate:
    def __init__(self):
        self.name = ""
        self.free = False
        self.ID   = ""

class BoardingArea:
    def __init__(self):
        self.name  = ""
        self.type  = False
        self.gates = []

class Terminal:
    def __init__(self):
        self.name  = ""
        self.areas = []
        self.codes = []

class BarcelonaAP:
    def __init__(self):
        self.code      = ""
        self.terminals = []


def SetGates(area, init_gate, end_gate, prefix):
    if init_gate > end_gate:
        return -1
    i = init_gate
    while i <= end_gate:
        g = Gate()
        g.name = prefix + area.name + str(i)
        g.free = True
        area.gates.append(g)
        i += 1
    return area


def LoadAirlines(terminal, t_name):
    filename = t_name + "_Airlines.txt"
    try:
        f = open(filename, "r")
    except:
        return -1

    terminal.codes = []
    lines = f.readlines()
    f.close()

    for line in lines:
        line = line.strip()
        if line != "":
            parts = line.split("\t")
            if len(parts) >= 2:
                terminal.codes.append(parts[1].strip())
    return terminal


def LoadAirportStructure():
    try:
        f = open("LEBL.txt", "r")
    except:
        return -1

    lines = f.readlines()
    f.close()
    lines = [l.strip() for l in lines]

    first      = lines[0].split()
    airport    = BarcelonaAP()
    airport.code = first[0]
    num_terminals = int(first[1])
    idx = 1

    for _ in range(num_terminals):
        term_parts = lines[idx].split()
        idx += 1
        terminal      = Terminal()
        terminal.name = term_parts[1]
        num_areas     = int(term_parts[2])

        for _ in range(num_areas):
            area_parts = lines[idx].split()
            idx += 1
            area      = BoardingArea()
            area.name = area_parts[1].lower()
            area.type = (area_parts[2] == "Schengen")
            init_gate = int(area_parts[4])
            end_gate  = int(area_parts[6])
            result    = SetGates(area, init_gate, end_gate, terminal.name)
            if result == -1:
                return -1
            terminal.areas.append(area)

        LoadAirlines(terminal, terminal.name)
        airport.terminals.append(terminal)

    return airport


def GateOccupancy(bcn):
    occupancy = []
    for terminal in bcn.terminals:
        for area in terminal.areas:
            for gate in area.gates:
                entry = [gate.name]
                if gate.free:
                    entry.append("free")
                    entry.append("")
                else:
                    entry.append("occupied")
                    entry.append(gate.ID)
                occupancy.append(entry)
    return occupancy


def IsAirlineInTerminal(terminal, name):
    if not terminal or not name:
        return False
    for code in terminal.codes:
        if code == name:
            return True
    return False


def SearchTerminal(bcn, name):
    for terminal in bcn.terminals:
        if IsAirlineInTerminal(terminal, name):
            return terminal.name
    return ""


def AssignGate(bcn, aircraft):
    terminal_name = SearchTerminal(bcn, aircraft.company)
    if terminal_name == "":
        print("Airline not found in any terminal")
        return -1

    terminal = next((t for t in bcn.terminals if t.name == terminal_name), None)
    if terminal is None:
        return -1

    for area in terminal.areas:
        for gate in area.gates:
            if gate.free:
                gate.free = False
                gate.ID   = aircraft.id
                return 0
    return -1

def AssignNightGates(bcn, aircrafts):
    #VERIFICAMOS con la condicion aircrafts[i].time == "00:00" and aircrafts[i].origin == "" que no tiene llegadas, aka es nocturno
    #Luego con funcion AssigGate le asignamos un puerta y pasa al siguiente
    if len(aircrafts) == 0:
        return -1
    i = 0
    while i < len(aircrafts):
        # Only process aircraft with no arrival data (night aircraft)
        if aircrafts[i].time == "00:00" and aircrafts[i].origin == "":
            AssignGate(bcn, aircrafts[i])
        i = i + 1

def AssignNightGates(bcn, aircrafts):
    #VERIFICAMOS con la condicion aircrafts[i].time == "00:00" and aircrafts[i].origin == "" que no tiene llegadas, aka es nocturno
    #Luego con funcion AssigGate le asignamos un puerta y pasa al siguiente
    if len(aircrafts) == 0:
        return -1
    i = 0
    while i < len(aircrafts):
        # Only process aircraft with no arrival data (night aircraft)
        if aircrafts[i].time == "00:00" and aircrafts[i].origin == "":
            AssignGate(bcn, aircrafts[i])
        i = i + 1


def FreeGate(bcn, id):
    t = 0
    while t < len(bcn.terminals):
        terminal = bcn.terminals[t]
        a = 0
        while a < len(terminal.areas):
            area = terminal.areas[a]
            g = 0
            while g < len(area.gates):
                gate = area.gates[g]
                if gate.free == False and gate.ID == id:
                    gate.free = True
                    gate.ID = ""
                    return 0
                g += 1
            a += 1
        t += 1
    return -1


def AssignGatesAtTime(bcn, aircrafts, time):
    # Parse the given hour as an integer (0-23)
    given_hour = int(time.split(":")[0])

    # Step 1: free gates of aircraft that have already departed before
    # the start of the considered period. An aircraft has departed if its
    # departure time is strictly less than the given hour.
    i = 0
    while i < len(aircrafts):
        aircraft = aircrafts[i]
        # Only process aircraft that have a departure record
        if hasattr(aircraft, 'departure') and aircraft.departure != "" and aircraft.departure != "00:00":
            dep_hour = int(aircraft.departure.split(":")[0])
            if dep_hour < given_hour:
                FreeGate(bcn, aircraft.id)
        i += 1

    # Step 2: assign gates to aircraft landing during the one-hour period
    # [given_hour, given_hour + 1). Count how many could not be assigned.
    not_assigned = 0
    i = 0
    while i < len(aircrafts):
        aircraft = aircrafts[i]
        # Only process landing aircraft (those with a non-empty arrival time
        # that is not the special night marker "00:00" with no origin)
        if hasattr(aircraft, 'time') and aircraft.time != "" and aircraft.time != "00:00":
            land_hour = int(aircraft.time.split(":")[0])
            if land_hour >= given_hour and land_hour < given_hour + 1:
                result = AssignGate(bcn, aircraft)
                if result == -1:
                    not_assigned += 1
        i += 1

    return not_assigned


def PlotDayOccupancy(bcn, aircrafts):

    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
    import numpy as np

    hours = []
    # unassigned_counts[h] = number of aircraft not assigned during hour h
    unassigned_counts = []
    # terminal_counts[h] = list of occupied gate counts, one per terminal
    terminal_counts = []

    terminal_names = [t.name for t in bcn.terminals]
    num_terminals = len(terminal_names)

    hour = 1
    while hour <= 23:
        time_str = str(hour).zfill(2) + ":00"
        not_assigned = AssignGatesAtTime(bcn, aircrafts, time_str)
        unassigned_counts.append(not_assigned)

        # Count occupied gates per terminal
        counts = []
        t = 0
        while t < len(bcn.terminals):
            terminal = bcn.terminals[t]
            occupied = 0
            a = 0
            while a < len(terminal.areas):
                area = terminal.areas[a]
                g = 0
                while g < len(area.gates):
                    if area.gates[g].free == False:
                        occupied += 1
                    g += 1
                a += 1
            counts.append(occupied)
            t += 1
        terminal_counts.append(counts)
        hours.append(hour)
        hour += 1

    # Build the plot
    x = np.arange(len(hours))
    # Width of each bar; distribute evenly within each group
    if num_terminals > 0:
        bar_width = 0.6 / num_terminals
    else:
        bar_width = 0.6

    fig, ax1 = plt.subplots(figsize=(14, 6))

    # Color palette for terminals
    colors = plt.colormaps["tab10"].colors

    for idx in range(num_terminals):
        offsets = x + (idx - num_terminals / 2 + 0.5) * bar_width
        values = [terminal_counts[h][idx] for h in range(len(hours))]
        ax1.bar(
            offsets,
            values,
            width=bar_width,
            label=terminal_names[idx],
            color=colors[idx % len(colors)],
            alpha=0.85,
            edgecolor="white",
            linewidth=0.5
        )

    ax1.set_xlabel("Hour of day", fontsize=11)
    ax1.set_ylabel("Gates occupied", fontsize=11)
    ax1.set_xticks(x)
    ax1.set_xticklabels([str(h).zfill(2) + ":00" for h in hours], rotation=45, ha="right")
    ax1.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax1.legend(title="Terminal", loc="upper left", fontsize=9)
    ax1.set_title("Gate occupancy per terminal throughout the day", fontsize=13)

    # Secondary y-axis: unassigned aircraft per hour
    ax2 = ax1.twinx()
    ax2.plot(
        x,
        unassigned_counts,
        color="crimson",
        marker="o",
        linewidth=1.8,
        markersize=5,
        label="Unassigned aircraft",
        zorder=5
    )
    ax2.set_ylabel("Unassigned aircraft", fontsize=11, color="crimson")
    ax2.tick_params(axis="y", labelcolor="crimson")
    ax2.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax2.legend(loc="upper right", fontsize=9)

    plt.tight_layout()
    plt.savefig("day_occupancy.png", dpi=150)
    plt.show()