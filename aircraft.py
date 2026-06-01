from airport import *
import math as math


class Aircraft:
    def __init__(self):
        self.id = ""
        self.company = ""
        self.origin = ""
        self.time = "00:00"


# Clase que representa un avión con sus atributos: id, aerolínea, origen y hora de llegada.

def GoodTimeFormat(time):
    # Parámetros: time (str) -> cadena con la hora a validar
    # Descripción: Valida que una cadena tenga formato de hora correcto (HH:MM). Devuelve True o False.
    try:
        if time == '':
            return False
        time = time.split(':')
        if len(time) != 2:
            return False
        if len(time[0]) != 2:
            return False
        if len(time[1]) != 2:
            return False

        hour = int(time[0])
        minute = int(time[1])
        if hour < 0 or hour > 23:
            return False
        if minute < 0 or minute > 59:
            return False
        else:
            return True
    except ValueError:
        return False


def LoadArrivals():
    # Parámetros: ninguno
    # Descripción: Lee el fichero Arrivals.txt y devuelve una lista de objetos Aircraft con los datos de cada vuelo.
    arrivals = []
    try:
        f = open('Arrivals.txt', 'r')
        f.readline()
        line = f.readline()
        while line != '':
            data = line.split()
            if len(data) == 4 and GoodTimeFormat(data[2]):
                a = Aircraft()
                a.id = data[0]
                a.time = data[2]
                a.origin = data[1]
                a.company = data[3]
                arrivals = arrivals + [a]
            line = f.readline()
        f.close()
        return arrivals
    except FileNotFoundError:
        return []


def PlotArrivals(aircrafts):
    # Parámetros: aircrafts (list) -> lista de objetos Aircraft
    # Descripción: Genera un gráfico de barras con el número de aterrizajes por hora del día.
    if len(aircrafts) == 0:
        print('List is empty')
        return
    fig, ax = pyplot.subplots()
    count = [0] * 24
    i = 0
    while i < len(aircrafts):
        hour = int(aircrafts[i].time.split(':')[0])
        count[hour] = count[hour] + 1
        i = i + 1
    ax.bar(range(24), count, color="#d4664b")
    ax.set_title('Landing Frequency')
    ax.set_xlabel('Hour')
    ax.set_ylabel('Number of landings')
    return fig


def SaveFlights(aircrafts):
    # Parámetros: aircrafts (list) -> lista de objetos Aircraft
    # Descripción: Guarda la lista de vuelos en el fichero Arrivals.txt, usando '-' para los campos vacíos.
    if len(aircrafts) == 0:
        print('List or File is empty')
    f = open(f'Arrivals.txt', 'w')
    i = 0
    f.write('AIRCRAFT ORIGIN ARRIVAL AIRLINE\n')
    while i < len(aircrafts):
        if aircrafts[i].id != '':
            aid = aircrafts[i].id
        else:
            aid = '-'
        if aircrafts[i].time != '':
            time = aircrafts[i].time
        else:
            time = '-'
        if aircrafts[i].origin != '':
            origin = aircrafts[i].origin
        else:
            origin = '-'
        if aircrafts[i].company != '':
            company = aircrafts[i].company
        else:
            company = '-'
        f.write(aid + ' ' + origin + ' ' + time + ' ' + company + '\n')
        i = i + 1
    f.close()


def PlotAirlines(aircrafts):
    # Parámetros:aircrafts (list) -> lista de objetos de aircraft
    # Descripción: Genera un gráfico de barras con el número de vuelos llegados por cada aeroliea
    if len(aircrafts) == 0:
        print('List is empty')
        return
    fig, ax = pyplot.subplots()
    different = []
    count = []
    d = 0
    while d < len(aircrafts):
        current = aircrafts[d].company
        i = 0
        found = False
        while not found and i < len(different):
            if different[i] == current:
                found = True
                count[i] = count[i] + 1
            i = i + 1
        if not found:
            different = different + [current]
            count = count + [1]
        d = d + 1
    ax.bar(different, count, color="#d4664b")
    ax.set_title('Airline Flights')
    ax.set_xlabel('Airlines')
    ax.set_ylabel('Number of arriving aircraft')
    ax.tick_params(axis='x', rotation=90)
    return fig


def PlotFlightsType(aircrafts):
    # Parámetros: aircrafts (list) -> lista de objetos Aircraft
    # Descripción: Genera un gráfico comparando cuántos vuelos provienen de la zona Schengen y cuántos de fuera.
    if len(aircrafts) == 0:
        print('List is empty')
        return
    fig, ax = pyplot.subplots()
    schengen = 0
    notschengen = 0
    i = 0
    while i < len(aircrafts):
        code = aircrafts[i].origin
        if IsSchengenAirport(code):
            schengen = schengen + 1
        else:
            notschengen = notschengen + 1
        i = i + 1
    ax.bar('Schengen', schengen, color='#d4664b', label='Schengen')
    ax.bar('Not Schengen', notschengen, color='#ff5c3b', label='Not Schengen')
    ax.set_title('Arrival Origin')
    ax.set_ylabel('Count')
    ax.legend()
    return fig


def DegreesToRadians(degrees):  # Había otra funcion que ya donde ya se tenia los vuelos en grados?
    # Parámetros: degrees (float) -> ángulo en grados
    # Descripción: Convierte un ángulo de grados a radianes.
    return degrees * (math.pi / 180)


def HaversineDistance(lat1, lon1, lat2, lon2):
    # Parámetros: lat1, lon1 (float) -> coordenadas del punto de origen
    #             lat2, lon2 (float) -> coordenadas del punto de destino
    # Descripción: Calcula la distancia en km entre dos coordenadas geográficas usando la fórmula de Haversine.
    RadioTierra = 6371.0  # KM

    rlat1 = DegreesToRadians(lat1)
    rlon1 = DegreesToRadians(lon1)
    rlat2 = DegreesToRadians(lat2)
    rlon2 = DegreesToRadians(lon2)

    diferencia_lat = rlat2 - rlat1
    diferencia_lon = rlon2 - rlon1
    # Usamos la formula del HAversine este

    a = (math.sin(diferencia_lat / 2) ** 2 + math.cos(rlat1) * math.cos(rlat2) * math.sin(diferencia_lon / 2) ** 2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = RadioTierra * c
    return distance


def FindAirports(airports, code):
    # Parámetros: airports (list) -> lista de objetos aeropuerto
    #             code (str) -> código ICAO a buscar
    # Descripción: Busca y devuelve un aeropuerto de la lista por su código ICAO, o None si no existe.
    i = 0
    while i < len(airports):
        if airports[i].icao == code:
            return airports[i]
        i += 1
    return None


def MapFlights(aircrafts):
    # Parámetros: aircrafts (list) -> lista de objetos Aircraft
    # Descripción: Genera un fichero KML con las trayectorias de cada vuelo desde su origen hasta Barcelona,
    #              coloreadas en azul si son Schengen y en rojo si no lo son.
    if len(aircrafts) == 0:
        print('List is empty')
        return
    # Escribimos las coordenadas de LEBL
    LEBLlon = 2.07833
    LEBLlat = 41.29694
    airports = LoadAirports()
    kml = open('Flights.kml', 'w')
    kml.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
    kml.write('<Document>\n')

    i = 0
    while i < len(aircrafts):
        codigoorigen = aircrafts[i].origin
        AeropuertoOrigen = FindAirports(airports, codigoorigen)
        if AeropuertoOrigen != None:
            origenlat = AeropuertoOrigen.latitude
            origenlon = AeropuertoOrigen.longitude
            # Pillamos codigo para determinar si Schengen o no, discutir colores luego
            if IsSchengenAirport(codigoorigen):
                color = 'ffff0000'  # Azul
            else:
                color = '#ff0000ff'  # Rojo
            # Trayectoria/linea de origen a destino
            kml.write('<Placemark>\n')
            kml.write('<name>' + aircrafts[i].id + '</name>\n')
            kml.write('<Style>\n')
            kml.write('  <LineStyle>\n')
            kml.write('    <color>' + color + '</color>\n')
            kml.write('    <width>2</width>\n')
            kml.write('  </LineStyle>\n')
            kml.write('</Style>\n')
            kml.write('<LineString>\n')
            kml.write('  <altitudeMode>clampToGround</altitudeMode>\n')
            kml.write('  <tessellate>1</tessellate>\n')
            kml.write('  <coordinates>\n')

            kml.write('  ' + str(origenlon) + ',' + str(origenlat) + '\n')
            kml.write('  ' + str(LEBLlon) + ',' + str(LEBLlat) + '\n')
            kml.write('  </coordinates>\n')
            kml.write('</LineString>\n')
            kml.write('</Placemark>\n')
        i += 1
    kml.write('</Document>\n')
    kml.write('</kml>\n')
    kml.close()
    print('Flights.kml generated with ' + str(len(aircrafts)) + ' trajectories.')


def LongDistanceArrivals(aircrafts):
    # Parámetros: aircrafts (list) -> lista de objetos Aircraft
    # Descripción: Filtra y devuelve solo los vuelos cuyo aeropuerto de origen está a más de 2000 km de Barcelona.
    if len(aircrafts) == 0:
        print('List is empty')
        return
    i = 0
    # Escribimos las coordenadas de LEBL
    LEBLlon = 2.07833
    LEBLlat = 41.29694

    # Utilizamos la condicion de 2000KM
    limite = 2000.0
    airports = LoadAirports()
    mayorlimite = []
    while i < len(aircrafts):
        origincode = aircrafts[i].origin
        originairport = FindAirports(airports, origincode)
        if originairport != None:
            dist = HaversineDistance(originairport.latitude, originairport.longitude, LEBLlat, LEBLlon)
            if dist > limite:
                mayorlimite.append(aircrafts[i])
        i += 1
    return mayorlimite


# Leemos el fichero de salidas línea por línea, y por cada línea válida crea un objeto Aircraft rellenando solo los campos de salida (id, destination, dep_time, company).
# Si el fichero no existe devuelve una lista vacía y un código de error -1.
def LoadDepartures(filename):
    departures = []
    try:
        f = open(filename, 'r')
    except FileNotFoundError:
        return [], -1
    f.readline()  # skip header
    line = f.readline()
    while line != '':
        data = line.split()
        if len(data) == 4 and GoodTimeFormat(data[2]):
            a = Aircraft()
            a.id = data[0]
            a.destination = data[1]
            a.dep_time = data[2]
            a.company = data[3]
            departures = departures + [a]
        line = f.readline()
    f.close()
    return departures


def MergeMovements(arrivals, departures):
    if len(arrivals) == 0 or len(departures) == 0:
        return -1
    merged = []
    # Copiamos llegadas en la lista merged
    i = 0
    while i < len(arrivals):
        a = Aircraft()
        a.id = arrivals[i].id
        a.company = arrivals[i].company
        a.origin = arrivals[i].origin
        a.time = arrivals[i].time
        a.destination = arrivals[i].destination
        a.dep_time = arrivals[i].dep_time
        merged = merged + [a]
        i = i + 1
    # Igualamos llegadas con salidad
    d = 0
    while d < len(departures):
        matched = False
        m = 0
        while m < len(merged):
            same_id = merged[m].id == departures[d].id
            has_arrival = merged[m].time != "00:00"
            no_departure = merged[m].dep_time == "00:00"
            arr_before_dep = merged[m].time < departures[d].dep_time
            if same_id and has_arrival and no_departure and arr_before_dep:
                merged[m].destination = departures[d].destination
                merged[m].dep_time = departures[d].dep_time
                matched = True
                break
            m = m + 1
        # Si No podemos encajar una llegada con un salidad eso significa que es un vuelo nocturno veamos la section 4 del proyecto que nos dice
        # que estos vuelo son nocturnos, salen pero no vuelven en el dia

        if not matched:
            a = Aircraft()
            a.id = departures[d].id
            a.company = departures[d].company
            a.destination = departures[d].destination
            a.dep_time = departures[d].dep_time
            merged = merged + [a]
        d = d + 1
    return merged


# Basicamente recorremos todas las salidas hasta encotrAR una llegada con el mismo id cuya hora de llegada sea
# antes y los fusionas en uno solo, si no añade el avion como avion nocturno

def NightAircraft(aircrafts):
    if len(aircrafts) == 0:
        return -1
    night = []
    i = 0
    while i < len(aircrafts):
        if aircrafts[i].time == "00:00" and aircrafts[i].dep_time != "00:00":
            night = night + [aircrafts[i]]
        i = i + 1
    return night
# Esta funcion es mas sencilla creamos lista night y hacemos que vaya añadiendo aviones que sean nocturnos
# Es decir que no tenga llegadas, porque o paso la noche en LEBL o salió muy tarde sin volver
