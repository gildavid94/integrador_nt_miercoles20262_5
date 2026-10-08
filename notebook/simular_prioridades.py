import random
import uuid
import pandas as pd

from faker import Faker

#1 Escoger el pais y lenguaje para simular los datos

fake=Faker("es_CO")

#2 Sembrar semillas 
Faker.seed(42)
random.seed(42)

#id (texto (UUID)),
#nombre (texto), 
#nivel (entero), ****
#dias_max_respuesta (entero).

FILAS=200
NIVELES = {
    "Crítica": 1,
    "Alta": 2,
    "Media": 3,
    "Baja": 4,
    "Informativa": 5
}

DIAS = {
    1: 2,
    2: 4,
    3: 6,
    4: 8,
    5: 10
}

def generar_datos_prioridades(numero_registros=FILAS):
    filas = []
    for _ in range(numero_registros):
        nombre_generado = random.choice(list(NIVELES.keys())) 
        nivel_generado = NIVELES[nombre_generado]
        filas.append({
            "id": str(uuid.uuid4()),                      
            "nombre": nombre_generado,
            "nivel": nivel_generado,
            "dias_max_respuesta": DIAS[nivel_generado]
        })
    return filas

tabla_ordenada_prioridades=pd.DataFrame(generar_datos_prioridades())

def  generar_muestra(datos,porcentaje):
    return datos.sample(fraccion=porcentaje,random_state=random.randint(0,9999)).index

def ensuciar(datos_df):
    datos_df=datos_df.copy()

#Se ensucia `nombre`: variantes: 'ALTA', ' alta ', 'Alta'.
    def escribir_mal(texto):
            variantes=[texto.lower(), f" {texto.title()} ", texto.capitalize()]
            return random.choice(variantes)
    subconjunto_datos=generar_muestra(datos_df,0.12)
    datos_df.loc[subconjunto_datos,"nombre"]=datos_df.loc[subconjunto_datos,"nombre"].map(escribir_mal)

#Se ensucia `nivel`: a veces como TEXTO ('3'), a veces la palabra ('tres') y 7% en None.
    subconjunto_datos=generar_muestra(datos_df,0.07)
    datos_df.loc[subconjunto_datos,"nivel"]=None

    subconjunto_datos = generar_muestra(datos_df, 0.10)
    validos = datos_df.loc[subconjunto_datos, "nivel"].notna()
    datos_df.loc[subconjunto_datos[validos], "nivel"] = datos_df.loc[subconjunto_datos[validos], "nivel"].astype(str)

    def convertir_a_palabra(valor):
        mapa = {1: 'uno', 2: 'dos', 3: 'tres', 4: 'cuatro', 5: 'cinco', 
                '1': 'uno', '2': 'dos', '3': 'tres', '4': 'cuatro', '5': 'cinco'}
        return mapa.get(valor, valor)

    subconjunto_datos = generar_muestra(datos_df, 0.10)
    datos_df.loc[subconjunto_datos, "nivel"] = datos_df.loc[subconjunto_datos, "nivel"].map(convertir_a_palabra)

#Se ensucia `dias_max_respuesta`: 5% en None y 3% con un valor absurdo (999).
    subconjunto_datos=generar_muestra(datos_df,0.05)
    datos_df.loc[subconjunto_datos,"dias_max_respuesta"]=None

    subconjunto_datos=generar_muestra(datos_df,0.03)
    datos_df.loc[subconjunto_datos,"dias_max_respuesta"]=999

#8% de las filas repetidas tal cual (duplicados exactos).
    duplicar_filas = datos_df.sample(frac=0.08, random_state=random.randint(0, 9999))
    datos_df = pd.concat([datos_df, duplicar_filas], ignore_index=True)

    
    
    

