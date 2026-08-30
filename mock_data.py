import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def generar_datos_hospitalarios(num_registros=150):
    """
    Genera un archivo CSV con datos simulados de inspecciones hospitalarias.
    Introduce errores intencionales (nulos, formatos incorrectos) para simular
    la carga manual de datos y justificar la necesidad de limpieza posterior.
    """
    sectores = ["Terapia Intensiva", "Guardia", "Quirófano", "Internación", "Laboratorio", "Rayos X"]
    equipos = ["Respirador", "Monitor Multiparamétrico", "Desfibrilador", "Bomba de Infusión", "Ecógrafo", "Máquina de Anestesia"]
    estados = ["Operativo", "Mantenimiento", "Critico"]
    
    fecha_inicio = datetime(2023, 1, 1)
    
    datos = []
    for _ in range(num_registros):
        fecha = fecha_inicio + timedelta(days=random.randint(0, 365))
        sector = random.choice(sectores)
        equipo = random.choice(equipos)
        
        # Probabilidades ponderadas para simular una distribución realista
        estado = random.choices(estados, weights=[0.7, 0.2, 0.1])[0]
        
        # El nivel de batería tiene correlación con el estado del equipo
        if estado == "Operativo":
            bateria = random.randint(70, 100)
        elif estado == "Mantenimiento":
            bateria = random.randint(20, 100)
        else:
            bateria = random.randint(0, 30)
            
        datos.append({
            "Fecha": fecha.strftime("%Y-%m-%d"),
            "Sector_Hospital": sector,
            "Equipo_Medico": equipo,
            "Estado_Actual": estado,
            "Nivel_Bateria": bateria
        })
        
    df = pd.DataFrame(datos)
    
    # Convertir todas las columnas a tipo 'object' (texto genérico) 
    # Esto evita el error de Pandas 2.0+ al intentar meter un string ("Baja") en una columna de números enteros (int64)
    df = df.astype(object)
    
    # --- Inyección de Ruido (Errores Intencionales) ---
    # Entre 5% y 10% de registros corruptos
    porcentaje_error = random.uniform(0.05, 0.10)
    num_errores = int(num_registros * porcentaje_error)
    
    for _ in range(num_errores):
        columna = random.choice(df.columns)
        indice = random.randint(0, num_registros - 1)
        tipo_error = random.choice(["NaN", "Formato_Erroneo"])
        
        if tipo_error == "NaN":
            df.loc[indice, columna] = np.nan
        elif tipo_error == "Formato_Erroneo":
            if columna == "Fecha":
                df.loc[indice, columna] = "Fecha Invalida"
            elif columna == "Nivel_Bateria":
                df.loc[indice, columna] = "Baja"
            else:
                df.loc[indice, columna] = "Desconocido"
            
    # Guardar los datos generados en un archivo CSV
    df.to_csv("inspecciones.csv", index=False)
    print(f"✅ Archivo 'inspecciones.csv' generado exitosamente con {num_registros} registros.")
    print(f"⚠️ Se introdujeron {num_errores} errores intencionales para practicar Data Cleaning.")

if __name__ == "__main__":
    generar_datos_hospitalarios()
