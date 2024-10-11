import sys           # Para manejar argumentos de línea de comandos
import getopt        # Para el procesamiento de argumentos del script
import requests      # Para realizar solicitudes HTTP a la API de consulta de MACs
import subprocess    # Para ejecutar comandos del sistema, como la consulta a la tabla ARP
import time          # Para medir el tiempo de respuesta de las solicitudes
import re            # Para validar el formato de las direcciones MAC con expresiones regulares

# Función para validar la dirección MAC


def is_valid_mac(mac):

    # Esta función utiliza una expresión regular para validar el formato de la dirección MAC.
    # Formatos válidos: aa:bb:cc:dd:ee:ff o aa-bb-cc-dd-ee-ff.
    # Retorna True si la dirección es válida, de lo contrario, False.

    # Expresion regular para validar MAC con separadores ":" o "-"
    pattern = re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$|^([0-9A-Fa-f]{2}[:-]){2}([0-9A-Fa-f]{2})$")
    return bool(pattern.match(mac))

# Funcion para consultar la API con la dirección MAC proporcionada


def lookup_mac(mac_address):

    # Realiza una consulta a la API utilizando la dirección MAC proporcionada.
    # Muestra el fabricante si se encuentra en la base de datos, y el tiempo de respuesta.

    start_time = time.time()  # Tiempo inicial para medir la duración de la solicitud
    url = f"https://api.maclookup.app/v2/macs/{mac_address}"  # URL de la API con la MAC

    try:
        # Realiza la solicitud a la API usando GET
        response = requests.get(url)

        # Si la solicitud fue exitosa, procesa la respuesta
        if response.status_code == 200:
            data = response.json()  # Extrae la respuesta en formato JSON
            manufacturer = data.get('company', 'Not found')  # Obtiene el nombre del fabricante
        elif response.status_code == 404:
            manufacturer = "Not found"  # Caso de dirección MAC no encontrada
        else:
            manufacturer = f"Error: {response.status_code}"  # Otros códigos de error

        # Calcula el tiempo de respuesta en milisegundos
        response_time = int((time.time() - start_time) * 1000)

        # Imprime los resultados de la consulta
        print(f"MAC address : {mac_address}")
        print(f"Fabricante : {manufacturer}")
        print(f"Tiempo de respuesta: {response_time}ms")

    except requests.RequestException as e:
        # Muestra un error en caso de que falle la consulta HTTP
        print(f"Error al consultar la API: {e}")

# Función para mostrar los dispositivos de la tabla ARP local


def show_arp_table():

    # Obtiene la tabla ARP del sistema local para mostrar las direcciones IP y MAC de los dispositivos conectados.
    # Consulta la API para obtener el nombre de los fabricantes de las MAC encontradas.

    try:
        # Ejecuta el comando ARP para obtener la tabla local
        result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
        arp_output = result.stdout.splitlines()  # Divide la salida en líneas individuales

        print("IP/MAC/Vendor:")

        # Procesa cada línea de la salida de la tabla ARP
        for line in arp_output:
            parts = line.split()
            if len(parts) >= 4:
                mac = parts[3]  # Obtiene la dirección MAC de la línea
                if ':' in mac or '-' in mac:  # Revisa si es una MAC válida
                    formatted_mac = mac.replace('-', ':').lower()
                    lookup_mac(formatted_mac)  # Consulta el fabricante de la MAC

    except Exception as e:
        print(f"Error al mostrar la tabla ARP: {e}")

# Función para mostrar la ayuda del script


def show_help():

    # Muestra el mensaje de ayuda del script con la descripción de cada parámetro.

    help_message = """
    Uso: python OUILookup.py --mac <mac> | --arp | [--help]
    --mac: Dirección MAC deseada para consultar. Ejemplo: aa:bb:cc:00:00:00.
    --arp: Muestra los fabricantes de los hosts disponibles en la tabla ARP.
    --help: Muestra este mensaje y termina.
    """
    print(help_message)

# Función principal para gestionar los argumentos de línea de comandos


def main(argv):

    # Función principal que procesa los argumentos de línea de comandos y llama a las funciones correspondientes.

    try:
        # Lee los argumentos del script y define las opciones válidas
        opts, args = getopt.getopt(argv, "", ["mac=", "arp", "help"])

    except getopt.GetoptError as err:
        print(err)
        show_help()
        sys.exit(2)  # Salida con error

    # Itera sobre las opciones proporcionadas
    for opt, arg in opts:
        if opt == "--help":
            show_help()  # Muestra la ayuda y termina
        elif opt == "--mac":
            if is_valid_mac(arg):
                lookup_mac(arg)  # Consulta la dirección MAC proporcionada
            else:
                print(f"Error: El formato de la dirección MAC '{arg}' no es válido. Use el formato aa:bb:cc:dd:ee:ff.")
        elif opt == "--arp":
            show_arp_table()  # Muestra la tabla ARP
        else:
            show_help()  # Muestra la ayuda si se ingresa una opción inválida

# Punto de entrada del script


if __name__ == "__main__":

    main(sys.argv[1:])  # Llama a la función principal con los argumentos proporcionados
