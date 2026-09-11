def mi_funcion_fea(a, b):
    variable_sin_usar = 42
    texto = "Hola " + "Mundo"
    return a + b


class mi_clase:
    def __init__(self):
        self.lista = [1, 2, 3, 4, 5]

    def un_metodo_muy_largo(self):
        print(
            "Esta es una línea exageradamente larga que sobrepasa por mucho el límite de ochenta y ocho caracteres que las buenas prácticas y Black exigen por defecto en cualquier proyecto de Python."
        )


print(mi_funcion_fea(2, 3))
