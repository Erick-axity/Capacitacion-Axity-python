import os

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

RUTA_MODELO = "mi_modelo_clasificador.pkl"


# =====================================================================
# 1. ENTRENAMIENTO Y SERIALIZACIÓN
# =====================================================================
def entrenar_modelo(ruta_csv: str) -> None:
    print("INICIANDO FASE DE ENTRENAMIENTO...")

    # A. Cargar datos con Pandas
    df = pd.read_csv(ruta_csv)
    print(f"Datos originales cargados: {len(df)} filas.")

    # B. Limpieza de datos (Quitar edades imposibles)
    # Pandas filtra la tabla dejando solo los que tienen edad menor a 100
    df_limpio = df[df["edad"] < 100]
    print(f"Datos después de limpieza: {len(df_limpio)} filas.")

    # C. Separar "Features" (X) y "Target" (y)
    X = df_limpio[["edad", "salario"]]
    y = df_limpio["compro"]

    # D. Dividir en datos de entrenamiento (80%) y prueba (20%)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # E. Entrenar el clasificador (Random Forest)
    modelo = RandomForestClassifier(random_state=42)
    modelo.fit(X_train, y_train)

    # Evaluar precisión
    predicciones = modelo.predict(X_test)
    precision = accuracy_score(y_test, predicciones)
    print(f"Modelo entrenado. Precisión (Accuracy): {precision * 100:.2f}%")

    # F. Serialización (Guardar el modelo)
    joblib.dump(modelo, RUTA_MODELO)
    print(f"Modelo guardado exitosamente en: {RUTA_MODELO}\n")


# =====================================================================
# 2. INFERENCIA BÁSICA (Predicción en vivo)
# =====================================================================
def hacer_inferencia(edad: int, salario: float) -> None:
    print("INICIANDO FASE DE INFERENCIA...")

    if not os.path.exists(RUTA_MODELO):
        print("Error: No se encontró el modelo. Entrénalo primero.")
        return

    # A. Cargar el modelo guardado
    modelo_cargado = joblib.load(RUTA_MODELO)

    # B. Preparar los datos nuevos (Debe tener la misma forma que X)
    # Scikit-learn espera un DataFrame de Pandas para la predicción
    nuevos_datos = pd.DataFrame([{"edad": edad, "salario": salario}])

    # C. Predecir
    resultado = modelo_cargado.predict(nuevos_datos)

    clase_predicha = "SÍ COMPRARÁ" if resultado[0] == 1 else "NO COMPRARÁ"
    print(
        f"Cliente (Edad: {edad}, Salario: ${salario:,.2f}) -> Predicción: {clase_predicha}\n"
    )


# =====================================================================
# EJECUCIÓN
# =====================================================================
if __name__ == "__main__":
    # 1. Entrenamos (Esto creará el archivo .pkl)
    entrenar_modelo("clientes.csv")

    # 2. Hacemos inferencias simulando clientes nuevos
    hacer_inferencia(edad=22, salario=35000.0)
    hacer_inferencia(edad=55, salario=85000.0)
