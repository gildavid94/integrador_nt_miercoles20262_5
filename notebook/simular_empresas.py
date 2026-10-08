import random
import uuid
from faker import Faker
import pandas as pd

# 1. Escoger el pais y lenguaje para simular los datos
fake = Faker("es_CO")

# 2. Sembrar semillas
Faker.seed(42)
random.seed(42)

# 3. Definir el dato y su tipo a simular
# id (texto (UUID)),
# nombre (texto),
# nit (texto),
# sector (texto),
# contacto (texto),
# correo (texto),
# telefono (texto),
# activa (booleano).

# 4. Definir el numero de datos simulados (DATASET)
FILAS = 300

SECTORES = ["tecnologia", "salud", "educacion", "logistica"]


# 5. Construir funcion generadora de datos
def generar_datos_empresas(numero_registros=FILAS):
  filas = []
  for _ in range(numero_registros):
    filas.append({
        "id": str(uuid.uuid4()),
        "nombre": fake.company(),
        "nit": fake.numerify("#########-#"),
        "sector": random.choice(SECTORES),
        "contacto": fake.name(),
        "correo": fake.company_email(),
        "telefono": fake.numerify("3#########"),
        "activa": random.choice([True, False]),
    })
  return filas


# 7. Ensuciar los datos


# 7.1. Generar una funcion que muestra los datos / obtiene la muestra
def generar_muestra(datos, fraccion):
  return datos.sample(
      frac=fraccion, random_state=random.randint(0, 9999)
  ).index


# 7.2. Funcion que ensucia los datos
def ensuciar(datos_df):
  datos_df = datos_df.copy()

  # Para el atributo nombre: 10% con espacios sobrantes al inicio y al final
  subconjunto_datos = generar_muestra(datos_df, 0.10)
  datos_df.loc[subconjunto_datos, "nombre"] = (
      " " + datos_df.loc[subconjunto_datos, "nombre"] + " "
  )

  # Para el atributo nombre: 15% en MAYUSCULAS
  subconjunto_datos = generar_muestra(datos_df, 0.15)
  datos_df.loc[subconjunto_datos, "nombre"] = datos_df.loc[
      subconjunto_datos, "nombre"
  ].str.upper()

  # Para el atributo nit: la mitad con puntos y guiones (900.123.456-7) y la otra mitad sin nada (9001234567)
  iso_nit = datos_df["nit"].str.replace("-", "", regex=False)
  latino_nit = (
      iso_nit.str[:3]
      + "."
      + iso_nit.str[3:6]
      + "."
      + iso_nit.str[6:9]
      + "-"
      + iso_nit.str[9]
  )
  datos_df["nit"] = iso_nit
  filas_elegidas = generar_muestra(datos_df, 0.50)
  datos_df.loc[filas_elegidas, "nit"] = latino_nit.loc[filas_elegidas]

  # Para el atributo sector: variantes del mismo sector ('Logistica', 'LOGISTICA', ' logistica ')
  def escribir_mal(texto):
    variantes = [
        texto.lower(),
        texto.upper(),
        f" {texto.lower()} ",
        texto.capitalize(),
    ]
    return random.choice(variantes)

  subconjunto_datos = generar_muestra(datos_df, 0.20)
  datos_df.loc[subconjunto_datos, "sector"] = datos_df.loc[
      subconjunto_datos, "sector"
  ].map(escribir_mal)

  # Para el atributo contacto: 8% en None (nulos)
  subconjunto_datos = generar_muestra(datos_df, 0.08)
  datos_df.loc[subconjunto_datos, "contacto"] = None

  # Para el atributo correo: 6% sin la arroba (correo invalido)
  subconjunto_datos = generar_muestra(datos_df, 0.06)
  datos_df.loc[subconjunto_datos, "correo"] = datos_df.loc[
      subconjunto_datos, "correo"
  ].str.replace("@", "", regex=False)

  # Para el atributo telefono: tres formatos mezclados ('3001234567', '300 123 4567', '+57 300-123-4567')
  iso_tel = datos_df["telefono"]
  espacios_tel = (
      iso_tel.str[:3] + " " + iso_tel.str[3:6] + " " + iso_tel.str[6:]
  )
  pais_tel = (
      "+57 " + iso_tel.str[:3] + "-" + iso_tel.str[3:6] + "-" + iso_tel.str[6:]
  )

  filas_elegidas = generar_muestra(datos_df, 0.33)
  datos_df.loc[filas_elegidas, "telefono"] = espacios_tel.loc[filas_elegidas]

  filas_elegidas = generar_muestra(datos_df, 0.33)
  datos_df.loc[filas_elegidas, "telefono"] = pais_tel.loc[filas_elegidas]

  # Para el atributo activa: a veces como texto ('SI', 'No', '1', '0')
  def escribir_mal_activa(valor):
    return random.choice(["SI", "No", "1", "0"])

  subconjunto_datos = generar_muestra(datos_df, 0.30)
  datos_df.loc[subconjunto_datos, "activa"] = datos_df.loc[
      subconjunto_datos, "activa"
  ].map(escribir_mal_activa)


  # 5% de las filas repetidas tal cual (duplicados exactos)
  filas_duplicadas = datos_df.sample(frac=0.05, random_state=42)
  datos_df = pd.concat([datos_df, filas_duplicadas], ignore_index=True)

  return datos_df

  # 3% de los nit repetidos entre empresas distintas (el NIT deberia ser unico)
  subconjunto_datos = generar_muestra(datos_df, 0.03)
  nits_existentes = datos_df.drop(subconjunto_datos)["nit"].tolist()
  datos_df.loc[subconjunto_datos, "nit"] = [
      random.choice(nits_existentes) for _ in range(len(subconjunto_datos))
  ]

# Función exportable para importar desde otros scripts
def generar_empresas(n=300):
  df_limpio = pd.DataFrame(generar_datos_empresas(n))
  df_sucio = ensuciar(df_limpio)
  return df_sucio


# Bloque para probar localmente el script
if __name__ == "__main__":
  df = generar_empresas()
  print("--- SHAPE ---")
  print(df.shape)
  print("\n--- HEAD ---")
  print(df.head())
  print("\n--- NULOS (ISNA) ---")
  print(df.isna().sum())
  