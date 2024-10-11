import sys
import getopt
import requests
import subprocess
import time
import re

# Validar la dirección MAC con una expresión regular
def is_valid_mac(mac):
    pattern = re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$|^([0-9A-Fa-f]{2}[:-]){2}([0-9A-Fa-f]{2})$")
    return bool(pattern.match(mac))

# Consultar la API con la dirección MAC
def lookup_mac(mac_address):
    start_time = time.time()
    url = f"https://api.maclookup.app/v2/macs/{mac_address}"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            manufacturer = data.get('company', 'Not found')
        elif response.status_code == 404:
            manufacturer = "Not found"
        else:
            manufacturer = f"Error: {response.status_code}"

        # Medir el tiempo de respuesta
        response_time = int((time.time() - start_time) * 1000)
        print(f"MAC address : {mac_address}")
        print(f"Fabricante : {manufacturer}")
        print(f"Tiempo de respuesta: {response_time}ms")

    except requests.RequestException as e:
        print(f"Error al consultar la API: {e}")

# Mostrar la tabla ARP local y consultar fabricantes
def show_arp_table():
    try:
        result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
        arp_output = result.stdout.splitlines()
        print("IP/MAC/Vendor:")

        for line in arp_output:
            parts = line.split()
            if len(parts) >= 4:
                mac = parts[3]
                if ':' in mac or '-' in mac:
                    formatted_mac = mac.replace('-', ':').lower()
                    lookup_mac(formatted_mac)
    except Exception as e:
        print(f"Error al mostrar la tabla ARP: {e}")

# Mostrar el mensaje de ayuda
def show_help():
    help_message = """
    Use: python OUILookup.py --mac <mac> | --arp | [--help]
    --mac: MAC a consultar. P.e. aa:bb:cc:00:00:00.
    --arp: muestra los fabricantes de los hosts disponibles en la tabla arp.
    --help: muestra este mensaje y termina.
    """
    print(help_message)

# Función principal para procesar los argumentos de línea de comandos
def main(argv):
    try:
        opts, args = getopt.getopt(argv, "", ["mac=", "arp", "help"])
    except getopt.GetoptError as err:
        print(err)
        show_help()
        sys.exit(2)

    for opt, arg in opts:
        if opt == "--help":
            show_help()
        elif opt == "--mac":
            if is_valid_mac(arg):
                lookup_mac(arg)
            else:
                print(f"Error: El formato de la dirección MAC '{arg}' no es válido. Use el formato aa:bb:cc:dd:ee:ff.")
        elif opt == "--arp":
            show_arp_table()
        else:
            show_help()

# Punto de entrada del script
if __name__ == "__main__":
    main(sys.argv[1:])
