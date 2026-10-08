import random
import uuid
import pandas as pd

from faker import Faker

#1. Escoger el pais y leguaje de la simulacion los datos
fake=Faker("es_CO")

#2. simular semillas;
Faker.seed(42)
random.seed(42)

#3. definir el dato y su tipo a simular
#id (texto (UUID))
#nombre (texto)
#descripcion (texto) 
#area_responsable (texto)

#4. definir el numero de datos simular (DATASET)
filas=250

CATEGORIAS=[ "Tecnología",
  "Educación",
  "Salud",
  "Finanzas",
  "Entretenimiento"]
AREAS=[ "Desarrollo",
  "Recursos Humanos",
  "Marketing",
  "Ventas",
  "Administración"]

#construir funcion generadora de datos
def generar_datos_usuarios(numero_registros=filas):

    filas=[]
    for _ in range(numero_registros):
        filas.append({
            "id":str (uuid.uuid4()),
            "nombre": random.choice(CATEGORIAS),
            "descripcion": fake.sentence(nb_words=8),
            "area_responsable": random.choice(AREAS)        ,
    
        })
        return filas

#6. Utilizaremos PANDAS  para ordenar los datos simulado y asi traer un DATAFRAME
tabla_ordenada_usuarios=pd.DataFrame(generar_datos_usuarios)
print(tabla_ordenada_usuarios)

#7.1 generar una funcion que muestre los datos
def generar_muestra(datos,porcentaje):
    return datos.sample(fraccion=porcentaje,random_state=random.randint(0,9999)).index

def ensuciar(datos_df):
    datos_df=datos_df.copy()
  #8. funcion que ensucia los datos
def ensuciar(datos_df):
    datos_df=datos_df.copy()

    # se ensucia `nombre` con variantes del mismo nombre
    def escribir_mal (texto):
            variantes=[texto.lower(), f" {texto.title()} ", texto.capitalize() ]
            return random.choice(variantes)
    
    indices_nombre=generar_muestra(datos_df,0.30)
    datos_df.loc[indices_nombre,"nombre"]=datos_df.loc[indices_nombre,"nombre"].apply(escribir_mal)

    # se ensucia `descripcion` con 15% de None (nulos)
    indices_descripcion=generar_muestra(datos_df,0.15)
    datos_df.loc[indices_descripcion,"descripcion"]=None

    # se ensucia `area_responsable` con 10% de None
    indices_area=generar_muestra(datos_df,0.10)
    datos_df.loc[indices_area,"area_responsable"]=None

    return datos_df

#9. mostrar los datos ensuciados
tabla_sucia_usuarios=ensuciar(tabla_ordenada_usuarios)
print(tabla_sucia_usuarios)
print(tabla_sucia_usuarios.isna().sum())