import random 
import uuid  # ids complejos
import pandas as pd
from faker import Faker

# 1. Escoger el pais y lenguaje para simular los datos
fake = Faker("es_CO") 

# 2. Sembrar semillas
Faker.seed(42)
random.seed(42)

# 3. Definir el dato y su tipo a simular
# id (texto (UUID)), 
# titulo (texto), 
# descripcion (texto), 
# url_archivo (texto), 
# fecha entrega 
# estado *******, 
# calificacion
# id_registro

# 4. Definir el numero de datos simulados (DATASET)
FILAS = 600

ESTADOS = ["pendiente", "entregado", "calificado"]
IDS_REGISTRO = ["f47ac10b-58cc-4372-a567-0e02b2c3d479", "3b92f76c-821a-4c9f-bbd3-1829e061b452", "a1b2c3d4-e5f6-4789-9012-3456789abcdef", "7d8e9f0a-1b2c-43de-9f8a-bc1234567890"]

# 5. Construir funcion generadora de datos
def generar_datos_evidencias(numero_registros = FILAS):

    filas = []
    for _ in range(numero_registros):
        estado_actual = random.choice(ESTADOS)
        
        # Logica coherente: Si esta pendiente, no hay calificacion (None o 0)
        # Si esta calificado, le damos una nota aleatoria entre 3.0 y 5.0
        if estado_actual == "pendiente" or "entregado":
            calificacion = None
        else:
            calificacion = round(random.uniform(3.0, 5.0), 1)
        filas.append({
            "id": str(uuid.uuid4()),
            "titulo": fake.sentence(nb_words = 5).rstrip("."),
            "descripcion": fake.sentence(nb_words = 12),
            "url_archivo": fake.url() + fake.file_name(category = "office"),
            "fecha_entrega": fake.date_time_between(start_date = "-1y", end_date = "now"),
            "estado": random.choice(ESTADOS),
            "calificacion": calificacion,
            "id_registro": random.choice(IDS_REGISTRO)
        })

    return filas

# 6. Utilizaremos PANDAS para ordenar los datos simulados en un DATAFRAME(tabla ordenada)
tabla_ordenada_evidencias = pd.DataFrame(generar_datos_evidencias()) 
print(tabla_ordenada_evidencias)

# 7. Ensuciar los datos (datos sin coherencia con el modelo)

# 7.1. Generar una funcion que muestre los datos
def generar_muestra(datos, porcentaje):
    return datos.sample(fraccion = porcentaje, random_state = random.randint(0,9999)).index

# 7.2. Funcion que ensucia los datos
def ensuciar(datos_df):
    datos_df = datos_df.copy() # Saco una copia antes de ensuciar

    # Se ensucia `titulo`: 10% con espacios sobrantes.
    subconjunto_datos = generar_muestra(datos_df, 0.1)
    datos_df.loc[subconjunto_datos, "titulo"] = " " + datos_df.loc[subconjunto_datos, "titulo"]

    # Se ensucia `descripcion`: 15% en None (nulos).
    subconjunto_datos = generar_muestra(datos_df, 0.15)
    datos_df.loc[subconjunto_datos, "descripcion"] = None

    # Se ensucia `url_archivo`: 8% sin el `http://` o `https://` del inicio (URL invalida)
    subconjunto_url = generar_muestra(datos_df, 0.08)
    # Reemplazamos los protocolos por texto vacío para invalidar la URL de inicio
    datos_df.loc[subconjunto_url, "url_archivo"] = (
        datos_df.loc[subconjunto_url, "url_archivo"]
        .str.replace("https://", "", regex=False)
        .str.replace("http://", "", regex=False)
        )
    
    # Se ensucia `fecha_entrega`: dos formatos mezclados: "2026-03-15 14:30:00" y "15/03/2026 14:30"
    iso = datos_df["fecha_entrega"].dt.strftime("%Y-%m-%d %H:%M:%S")               
    latino = datos_df["fecha_entrega"].dt.strftime("%d/%m/%Y %H:%M")              
    datos_df["fecha_entrega"] = iso                                               
    filas_elegidas = generar_muestra(datos_df, 0.40)
    datos_df.loc[filas_elegidas, "fecha_entrega"] = latino.loc[filas_elegidas]

    # Se ensucia `estado`: variantes: 'enviada', 'EN REVISION', ' Aprobada '
    estados_alternativos = ["enviada", "EN REVISION", " Aprobada "]
    filas_elegidas = generar_muestra(datos_df, 0.10)
    datos_df.loc[filas_elegidas, "estado"] = random.choices(estados_alternativos, k=len(filas_elegidas))

    # Se ensucia `calificacion`: 6% en None 
    filas_elegidas = generar_muestra(datos_df, 0.06)
    datos_df.loc[filas_elegidas, "calificacion"] = None
    # 4% fuera de rango (7.5 o -1) y a veces como texto con coma ('4,5')
    filas_elegidas = generar_muestra(datos_df, 0.04)
    datos_df.loc[filas_elegidas, "calificacion"] = random.choices([7.5, -1, "4,5"], k=len(filas_elegidas)) 

    # 5% de las filas repetidas tal cual (duplicados exactos)
    indices_a_duplicar = generar_muestra(datos_df, 0.05)
    filas_duplicadas = datos_df.loc[indices_a_duplicar]
    
    # Unir el DataFrame original con las filas duplicadas usando pd.concat
    datos_df = pd.concat([datos_df, filas_duplicadas], ignore_index=True)
    
    # Mezclar el DataFrame para que los duplicados no queden al final
    datos_df = datos_df.sample(frac=1, random_state=42).reset_index(drop=True)

    # 10% con el par `id_registro` + `url_archivo` REPETIDO: la misma entrega subida dos veces (eso el back lo prohibe con 409)
    indices_repetidos = generar_muestra(datos_df, 0.10)
    subconjunto_conflicto = generar_muestra(datos_df, 0.10)
    
    for idx in subconjunto_conflicto:
        # Elegir otra fila al azar de todo el DataFrame para robarle su id_registro y url_archivo
        fila_donante = datos_df.sample(n=1).iloc[0]
        
        datos_df.loc[idx, "id_registro"] = fila_donante["id_registro"]
        datos_df.loc[idx, "url_archivo"] = fila_donante["url_archivo"]

    # Mezclar (barajar) el DataFrame final para que el ruido quede bien distribuido
    datos_df = datos_df.sample(frac=1, random_state=42).reset_index(drop=True)

    # Retornar el DataFrame para poder importarlo desde el script de exportación
    return datos_df

    #Todo se arma en una funcion `generar_evidencias(n=600)` que **devuelve el DataFrame** (`return df`), para poder importarla desde el script de exportacion
    # --- Bloque de prueba local ---
    if __name__ == "__main__":
        df = generar_evidencias(600)
    
        print("--- SHAPE (Filas, Columnas) ---")
        print(df.shape)
    
        print("\n--- HEAD (Primeras filas) ---")
        print(df.head())
    
        print("\n--- ISNA().SUM() (Conteo de nulos por columna) ---")
        print(df.isna().sum())

    
