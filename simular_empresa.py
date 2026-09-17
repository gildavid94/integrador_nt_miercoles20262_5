import random
import uuid

from faker import Faker

#1. Escoger el pais y lenguaje para simular los datos
fake=Faker("es_CO")

#2. Sembrar semillas
Faker.seed(42)
random.seed(42)

#3. Definir el dato y su tipo a simular
#id (texto (UUID)), 
#nombre (texto), 
#nit (texto), 
#sector (texto),***************** 
#contacto (texto), 
#correo (texto), 
#telefono (texto), 
#ctiva (booleano).

#4. Definir el numero de datos simulados (DATASET)
filas=300