import matplotlib.pyplot as pyplot

class Airport:
    def __init__(self):
        self.icao = ""
        self.latitude = 0.0
        self.longitude = 0.0
        self.schengen = False
# Clase que representa un aeropuerto con sus atributos: código ICAO, latitud, longitud y si es Schengen.

def IsSchengenAirport(code):
    # Parámetros: code (str) -> código ICAO del aeropuerto
    # Descripción: Comprueba si un aeropuerto pertenece a la zona Schengen según los dos primeros caracteres de su código ICAO.

    if code == '' or len(code) != 4:
        return False
    zone = code[0] + code[1]
    codes = ['ET','EI','LO','EB','LK','LC','EK','EE','EF','LF','ED','LG','EH','LH','BI','LI','EV','EY','EL','LM','EN','EP','LP','LZ','LJ','LE','ES','LS','GC','LD','LR','LB']
    found = False
    i = 0
    while not found and i < len(codes):
        if codes[i] == zone:
            found = True
        i = i + 1
    return found

def ConvertCoordinates(coord):
    # Parámetros: coord (str) -> coordenada en formato DMS (ej: N412945)
    # Descripción: Convierte una coordenada en formato DMS (grados, minutos, segundos) a formato decimal. Devuelve False si el formato es inválido.

    try:
        direction = coord [0]
        if direction == 'N' or direction == 'S':
            degrees = int(coord[1:3])
            minutes = int(coord[3:5])
            seconds = int(coord[5:7])
        else:
            degrees = int(coord[1:4])
            minutes = int(coord[4:6])
            seconds = int(coord[6:8])
        decimal = degrees + minutes/60 + seconds/3600
        if direction == 'S' or direction == 'W':
            decimal = -decimal
        return decimal
    except Exception:
        print(f'{coord} is not a valid coordinate.')
        return False

def ReturnCoordinates(decimal, islat):
    # Parámetros: decimal (float) -> coordenada en formato decimal
    #             islat (bool) -> True si es latitud, False si es longitud
    # Descripción: Convierte una coordenada decimal a formato DMS con dirección (N/S/E/W).

    if islat:
        if decimal >= 0:
            direction = "N"
        else:
            direction = "S"
    else:
        if decimal >= 0:
            direction = "E"
        else:
            direction = "W"
    decimal = abs(decimal)
    deg = int(decimal)
    mins = int((decimal - deg) * 60)
    sec = int((decimal - deg - mins/60)*3600)
    if islat:
        if deg < 10:
            degfin = "0" + str(deg)
        else:
            degfin = str(deg)
    else:
        if deg < 10:
            degfin = "00" + str(deg)
        elif deg < 100:
            degfin = "0" + str(deg)
        else:
            degfin = str(deg)
    if mins < 10:
        minsfin = "0" + str(mins)
    else:
        minsfin = str(mins)
    if sec < 10:
        secfin = "0" + str(sec)
    else:
        secfin = str(sec)
    return direction + degfin + minsfin + secfin

def SetSchengen(airport):
    # Parámetros: airport (Airport) -> objeto aeropuerto
    # Descripción: Actualiza el atributo schengen del aeropuerto según su código ICAO.

    airport.schengen = IsSchengenAirport(airport.icao)

def PrintAirport(airport):
    # Parámetros: airport (Airport) -> objeto aeropuerto a mostrar
    # Descripción: Imprime por pantalla los datos del aeropuerto. Muestra un error si el objeto no es válido.

    try:
        print("ICAO:", airport.icao)
        print("Latitude:", airport.latitude)
        print("Longitude:", airport.longitude)
        print("Schengen:", airport.schengen)
    except AttributeError:
        print("Error, invalid airport.")

def LoadAirports():
    # Parámetros: ninguno
    # Descripción: Lee el fichero Airports.txt y devuelve una lista de objetos Airport con todos los aeropuertos.

    f = open('Airports.txt', 'r')
    f.readline()
    airports = []
    line = f.readline()
    while line != '':
        if line.strip() != '':
            elements = line.split()
            a = Airport()
            a.icao = elements[0]
            a.latitude = ConvertCoordinates(elements[1])
            a.longitude = ConvertCoordinates(elements[2])
            a.schengen = IsSchengenAirport(a.icao)
            airports = airports + [a]
        line = f.readline()
    f.close()
    return airports

def SaveSchengenAirports(airport):
    # Parámetros: airport (Airport) -> objeto aeropuerto a guardar
    # Descripción: Añade un aeropuerto al fichero Airports.txt solo si es Schengen y pasa todas las validaciones. Avisa si ya existe.

    if airport is None:
        print('Input a valid airport.')
        return False
    if len(airport.icao) != 4:
        print("Invalid ICAO code")
        return False
    if not ('A' <= airport.icao[0] <= 'Z') or not ('A' <= airport.icao[1] <= 'Z') or not ('A' <= airport.icao[2] <= 'Z') or not ('A' <= airport.icao[3] <= 'Z'):
        print("Invalid Airport code")
        return False
    if airport.latitude < -90 or airport.latitude > 90:
        print("Invalid latitude")
        return False
    if airport.longitude < -180 or airport.longitude > 180:
        print("Invalid longitude")
        return False
    if not IsSchengenAirport(airport.icao):
        print("Not in Schengen.")
        return False
    full = []
    f = open(f'Airports.txt', 'r')
    line = f.readline()
    while line != "":
        full = full + [line]
        line = f.readline()
    f.close()
    i = 0
    found = False
    while i < len(full) and not found:
        elements = full[i].split(' ')
        if elements[0] == airport.icao:
            found = True
        if not found:
            i = i + 1
    if found:
        print('Airport is already on the list.')
        return found
    else:
        airportAdd = str(airport.icao) + ' ' + ReturnCoordinates(airport.latitude, True) + ' ' + ReturnCoordinates(
            airport.longitude, False)
        f = open(f'Airports.txt', 'a')
        last = full[-1].split(' ')
        if '\n' in last[-1]:
            f.write(f'{airportAdd}\n')
        else:
            f.write(f'\n{airportAdd}')
        f.close()
        print('Airport added to the list.')

def AddAirport(airport):
    # Parámetros: airport (Airport) -> objeto aeropuerto a añadir
    # Descripción: Añade cualquier aeropuerto válido al fichero Airports.txt tras validar su código ICAO y coordenadas. Avisa si ya existe.

    if airport is None:
        print('Input a valid airport.')
        return False
    if len(airport.icao) != 4:
        print("Invalid ICAO code")
        return False
    if not ('A' <= airport.icao[0] <= 'Z') or not ('A' <= airport.icao[1] <= 'Z') or not ('A' <= airport.icao[2] <= 'Z') or not ('A' <= airport.icao[3] <= 'Z'):
        print("Invalid Airport code")
        return False
    if airport.latitude < -90 or airport.latitude > 90:
        print("Invalid latitude")
        return False
    if airport.longitude < -180 or airport.longitude > 180:
        print("Invalid longitude")
        return False
    full = []
    f = open(f'Airports.txt', 'r')
    line = f.readline()
    while line != "":
        full = full + [line]
        line = f.readline()
    f.close()
    i = 0
    found = False
    while i < len(full) and not found:
        elements = full[i].split(' ')
        if elements[0] == airport.icao:
            found = True
        if not found:
            i = i + 1
    if found:
        print('Airport is already on the list.')
        return True
    else:
        airportAdd = str(airport.icao) + ' ' + ReturnCoordinates(airport.latitude, True) + ' ' + ReturnCoordinates(airport.longitude, False)
        f = open(f'Airports.txt', 'a')
        last = full[-1].split(' ')
        if '\n' in last[-1]:
            f.write(f'{airportAdd}\n')
        else:
            f.write(f'\n{airportAdd}')
        f.close()
        print('Airport added to the list.')

def RemoveAirport(airports, code):
    # Parámetros: airports (list) -> lista de objetos Airport
    #             code (str) -> código ICAO del aeropuerto a eliminar
    # Descripción: Elimina un aeropuerto de la lista y actualiza el fichero Airports.txt. Avisa si el código no existe.

    if len(airports) == 0:
        print('List is empty')
        return []

    found = False
    new_airports = []
    i = 0

    while i < len(airports):
        if airports[i].icao == code:
            found = True
        else:
            new_airports = new_airports + [airports[i]]
        i = i + 1

    if not found:
        print('The code is not indexed.')
        return

    else:
        f = open(f'Airports.txt', 'w')
        f.write("CODE LAT     LON\n")
        i = 0
        while i < len(new_airports):
            f.write(new_airports[i].icao + ' ' + ReturnCoordinates(new_airports[i].latitude, True) + ' ' + ReturnCoordinates(new_airports[i].longitude, False) + '\n')
            i = i+1
        f.close()

def PlotAirports(airports):
    # Parámetros: airports (list) -> lista de objetos Airport
    # Descripción: Genera un gráfico de barras comparando el número de aeropuertos Schengen y no Schengen.

    if len(airports) == 0:
        print('No airports found.')
        return
    fig, ax = pyplot.subplots()
    schengen = 0
    notschengen = 0
    i = 0
    while i < len(airports):
        if airports[i].schengen:
            schengen = schengen + 1
        else:
            notschengen = notschengen + 1
        i = i + 1
    ax.bar('Schengen', schengen, color='#7c3aed', label='Schengen')
    ax.bar('Not Schengen', notschengen, color='#ff5c3b', label='Not Schengen')
    ax.set_title('Schengen Airports')
    ax.set_ylabel('Count')
    return fig

def MapAirports(airports):
    # Parámetros: airports (list) -> lista de objetos Airport
    # Descripción: Genera un fichero KML con la posición de cada aeropuerto, coloreados en rojo si son Schengen y en azul si no lo son.

    if len(airports) == 0:
        print('No airports found.')
        return
    kml = open(f'Airports.kml', 'w')
    kml.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
    kml.write('<Document>\n')
    i = 0
    while i < len(airports):
        kml.write(f'<Placemark> <name>{airports[i].icao}</name>\n')
        if airports[i].schengen:
            kml.write('<Style><IconStyle><color>ff0000ff</color></IconStyle></Style>\n')
        else:
            kml.write('<Style><IconStyle><color>ffff0000</color></IconStyle></Style>\n')
        kml.write('<Point>\n')
        kml.write(f'<coordinates>{airports[i].longitude},{airports[i].latitude}</coordinates>\n')
        kml.write('</Point>\n')
        kml.write('</Placemark>\n')
        i = i+1
    kml.write('</Document>\n')
    kml.write('</kml>\n')
    kml.close()