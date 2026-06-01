from airport import IsSchengenAirport


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
        f = open("Terminals.txt", "r")
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
    if terminal_name != "":
        terminal = next((t for t in bcn.terminals if t.name == terminal_name), None)
        if terminal is not None:
            for area in terminal.areas:
                for gate in area.gates:
                    if gate.free:
                        gate.free = False
                        gate.ID = aircraft.id
                        return 0
    is_schengen = IsSchengenAirport(aircraft.origin)
    for terminal in bcn.terminals:
        for area in terminal.areas:
            if area.type == is_schengen:
                for gate in area.gates:
                    if gate.free:
                        gate.free = False
                        gate.ID = aircraft.id
                        return 0

    return -1

def AssignNightGates(bcn, aircrafts):
    #VERIFICAMOS con la condicion aircrafts[i].time == "00:00" and aircrafts[i].origin == "" que no tiene llegadas, aka es nocturno
    #Luego con funcion AssigGate le asignamos un puerta y pasa al siguiente
    if len(aircrafts) == 0:
        return -1
    i = 0
    while i < len(aircrafts):

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


def LoadDepartures():
    departures = {}
    try:
        f = open("Departures.txt", "r")
    except:
        return {}

    lines = f.readlines()
    f.close()

    for line in lines[1:]:  # Skip header row
        line = line.strip()
        if line != "":
            parts = line.split()  # Split on whitespace instead of tab
            if len(parts) >= 3:
                flight_id   = parts[0].strip()
                depart_time = parts[2].strip()  # Column 2 is departure, not 1
                departures[flight_id] = depart_time

    return departures


def AssignGatesAtTime(bcn, aircrafts, time, departures):
    given_hour = int(time.split(":")[0])
    events = []
    for aircraft in aircrafts:
        dep_time = departures.get(aircraft.id, "")
        if dep_time != "" and dep_time != "00:00":
            dep_hour = int(dep_time.split(":")[0])
            dep_min = int(dep_time.split(":")[1])
            if dep_hour == given_hour:
                events.append((dep_hour, dep_min, "departure", aircraft))

        if aircraft.time != "" and aircraft.time != "00:00":
            land_hour = int(aircraft.time.split(":")[0])
            land_min = int(aircraft.time.split(":")[1])
            if land_hour == given_hour:
                events.append((land_hour, land_min, "arrival", aircraft))
                
    events.sort(key=lambda e: (e[1], 0 if e[2] == "departure" else 1))

    not_assigned = 0
    for _, _, event_type, aircraft in events:
        if event_type == "departure":
            FreeGate(bcn, aircraft.id)
        else:
            if AssignGate(bcn, aircraft) == -1:
                not_assigned += 1

    return not_assigned


def PlotDayOccupancy(bcn, aircrafts):
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
    import numpy as np

    departures = LoadDepartures()

    def count_occupied_gates(bcn):
        return [
            sum(1 for area in terminal.areas for gate in area.gates if not gate.free)
            for terminal in bcn.terminals
        ]

    terminal_names = [t.name for t in bcn.terminals]
    hours = list(range(1, 24))
    unassigned_counts = []
    terminal_counts = []

    for hour in hours:
        unassigned_counts.append(AssignGatesAtTime(bcn, aircrafts, f"{hour:02d}:00", departures))
        terminal_counts.append(count_occupied_gates(bcn))

    x = np.arange(len(hours))
    bar_width = 0.6 / max(len(terminal_names), 1)
    colors = plt.colormaps["tab10"].colors

    fig, ax1 = plt.subplots(figsize=(14, 6))

    for idx, name in enumerate(terminal_names):
        offsets = x + (idx - len(terminal_names) / 2 + 0.5) * bar_width
        values = [terminal_counts[h][idx] for h in range(len(hours))]
        ax1.bar(offsets, values, width=bar_width, label=name,
                color=colors[idx % len(colors)], alpha=0.85, edgecolor="white", linewidth=0.5)

    ax1.set_xlabel("Hour of day", fontsize=11)
    ax1.set_ylabel("Gates occupied", fontsize=11)
    ax1.set_xticks(x)
    ax1.set_xticklabels([f"{h:02d}:00" for h in hours], rotation=45, ha="right")
    ax1.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax1.legend(title="Terminal", loc="upper left", fontsize=9)
    ax1.set_title("Gate occupancy per terminal throughout the day", fontsize=13)

    ax2 = ax1.twinx()
    ax2.plot(x, unassigned_counts, color="crimson", marker="o",
             linewidth=1.8, markersize=5, label="Unassigned aircraft", zorder=5)
    ax2.set_ylabel("Unassigned aircraft", fontsize=11, color="crimson")
    ax2.tick_params(axis="y", labelcolor="crimson")
    ax2.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax2.legend(loc="upper right", fontsize=9)

    plt.tight_layout()
    plt.show()
