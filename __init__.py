# -*- coding: utf-8 -*-
"""Recomendación de destinos - Proyecto Sistemas Basados en Conocimiento.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1K8X6wE7yomSpUyE_EpHwHS5prXcF2Y5T

# Sistema Basado en Conocimientos para Planificación de Vacaciones

Hellen Aguilar Noguera

José Leonardo Araya Parajeles

Fernando Rojas Meléndez

Alejandro Villalobos Hernández

*Universidad CENFOTEC*

TODOS:
- Generar más datos con APIs (opcional) -> Leonardo
- Hacer un Docker file -> Alejandro o algo para que no haya que tener que subir el archivo para ejecutarlo o usar google drive -> Fernando
- Documentar mejor (tal vez en uno de estas secciones de texto) cuales son nuestras reglas, por ejemplo usar logica difusa, y el orden que se ejecutan -> Hellen
- Diagrama de conocimiento: este es un diagrama que detalla los criterios de inferencia, tales como reglas importantes, umbrales o árboles de probabilidad que aplican para la inferencia. -> Alejandro
- Agregar ejemplos documentados del script "Ejemplos: se deben facilitar ejemplos para verificar el funcionamiento y
reproducir el trabajo hecho hasta el punto del avance." Ejemplos de inputs para recomendacion. -> Fernando
- Modificar el documento de diseño (overleaf) con las nuevas adiciones https://www.overleaf.com/5719863953rtbvbmnhmpyn#d61ea3 -> Fernando

Limpieza de datos
===========================
Primero limpiamos y cambiamos el data set para que tenga más sentido para lo que queremos. El data set inicial es sobre detalles de viajes. Vamos a tomarlo como base para crear una base de datos de destinos y presupuestos para recomendaciones
"""

# import pandas as pd
# import re

# # Función para limpiar valores de costo eliminando caracteres no numéricos y convirtiendo a float
# def clean_cost(cost):
#     if pd.isna(cost):
#         return None
#     cleaned = re.sub(r'[^\d.]', '', str(cost))  # Elimina caracteres no numéricos excepto el punto decimal
#     try:
#         return float(cleaned)
#     except ValueError:
#         return None

# # Cargar el conjunto de datos original (reemplaza 'tu_archivo.csv' con la ruta real del archivo)
# df = pd.read_csv('Travel details dataset.csv')

# # Limpiar las columnas de costos
# df['Accommodation cost'] = df['Accommodation cost'].apply(clean_cost)
# df['Transportation cost'] = df['Transportation cost'].apply(clean_cost)

# # Extraer el mes de la columna Start date
# df['Month'] = pd.to_datetime(df['Start date']).dt.month

# # Estandarizar el tipo de transporte
# df['Transportation type'] = df['Transportation type'].str.lower().str.strip()
# df['Transportation type'] = df['Transportation type'].replace({'plane': 'flight', 'airplane': 'flight'})

# # Filtrar solo los viajes con transporte en avión
# df = df[df['Transportation type'] == 'flight']

# # Eliminar filas con valores faltantes en columnas esenciales
# essential_columns = [
#     'Destination', 'Month', 'Duration (days)', 'Traveler gender',
#     'Traveler nationality', 'Accommodation type', 'Accommodation cost',
#     'Transportation cost'
# ]
# df = df.dropna(subset=essential_columns)

# # Seleccionar columnas relevantes para el nuevo conjunto de datos
# new_dataset = df[[
#     'Destination', 'Month', 'Duration (days)', 'Traveler gender',
#     'Traveler nationality', 'Accommodation type', 'Accommodation cost',
#     'Transportation cost'
# ]]

# # Guardar el nuevo conjunto de datos en un archivo CSV
# new_dataset.to_csv('cleaned_travel_dataset.csv', index=False)

# # Mostrar las primeras filas para verificar
# print(new_dataset.head())

# from google.colab import drive
# drive.mount('/content/drive')

"""'''
Módulo base_conocimiento.py (Reglas)
===========================
Este módulo contiene la implementación de la Base de Conocimientos del sistema basado en conocimientos (KBS).
Se encarga de almacenar y aplicar reglas de recomendación de destinos en función de criterios como presupuesto,
duración del viaje, mes de viaje y preferencias de hospedaje.


Método de Similitud Utilizado:
------------------------------
Este sistema utiliza **similitud de coseno** para recomendar destinos de viaje.
Matemáticamente, la similitud de coseno se define como:

    similarity(A, B) = (A ⋅ B) / (||A|| ||B||)

Donde:
- **A** es el vector de entrada del usuario con atributos normalizados (`presupuesto`, `duración promedio`, `mes`).
- **B** es cada destino en el dataset, también normalizado.
- **A ⋅ B** es el producto punto de los vectores.
- **||A||** y **||B||** son las normas euclidianas de los vectores.

Este método mide qué tan similares son dos puntos en el espacio, considerando solo la dirección y no la magnitud.
En este caso, en lugar de realizar un filtrado estricto, el sistema encuentra los destinos más similares al perfil
 del usuario en términos de costos, duración y fecha del viaje.
'''
"""

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import json
import Rule as rl

class BaseConocimiento:
    """
    Clase que representa la Base de Conocimientos del sistema.
    Permite recomendar destinos similares a los criterios ingresados por el usuario
    en base a una métrica de similitud en vez de aplicar reglas estrictas.
    """


    def __init__(self, travel_data):
        """
        Inicializa la base de conocimientos con el dataset de viajes.

        Parámetros:
        - travel_data (DataFrame): DataFrame de pandas con la información de viajes.
        """

        # Travel Data es el CSV (Limpio)
        self.travel_data = travel_data.copy()

        # Calculamos el costo total del viaje sumando alojamiento y transporte
        self.travel_data["Total cost"] = (
            self.travel_data["Accommodation cost"] + self.travel_data["Transportation cost"]
        )

        # Normalizamos los datos numéricos para compararlos adecuadamente
        self.scaler = MinMaxScaler()
        self.normalized_data = self.scaler.fit_transform(
            self.travel_data[["Total cost", "Duration (days)", "Month"]]
        )

        self.rules = self.load_rules()
        print("Reglas cargadas.")

        print("Base de conocimientos inicializada.")

    def load_rules(self):
        rules_file = "rules.json"
        with open(rules_file, "r") as f:
            rules_config = json.load(f)["rules"]

        rules = []
        for rule in rules_config:
            if rule["type"] == "cosine_similarity":
                rules.append(rl.CosineSimilarityRule(self.scaler, self.normalized_data))
            elif rule["type"] == "threshold":
                rules.append(rl.ThresholdRule(rule["threshold"], rule["column_name"]))
            elif rule["type"] == "equality":
                rules.append(rl.EqualityRule(rule["column_name"]))
        return rules

    def calcular_similitud(self, presupuesto, duracion_min, duracion_max, mes):
        # """
        # Calcula la similitud entre los destinos en el dataset y la entrada del usuario
        # usando la distancia de coseno.
        # """
        # print("Calculando similitud...")
        # # Promediamos la duración mínima y máxima del usuario para calcular similitud
        # user_input = pd.DataFrame([[presupuesto, (duracion_min + duracion_max) / 2, mes]],
        #                       columns=["Total cost", "Duration (days)", "Month"])
        # user_input_scaled = self.scaler.transform(user_input)
        # print("Datos normalizados del usuario")

        # # Calculamos la similitud entre la entrada del usuario y los datos normalizados
        # similitudes = cosine_similarity(user_input_scaled, self.normalized_data)[0]

        # print("Similitud calculada.")
        # return similitudes
        
        user_input = [presupuesto, (duracion_min + duracion_max) / 2, mes]
        results = [rule.apply(user_input, self.travel_data) for rule in self.rules]

        # Combinar los resultados de las reglas. Verificar si es la agregación adecuada. TODO
        return np.mean(results, axis=0)

    def recomendar_destinos(self, presupuesto, duracion_min, duracion_max, mes, tipo_hospedaje=None):
        """
        Recomienda destinos similares a las preferencias del usuario usando distancia de coseno.

        Parámetros:
        - presupuesto (float): Presupuesto máximo del usuario.
        - duracion_min (int): Duración mínima del viaje en días.
        - duracion_max (int): Duración máxima del viaje en días.
        - mes (int): Mes en el que el usuario desea viajar (1-12).
        - tipo_hospedaje (str, opcional): Tipo de hospedaje preferido por el usuario.

        Retorna:
        - DataFrame con los destinos recomendados y su nivel de similitud con las preferencias del usuario.
        """
        # Obtenemos las similitudes para cada destino
        self.travel_data["Similarity"] = self.calcular_similitud(presupuesto, duracion_min, duracion_max, mes)

        # Filtrar destinos que no excedan el presupuesto del usuario
        #destinos_filtrados = self.travel_data[self.travel_data["Total cost"] <= presupuesto]
        destinos_filtrados = self.travel_data
        
        # Si no hay destinos dentro del presupuesto, retornamos un DataFrame vacío.
        if destinos_filtrados.empty:
            print("No hay destinos dentro del presupuesto ingresado.")
            return pd.DataFrame()

        # Ordenamos los destinos según la similitud calculada
        destinos_recomendados = destinos_filtrados.sort_values(by="Similarity", ascending=False)

        # Si el usuario tiene una preferencia de hospedaje, filtramos los resultados
        if tipo_hospedaje:
            destinos_recomendados = destinos_recomendados[destinos_recomendados["Accommodation type"] == tipo_hospedaje]

        return destinos_recomendados[["Destination", "Total cost", "Duration (days)", "Accommodation type", "Similarity"]].head(6)

"""'''
Módulo base_hechos.py
===========================
Este módulo maneja la Base de Hechos del sistema basado en conocimientos (KBS).
Almacena los datos ingresados por los usuarios, como presupuesto, preferencias y fechas de viaje.
'''
"""

class BaseHechos:
    """
    Clase que representa la Base de Hechos del sistema.
    Almacena la información del usuario para personalizar las recomendaciones.
    """

    def __init__(self):
        """
        Inicializa la base de hechos con datos vacíos.
        """
        self.hechos = {}

    def ingresar_datos_usuario(self):
        """
        Solicita y almacena interactivamente los datos ingresados por el usuario.
        """
        self.hechos["presupuesto"] = float(input("Ingrese su presupuesto en USD: "))
        self.hechos["duracion_min"] = int(input("Ingrese la duración mínima del viaje en días: "))
        self.hechos["duracion_max"] = int(input("Ingrese la duración máxima del viaje en días: "))
        self.hechos["mes"] = int(input("Ingrese el mes en el que desea viajar (1-12): "))
        self.hechos["tipo_hospedaje"] = input("Ingrese el tipo de hospedaje deseado (Hotel, Resort, Villa, Airbnb) o deje en blanco para cualquier: ")
        if not self.hechos["tipo_hospedaje"]:
            self.hechos["tipo_hospedaje"] = None

    def obtener_datos_usuario(self):
        """
        Retorna los datos almacenados del usuario.
        """
        return self.hechos

"""'''
Módulo motor_inferencia.py
===========================
Este módulo implementa el Motor de Inferencia del sistema basado en conocimientos (KBS).
Se encarga de aplicar las reglas y obtener recomendaciones personalizadas.
'''
"""

class MotorInferencia:
    """
    Clase que representa el Motor de Inferencia del sistema.
    Integra la Base de Hechos con la Base de Conocimientos para generar recomendaciones.
    """

    def __init__(self, base_conocimiento, base_hechos):
        """
        Inicializa el motor de inferencia con las bases de conocimiento y hechos.
        """
        self.base_conocimiento = base_conocimiento
        self.base_hechos = base_hechos

    def generar_recomendaciones(self):
        """
        Genera recomendaciones de viaje basadas en los datos del usuario.
        Muestra únicamente los 6 destinos más recomendados.

        Retorna:
        - DataFrame con los 6 mejores destinos según la similitud.
        """
        datos_usuario = self.base_hechos.obtener_datos_usuario()
        recomendaciones = self.base_conocimiento.recomendar_destinos(
            datos_usuario["presupuesto"],
            datos_usuario["duracion_min"],
            datos_usuario["duracion_max"],
            datos_usuario["mes"],
            datos_usuario["tipo_hospedaje"]
        )

        return recomendaciones.head(6)

"""Ejemplos de inputs para recomendacion:
- Pendiente


Módulo main.py
===============================================
Este módulo proporciona un script de prueba para ejecutar el sistema completo.
'''
"""

if __name__ == "__main__":
    import pandas as pd

    # Cargar el dataset
    file_path = "cleaned_travel_dataset.csv"  # Asegúrate de subirlo en Colab
    travel_data = pd.read_csv(file_path)

    # Instanciar bases de datos
    base_conocimiento = BaseConocimiento(travel_data)
    base_hechos = BaseHechos()

    continuar = 1
    while continuar == 1:
        # Ingresar datos del usuario de forma interactiva
        base_hechos.ingresar_datos_usuario()

        # Instanciar motor de inferencia
        motor = MotorInferencia(base_conocimiento, base_hechos)

        # Obtener recomendaciones
        recomendaciones = motor.generar_recomendaciones()
        print("\nRecomendaciones de viaje:")
        print(recomendaciones)

        continuar = int(input("Desea continuar? (1: Sí, 0: No): "))
        print("\n")

    