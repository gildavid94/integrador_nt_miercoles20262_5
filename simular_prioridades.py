import random
import uuid

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
NIVELES=[1,2,3,4]
DIAS=[3,4,5,6]

def generar_datos_prioridades(numero_registros=FILAS):
    filas = []
    for _ in range(numero_registros):
        filas.append({
            "id":str(uuid.uuid4()),
            "nombre":random.choice(list(NIVELES.keys())),
            "nivel":NIVELES[nombre],
            "dias_max_respuesta":DIAS[nivel]
        })
    return filas