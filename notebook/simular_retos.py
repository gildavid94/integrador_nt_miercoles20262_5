import random
import uuid
from datetime import timedelta
from faker import Faker
import pandas as pd

# 1. Escoger el pais y lenguaje para simular los datos
fake = Faker("es_CO")

# 2. Sembrar semillas
Faker.seed(42)
random.seed(42)

# 3. Definir constantes requeridas por los criterios de aceptación
FILAS = 500

ESTADOS = ["ACTIVO", "EN_CURSO", "CERRADO", "PENDIENTE", "CANCELADO"]
IDS_EMPRESA = [str(uuid.uuid4()) for _ in range(5)]
IDS_CATEGORIA = [str(uuid.uuid4()) for _ in range(4)]
IDS_PRIORIDAD = [str(uuid.uuid4()) for _ in range(3)]


# 5. Construir funcion generadora de datos
def generar_retos(numero_registros=FILAS):
    filas = []

    for _ in range(numero_registros):
        # A. Fechas base
        f_inicio = fake.date_between(start_date="-1y", end_date="+3m")
        f_fin = f_inicio + timedelta(days=random.randint(15, 180))

        # B. Valores limpios base
        nombre = fake.sentence(nb_words=6).rstrip(".")
        descripcion = fake.sentence(nb_words=12)
        estado = random.choice(ESTADOS)

        # C. Reglas para ensuciar datos según criterios del tablero
        # 10% con espacios sobrantes
        if random.random() < 0.10:
            nombre = f"  {nombre}   "

        # 12% en None (nulos)
        if random.random() < 0.12:
            descripcion = None

        # Mezclar formatos de fecha ("YYYY-MM-DD" y "DD/MM/YYYY")
        if random.random() < 0.50:
            fecha_inicio_str = f_inicio.strftime("%Y-%m-%d")
        else:
            fecha_inicio_str = f_inicio.strftime("%d/%m/%Y")

        # 8% None y 5% ANTERIOR a fecha_inicio (error lógico)
        prob_f_fin = random.random()
        if prob_f_fin < 0.08:
            fecha_fin_str = None
        elif prob_f_fin < 0.13:
            f_fin_erronea = f_inicio - timedelta(days=random.randint(1, 30))
            fecha_fin_str = f_fin_erronea.strftime("%Y-%m-%d")
        else:
            fecha_fin_str = f_fin.strftime("%Y-%m-%d")

        # Variantes de estado
        prob_estado = random.random()
        if prob_estado < 0.20:
            estado = "en_curso"
        elif prob_estado < 0.35:
            estado = "EN CURSO"
        elif prob_estado < 0.50:
            estado = " Cerrado "

        filas.append(
            {
                "id": str(uuid.uuid4()),
                "nombre": nombre,
                "descripcion": descripcion,
                "fecha_inicio": fecha_inicio_str,
                "fecha_fin": fecha_fin_str,
                "estado": estado,
                "id_empresa": random.choice(IDS_EMPRESA),
                "id_categoria": random.choice(IDS_CATEGORIA),
                "id_prioridad": random.choice(IDS_PRIORIDAD),
            }
        )

    # 5% de filas repetidas tal cual (duplicados exactos)
    cantidad_duplicados = int(numero_registros * 0.05)
    for _ in range(cantidad_duplicados):
        filas.append(random.choice(filas))

    # Retorna el DataFrame exigido en la historia de usuario
    return pd.DataFrame(filas)


# Bloque para verificar la ejecución directamente en terminal
if _name_ == "_main_":
    df = generar_retos(FILAS)
    print("Shape:", df.shape)
    print("\nHead:\n", df.head())
    print("\nNulos:\n", df.isna().sum())