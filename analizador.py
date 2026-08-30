import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def cargar_datos(ruta_archivo):
    """
    Carga los datos desde un archivo CSV a un DataFrame de Pandas.
    """
    try:
        df = pd.read_csv(ruta_archivo)
        print(f"📊 Datos cargados exitosamente. Total de registros originales: {len(df)}")
        return df
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo '{ruta_archivo}'. Ejecute mock_data.py primero.")
        return None

def limpiar_datos(df):
    """
    Limpia el DataFrame: elimina/imputa nulos y corrige tipos de datos (Data Wrangling).
    """
    print("\n🧹 Iniciando proceso de limpieza de datos...")
    df_limpio = df.copy()
    
    # 1. Corregir tipos de datos
    # 'errors=coerce' fuerza las fechas/números inválidos (ej. strings sueltos) a NaN o NaT
    df_limpio['Fecha'] = pd.to_datetime(df_limpio['Fecha'], errors='coerce')
    df_limpio['Nivel_Bateria'] = pd.to_numeric(df_limpio['Nivel_Bateria'], errors='coerce')
    
    # 2. Manejar valores nulos (NaN)
    # Para columnas categóricas o críticas, eliminamos las filas si están vacías o son 'Desconocido'
    columnas_criticas = ['Fecha', 'Sector_Hospital', 'Equipo_Medico', 'Estado_Actual']
    df_limpio.replace("Desconocido", np.nan, inplace=True)
    df_limpio.dropna(subset=columnas_criticas, inplace=True)
    
    # Para la batería, imputamos los nulos con el promedio de batería de ese estado
    if df_limpio['Nivel_Bateria'].isnull().any():
        media_bateria_estado = df_limpio.groupby('Estado_Actual')['Nivel_Bateria'].transform('mean')
        df_limpio['Nivel_Bateria'] = df_limpio['Nivel_Bateria'].fillna(media_bateria_estado)
    
    print(f"✨ Limpieza finalizada. Registros válidos retenidos: {len(df_limpio)}")
    return df_limpio

def analizar_metricas(df):
    """
    Extrae y muestra métricas clave del estado de la auditoría.
    """
    print("\n📈 --- MÉTRICAS CLAVE ---")
    
    # Métrica 1: Cantidad de equipos críticos por sector
    criticos = df[df['Estado_Actual'] == 'Critico']
    conteo_criticos = criticos.groupby('Sector_Hospital').size()
    
    print("\nCantidad de equipos en estado 'Critico' por sector:")
    if conteo_criticos.empty:
        print("No se encontraron equipos en estado crítico.")
    else:
        print(conteo_criticos.to_string())
    
    # Métrica 2: Porcentaje general de operatividad
    total_equipos = len(df)
    operativos = len(df[df['Estado_Actual'] == 'Operativo'])
    porcentaje_operativo = (operativos / total_equipos) * 100
    print(f"\nPorcentaje general de operatividad de los equipos: {porcentaje_operativo:.2f}%")
    
    return df

def generar_reportes(df):
    """
    Genera y guarda gráficos visuales usando Matplotlib.
    """
    print("\n🎨 Generando visualizaciones...")
    
    # Aplicar un estilo limpio y profesional (propio de matplotlib)
    plt.style.use('ggplot')
    
    # --- Gráfico 1: Incidentes (Mantenimiento/Crítico) por sector (Barras Horizontales) ---
    incidentes = df[df['Estado_Actual'].isin(['Mantenimiento', 'Critico'])]
    
    if not incidentes.empty:
        # Agrupar y desapilar para que sea apilado en la gráfica
        conteo_incidentes = incidentes.groupby(['Sector_Hospital', 'Estado_Actual']).size().unstack(fill_value=0)
        
        # Colores personalizados (Naranja para mantenimiento, Rojo para crítico)
        colores_barras = []
        if 'Mantenimiento' in conteo_incidentes.columns:
            colores_barras.append('#f39c12')
        if 'Critico' in conteo_incidentes.columns:
            colores_barras.append('#e74c3c')
            
        fig, ax = plt.subplots(figsize=(10, 6))
        conteo_incidentes.plot(kind='barh', stacked=True, ax=ax, color=colores_barras)
        
        ax.set_title('Incidentes por Sector Hospitalario', fontsize=14, fontweight='bold')
        ax.set_xlabel('Cantidad de Equipos')
        ax.set_ylabel('Sector del Hospital')
        
        plt.tight_layout()
        plt.savefig('incidentes_por_sector.png')
        plt.close()
        print("➡️  Gráfico de incidentes guardado como 'incidentes_por_sector.png'")
    
    # --- Gráfico 2: Porcentaje global del estado (Gráfico de Torta) ---
    estado_counts = df['Estado_Actual'].value_counts()
    
    # Mapa de colores para mantener consistencia
    color_map = {'Operativo': '#2ecc71', 'Mantenimiento': '#f39c12', 'Critico': '#e74c3c'}
    colores_pie = [color_map.get(estado, '#95a5a6') for estado in estado_counts.index]
    
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(estado_counts, labels=estado_counts.index, autopct='%1.1f%%', 
           startangle=90, colors=colores_pie, shadow=True, 
           wedgeprops={'edgecolor': 'black', 'linewidth': 1})
           
    ax.set_title('Estado Global del Equipamiento Médico', fontsize=16, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('estado_equipamiento.png')
    plt.close()
    print("➡️  Gráfico de torta guardado como 'estado_equipamiento.png'")

if __name__ == "__main__":
    ruta_csv = "inspecciones.csv"
    
    df_crudo = cargar_datos(ruta_csv)
    
    if df_crudo is not None:
        df_limpio = limpiar_datos(df_crudo)
        analizar_metricas(df_limpio)
        generar_reportes(df_limpio)
        print("\n✅ Proceso completado exitosamente.")
