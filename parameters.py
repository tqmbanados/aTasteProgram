SCORE_IMAGE_PATH = ["ly_files", "ly_files.png"]
WINDOW_GEOMETRY = (200, 100, 1700, 900)
BEAT_DURATION_MS = 1000
COMMANDS = ['sentarse', 'leer', 'nadar', 'bailar', 'asentir', 'negar', 'saltar',
            'esconderse', 'tocar_instrumento', 'levantar_brazo', 'bajar_brazo',
            'remar', 'gritar', 'caminar', 'pensar', 'mover_derecha', 'mover_izquierda',
            'abrazar', 'estirar', 'girar', 'imitar_animal', 'reir', 'señalar', 'revolver']
USE_API = True
TEST_COMMANDS = True

COMMANDS_TEST = ["Sentarse", "Leer", "Nadar", "Bailar", "Asentir", "Negar", "Saltar",
                 "Esconderse", "Tocar Instrumento", "Levantar Brazo", "Bajar Brazo",
                 "Remar", "Gritar", "Caminar", "Pensar", "Mover a Derecha",
                 "Mover a Izquierda", "Abrazar", "Estirar", "Girar", "Imitar Animal",
                 "Reír", "Señalar", "Revolver"]

if __name__ == "__main__":
    com = []
    #for command in COMMANDS_TEST:
    #    new = command.replace(' ', '_')
    #    new = new.lower()
    #    com.append(new)
    zipped = zip(COMMANDS, COMMANDS_TEST)
    dicc = {command: text for command, text in zipped}
    print(dicc)
