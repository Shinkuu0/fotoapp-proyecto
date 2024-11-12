from PIL import Image, ImageEnhance, ImageFilter
import matplotlib.pyplot as plt
import numpy as np
import os
import urllib.request
from PIL import Image
from io import BytesIO

def descargar_imagen(url):
    """
    Descargar una imagen desde una URL utilizando urllib.
    """
    try:
        # Descargar la imagen desde la URL
        with urllib.request.urlopen(url) as url_response:
            imagen = Image.open(BytesIO(url_response.read()))
        
        return imagen

    except Exception as e:
        print(f"Error al descargar la imagen: {e}")
        raise


def redimensionar_para_red(ruta_imagen, red_social):
    """Redimensiona la imagen a las dimensiones recomendadas por la red social."""
    try:
        # Verifica si la ruta de la imagen existe
        if not os.path.exists(ruta_imagen):
            raise ValueError("La ruta de la imagen no existe")

        dimensiones = {
            "youtube": (1280, 720),
            "instagram": (1080, 1080),
            "twitter": (1200, 675),
            "facebook": (1200, 630)
        }

        red_social = red_social.lower()
        if red_social not in dimensiones:
            raise ValueError(f"Red social no soportada. Opciones válidas: {list(dimensiones.keys())}")

        # Abre la imagen
        imagen = Image.open(ruta_imagen)
        ancho_objetivo, alto_objetivo = dimensiones[red_social]

        # Calcula la relación de aspecto original y objetivo
        ratio_original = imagen.width / imagen.height
        ratio_objetivo = ancho_objetivo / alto_objetivo

        # Redimensiona la imagen manteniendo la relación de aspecto
        if ratio_original > ratio_objetivo:
            nuevo_ancho = ancho_objetivo
            nuevo_alto = int(nuevo_ancho / ratio_original)
        else:
            nuevo_alto = alto_objetivo
            nuevo_ancho = int(nuevo_alto * ratio_original)

        # Redimensiona la imagen y la coloca en un fondo blanco
        imagen_redimensionada = imagen.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)
        imagen_final = Image.new("RGB", dimensiones[red_social], (255, 255, 255))
        offset = ((ancho_objetivo - nuevo_ancho) // 2, (alto_objetivo - nuevo_alto) // 2)
        imagen_final.paste(imagen_redimensionada, offset)

        # Guarda la imagen redimensionada
        nombre_salida = f"redimensionada_{red_social}_{os.path.basename(ruta_imagen)}"
        imagen_final.save(nombre_salida)

        return imagen_final, nombre_salida

    except Exception as e:
        print(f"Error al procesar la imagen: {str(e)}")
        raise


def ajustar_contraste(ruta_imagen):
    """Ajusta el contraste de la imagen utilizando su histograma."""
    try:
        # Verifica si la ruta de la imagen existe
        if not os.path.exists(ruta_imagen):
            raise ValueError("La ruta de la imagen no existe")

        imagen = Image.open(ruta_imagen)

        # Si la imagen está en RGB, aplica la ecualización al canal Y (brillo)
        if imagen.mode == 'RGB':
            imagen_ycbcr = imagen.convert('YCbCr')
            canales = list(imagen_ycbcr.split())

            canal_y = np.array(canales[0])
            hist, bins = np.histogram(canal_y.flatten(), 256, [0, 256])
            cdf = hist.cumsum()
            cdf_normalizado = cdf * float(hist.max()) / cdf.max()

            lookup_table = np.interp(canal_y.flatten(), bins[:-1], cdf_normalizado)
            canales[0] = Image.fromarray(lookup_table.reshape(canal_y.shape).astype('uint8'))

            imagen_final = Image.merge('YCbCr', canales).convert('RGB')
        else:
            imagen_array = np.array(imagen)
            hist, bins = np.histogram(imagen_array.flatten(), 256, [0, 256])
            cdf = hist.cumsum()
            cdf_normalizado = cdf * float(hist.max()) / cdf.max()

            lookup_table = np.interp(imagen_array.flatten(), bins[:-1], cdf_normalizado)
            imagen_final = Image.fromarray(lookup_table.reshape(imagen_array.shape).astype('uint8'))

        # Guarda la imagen con el contraste ajustado
        nombre_salida = f"contraste_ajustado_{os.path.basename(ruta_imagen)}"
        imagen_final.save(nombre_salida)

        return imagen_final, nombre_salida

    except Exception as e:
        print(f"Error al ajustar el contraste: {str(e)}")
        raise


def aplicar_filtro(imagen, opcion_filtro):
    """Aplica un filtro seleccionado por número (incluyendo la opción 'original')."""
    try:
        filtros = {
            1: 'original',   # Opción para mantener la imagen original
            2: ImageFilter.BLUR,
            3: ImageFilter.CONTOUR,
            4: ImageFilter.DETAIL,
            5: ImageFilter.EDGE_ENHANCE,
            6: ImageFilter.EDGE_ENHANCE_MORE,
            7: ImageFilter.EMBOSS,
            8: ImageFilter.FIND_EDGES,
            9: ImageFilter.SHARPEN,
            10: ImageFilter.SMOOTH
        }

        # Si se selecciona la opción 1 (original), simplemente devolvemos la imagen sin cambios
        if opcion_filtro == 1:
            return imagen

        # Si no es la opción "original", aplicamos el filtro correspondiente
        if opcion_filtro in filtros:
            imagen_filtrada = imagen.filter(filtros[opcion_filtro])
            return imagen_filtrada
        else:
            raise ValueError("Opción de filtro no válida")

    except Exception as e:
        print(f"Error al aplicar el filtro: {str(e)}")
        raise


def boceto_persona(ruta_imagen, persona=True):
    """Crea un boceto de una persona en la imagen usando bordes y ajuste de contraste."""
    try:
        # Verifica si la ruta de la imagen existe
        if not os.path.exists(ruta_imagen):
            raise ValueError("La ruta de la imagen no existe")

        if not persona:
            raise ValueError("La imagen no contiene una persona")

        imagen = Image.open(ruta_imagen)

        # Convierte la imagen a escala de grises y encuentra los bordes
        imagen_gris = imagen.convert('L')
        bordes = imagen_gris.filter(ImageFilter.FIND_EDGES)

        # Aumenta el contraste y el brillo
        enhancer = ImageEnhance.Contrast(bordes)
        boceto = enhancer.enhance(2.0)
        boceto = ImageEnhance.Brightness(boceto).enhance(2.0)

        # Guarda la imagen del boceto
        nombre_salida = f"boceto_{os.path.basename(ruta_imagen)}"
        boceto.save(nombre_salida)

        return boceto, nombre_salida

    except Exception as e:
        print(f"Error al crear el boceto: {str(e)}")
        raise


def menu_principal():
    while True:
        print("\n=== FotoApp Menu ===")
        print("1. Redimensionar para red social")
        print("2. Ajustar contraste")
        print("3. Aplicar filtro")
        print("4. Crear boceto artístico")
        print("5. Salir")

        try:
            opcion = input("\nElige una opción (1-5): ")

            if opcion == "5":
                print("¡Gracias por usar FotoApp!")
                break

            url_imagen = input("Ingresa la URL de la imagen: ")
            imagen = descargar_imagen(url_imagen)

            if opcion == "1":
                red_social = input("Ingresa la red social (Youtube/Instagram/Twitter/Facebook): ")
                imagen = redimensionar_para_red(imagen, red_social)
                imagen.show()

            elif opcion == "2":
                imagen = ajustar_contraste(imagen)
                imagen.show()

            elif opcion == "3":
                print("\nFiltros disponibles:")
                print("1. Original")
                print("2. Blur")
                print("3. Contour")
                print("4. Detail")
                print("5. Edge Enhance")
                print("6. Edge Enhance More")
                print("7. Emboss")
                print("8. Find Edges")
                print("9. Sharpen")
                print("10. Smooth")
                opcion_filtro = int(input("Selecciona el número del filtro (1-10): "))
                imagen = aplicar_filtro(imagen, opcion_filtro)
                imagen.show()

            elif opcion == "4":
                respuesta = input("¿La imagen contiene una persona? (s/n): ").lower()
                persona = respuesta == 's'
                imagen = boceto_persona(imagen, persona)
                imagen.show()

            else:
                print("Opción no válida. Por favor elige una opción entre 1 y 5.")

        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Ocurrió un error inesperado: {e}")

menu_principal()
