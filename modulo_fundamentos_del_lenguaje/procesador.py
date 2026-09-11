import json
import re


def procesar_datos(ruta_archivo):
    # OBJETIVO: Expresiones regulares (Regex) para validar formato de email
    patron_email = r"^[\w\.-]+@[\w\.-]+\.\w+$"

    # OBJETIVO: Colecciones (Lista para guardar nombres y variables para agregar datos)
    total_ventas = 0
    vendedores_validos = []

    # OBJETIVO: Manejo de errores y excepciones robusto (try-except)
    try:
        with open(ruta_archivo, "r", encoding="utf-8") as archivo:
            # Lee el JSON (esto nos da una Lista de Diccionarios)
            datos = json.load(archivo)

    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{ruta_archivo}'.")
        return
    except json.JSONDecodeError:
        print("Error: El archivo no tiene un formato JSON válido.")
        return
    except Exception as e:
        print(f"Error inesperado: {e}")
        return

    # OBJETIVO: Control de flujo (for) para iterar la lista
    for usuario in datos:
        nombre = usuario.get("nombre", "Desconocido")
        email = usuario.get("email", "")
        rol = usuario.get("rol", "invitado")
        ventas = usuario.get("ventas", 0)

        # Filtro: Validar email con la expresión regular
        if not re.match(patron_email, email):
            print(f"Advertencia: Email inválido ignorado -> {nombre} ({email})")
            continue  # Salta a la siguiente iteración del for

        # OBJETIVO: Pattern Matching (El equivalente a "switch" en Python 3.10+)
        match rol:
            case "admin":
                print(f"Admin detectado: {nombre}, acceso total.")

            case "vendedor" if ventas > 100:  # Pattern matching con condición extra
                print(f"Vendedor estrella: {nombre} (Ventas: {ventas})")
                total_ventas += ventas
                vendedores_validos.append(nombre)

            case "vendedor":
                print(f"Vendedor normal: {nombre} (Ventas: {ventas})")
                total_ventas += ventas
                vendedores_validos.append(nombre)

            case _:  # Caso por defecto (el equivalente a 'default')
                print(f"Rol sin permisos de venta: {nombre}")

    # Mostrar la agregación de datos
    print("\n--- Resumen de la Operación ---")
    print(f"Total de ventas válidas: {total_ventas}")
    print(f"Vendedores procesados correctamente: {vendedores_validos}")


# Ejecutar la función
if __name__ == "__main__":
    procesar_datos("datos.json")
