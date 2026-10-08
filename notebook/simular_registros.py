import random
import uuid
import pandas as pd
from faker import Faker

# 1. Escoger el país y lenguaje para simular los datos
fake = Faker("es_CO")

# 2. Sembrar semillas para garantizar reproducibilidad
Faker.seed(42)
random.seed(42)

# 3. Definir constantes iniciales requeridas
FILAS = 800
ESTADOS = ["INSCRITO", "EN_PROCESO", "FINALIZADO"]

# Definir catálogos de IDs estables para simular las llaves foráneas lógicas
IDS_USUARIO = [str(uuid.uuid4()) for _ in range(30)]
IDS_RETO = [str(uuid.uuid4()) for _ in range(10)]

# 5. Construir función generadora de datos de registros
def generar_registros(numero_registros=FILAS):
    filas = []
    for _ in range(numero_registros):
        filas.append({
            "id": str(uuid.uuid4()),
            "fecha_registro": fake.date_time_between(start_date="-1y", end_date="now"),
            "observacion": fake.sentence(nb_words=10),
            "estado": random.choice(ESTADOS),
            "id_usuario": random.choice(IDS_USUARIO),
            "id_reto": random.choice(IDS_RETO)
        })
    return filas

# 6. Utilizar PANDAS para ordenar los datos simulados en un DataFrame
tabla_ordenada_registros=pd.DataFrame(generar_datos_registros())

# 7.1. Generar una función auxiliar que obtenga los índices de una muestra aleatoria
def generar_muestra(datos, porcentaje):
    return datos.sample(frac=porcentaje, random_state=random.randint(0, 9999)).index

# 7.2. Función que ensucia los datos cumpliendo con los criterios del proyecto
def ensuciar(datos_df):
    datos_df = datos_df.copy()
    
    # Ensuciar 'observacion': 20% en None (nulos)
    subconjunto_datos = generar_muestra(datos_df, 0.20)
    datos_df.loc[subconjunto_datos, "observacion"] = None
    
    # Ensuciar 'estado': variantes de escritura ('inscrito', 'EN PROCESO', ' Finalizado ')
    def escribir_mal_estado(texto):
        variantes = [texto.lower(), texto.replace("_", " "), f" {texto.capitalize()} "]
        return random.choice(variantes)
        
    subconjunto_datos = generar_muestra(datos_df, 0.25)
    datos_df.loc[subconjunto_datos, "estado"] = datos_df.loc[subconjunto_datos, "estado"].map(escribir_mal_estado)
    
    # Ensuciar 'fecha_registro': dos formatos mezclados ("2026-03-15 14:30:00" y "15/03/2026 14:30")
    iso = datos_df["fecha_registro"].dt.strftime("%Y-%m-%d %H:%M:%S")
    latino = datos_df["fecha_registro"].dt.strftime("%d/%m/%Y %H:%M")
    datos_df["fecha_registro"] = iso
    filas_elegidas = generar_muestra(datos_df, 0.40)
    datos_df.loc[filas_elegidas, "fecha_registro"] = latino.loc[filas_elegidas]
    
    # 10% con el par id_usuario + id_reto REPETIDO (mismo usuario inscrito dos veces en el mismo reto)
    n_repetidos_par = int(len(datos_df) * 0.10)
    indices_fuente = datos_df.sample(n=n_repetidos_par, random_state=42).index
    indices_destino = datos_df.sample(n=n_repetidos_par, random_state=99).index
    for src, dst in zip(indices_fuente, indices_destino):
        if src != dst:
            datos_df.loc[dst, "id_usuario"] = datos_df.loc[src, "id_usuario"]
            datos_df.loc[dst, "id_reto"] = datos_df.loc[src, "id_reto"]
            
    # 5% de las filas repetidas tal cual (duplicados exactos con nuevo id único)
    n_duplicados = int(len(datos_df) * 0.05)
    duplicas = datos_df.sample(n=n_duplicados, random_state=123).copy()
    duplicas["id"] = [str(uuid.uuid4()) for _ in range(n_duplicados)]
    datos_df = pd.concat([datos_df, duplicas], ignore_index=True)
    
    return datos_df

def generar_registros_sucios(n=800):
    """Función principal requerida que genera y devuelve el DataFrame con datos sucios."""
    df_base = pd.DataFrame(generar_registros(n))
    df_sucio = ensuciar(df_base)
    return df_sucio

if __name__ == "__main__":
    df = generar_registros_sucios(800)
    print("Dimensiones del DataFrame (df.shape):")
    print(df.shape)
    print("\nPrimeras filas (df.head()):")
    print(df.head())
    print("\nConteo de valores nulos (df.isna().sum()):")
    print(df.isna().sum())