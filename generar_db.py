#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera la base de datos del caso "El Misterio del Trofeo Robado".
Diseñado para resolverse SIN usar JOIN: cada paso es una consulta a una sola tabla.
"""

import os
import random
import sqlite3

random.seed(20260305)

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "misterio-trofeo.db")
if os.path.exists(DB):
    os.remove(DB)

con = sqlite3.connect(DB)
cur = con.cursor()

# ----------------------------------------------------------------------
# Esquema
# ----------------------------------------------------------------------
cur.executescript("""
CREATE TABLE persona (
    id        INTEGER PRIMARY KEY,
    nombre    TEXT    NOT NULL,
    grupo     TEXT    NOT NULL,
    num_lista INTEGER NOT NULL,
    calle     TEXT    NOT NULL,
    numero    INTEGER NOT NULL
);

CREATE TABLE parte_incidencia (
    id          INTEGER PRIMARY KEY,
    fecha       INTEGER NOT NULL,
    tipo        TEXT    NOT NULL,
    lugar       TEXT    NOT NULL,
    descripcion TEXT    NOT NULL
);

CREATE TABLE declaracion (
    id         INTEGER PRIMARY KEY,
    id_persona INTEGER NOT NULL REFERENCES persona(id),
    texto      TEXT    NOT NULL
);

CREATE TABLE socio_gimnasio (
    codigo     TEXT    PRIMARY KEY,
    id_persona INTEGER NOT NULL REFERENCES persona(id),
    fecha_alta INTEGER NOT NULL,
    estado     TEXT    NOT NULL
);

CREATE TABLE inscripcion_excursion (
    id         INTEGER PRIMARY KEY,
    id_persona INTEGER NOT NULL REFERENCES persona(id),
    destino    TEXT    NOT NULL,
    fecha      INTEGER NOT NULL
);

CREATE TABLE solucion (
    usuario INTEGER,
    valor   TEXT
);
""")

# ----------------------------------------------------------------------
# Personas
# ----------------------------------------------------------------------
NOMBRES = ["Lucia", "Martina", "Sofia", "Julia", "Valeria", "Emma", "Daniela", "Alba",
           "Carmen", "Marta", "Irene", "Nerea", "Claudia", "Ainhoa", "Rocio", "Elena",
           "Paula", "Noelia", "Andrea", "Celia", "Inma", "Marisol", "Silvia", "Vega",
           "Hugo", "Martin", "Mateo", "Leo", "Pablo", "Alvaro", "Adrian", "Diego",
           "Manuel", "Javier", "Marcos", "Sergio", "Ismael", "Rafael", "Nicolas",
           "Antonio", "Curro", "Alonso", "Gonzalo", "Bruno", "Aitor", "Dario", "Iker"]

APELLIDOS = ["Delgado", "Cantero", "Salcedo", "Moreno", "Reina", "Bermudez", "Ocana",
             "Quesada", "Trujillo", "Valverde", "Aguilar", "Zamora", "Palomo", "Cordero",
             "Herrera", "Lobato", "Mansilla", "Pineda", "Rueda", "Sandoval", "Tirado",
             "Ubeda", "Vargas", "Yuste", "Barea", "Carrasco", "Duran", "Espejo",
             "Fuentes", "Gamero", "Higueras", "Jurado", "Lozano", "Marchena", "Nogales",
             "Olmedo", "Pizarro", "Ramirez", "Serrano", "Tinoco", "Utrera", "Vidal"]

CALLES = ["Sierra Nevada", "Alameda", "Los Naranjos", "Guadalquivir", "Blas Infante",
          "Cabo de Gata", "Puerta de Jerez", "Alcazaba", "Rio Genil", "Torre del Oro",
          "Molino Viejo", "Las Adelfas"]

GRUPOS = ["1ESO-A", "1ESO-B", "1ESO-C", "2ESO-A", "2ESO-B", "3ESO-A", "3ESO-B",
          "4ESO-A", "4ESO-B", "1BACH-A", "1BACH-B", "2BACH-A", "2BACH-B"]

usados = set()
def nombre_nuevo(pila=None):
    while True:
        n = "%s %s %s" % (random.choice(NOMBRES), random.choice(APELLIDOS), random.choice(APELLIDOS))
        if n not in usados:
            usados.add(n)
            return n

personas = []          # (id, nombre, grupo, num_lista, calle, numero)
pid = 0
for grupo in GRUPOS:
    n_alumnos = random.randint(22, 28)
    for lista in range(1, n_alumnos + 1):
        pid += 1
        personas.append([pid, nombre_nuevo(), grupo, lista,
                         random.choice(CALLES), random.randint(1, 84)])

# --- Personas clave ---------------------------------------------------
# Testigo 1: el ultimo de la lista de 1BACH-B
t1 = [p for p in personas if p[2] == "1BACH-B"][-1]
t1[1] = "Alonso Pineda Barea"

# Testigo 2: Marisol de la calle Sierra Nevada (unica)
for p in personas:
    if p[1].startswith("Marisol"):
        p[1] = "Nerea" + p[1][7:]          # eliminamos las Marisol generadas al azar
t2 = [p for p in personas if p[2] == "2BACH-A"][4]
t2[1] = "Marisol Cantero Ruiz"
t2[4] = "Sierra Nevada"
t2[5] = 17
# Marisoles señuelo, en otras calles
senuelos_marisol = [p for p in personas if p[2] in ("3ESO-A", "1ESO-C", "4ESO-B")][:3]
for p, calle in zip(senuelos_marisol, ["Alameda", "Rio Genil", "Las Adelfas"]):
    p[1] = "Marisol " + " ".join(p[1].split()[1:])
    p[4] = calle

# Culpable
culpable = [p for p in personas if p[2] == "4ESO-A"][11]
culpable[1] = "Marcos Delgado Rueda"
culpable[4] = "Molino Viejo"
CULPABLE_ID = culpable[0]
CULPABLE_NOMBRE = culpable[1]

# Nadie más se llama igual que el culpable ni que los testigos
assert [p[1] for p in personas].count(CULPABLE_NOMBRE) == 1
assert len([p for p in personas if p[1].startswith("Marisol") and p[4] == "Sierra Nevada"]) == 1
assert len([p for p in personas if p[2] == "1BACH-B" and p[3] == t1[3]]) == 1

cur.executemany("INSERT INTO persona VALUES (?,?,?,?,?,?)", personas)

# ----------------------------------------------------------------------
# Partes de incidencia
# ----------------------------------------------------------------------
LUGARES = ["Hall del instituto", "Pista deportiva", "Biblioteca", "Cafeteria",
           "Aula 12", "Laboratorio", "Gimnasio", "Aparcamiento", "Patio", "Conserjeria"]
TIPOS = ["robo", "pelea", "desperfectos", "perdida", "ruidos"]

RELLENO = [
    "Alguien ha dejado la puerta del laboratorio abierta toda la noche.",
    "Dos alumnos discuten por el turno de la mesa de ping-pong.",
    "Aparece una pintada a rotulador en la puerta del aula.",
    "Se pierde una calculadora cientifica durante el recreo.",
    "Se oyen golpes en la sala de calderas. No se encuentra la causa.",
    "Desaparecen tres balones del almacen de Educacion Fisica.",
    "Un grupo enciende la musica muy alta en el patio a la hora de clase.",
    "Se rompe un cristal de la ventana del pasillo. Nadie declara haberlo visto.",
    "Falta dinero de la hucha del viaje de estudios.",
    "Se atasca la puerta de la biblioteca y hay que llamar al conserje.",
    "Alguien ha movido todas las sillas del salon de actos.",
    "Se pierde un abrigo azul en el vestuario.",
    "Aparecen restos de bocadillo dentro de un ordenador de la sala de informatica.",
    "Dos bicicletas aparecen con las ruedas desinfladas en el aparcamiento.",
    "Se estropea la fotocopiadora despues de un uso indebido.",
]

partes = []
idp = 0
for _ in range(90):
    idp += 1
    mes = random.choice([1, 2, 3])
    dia = random.randint(1, 28)
    partes.append((idp, 20260000 + mes * 100 + dia, random.choice(TIPOS),
                   random.choice(LUGARES), random.choice(RELLENO)))

# Señuelos del mismo dia y del mismo lugar
idp += 1
partes.append((idp, 20260305, "pelea", "Hall del instituto",
               "Dos alumnos se empujan en la fila de la maquina de bebidas. Sin consecuencias."))
idp += 1
partes.append((idp, 20260305, "robo", "Cafeteria",
               "Faltan dos paquetes de galletas del expositor. Se recupera el material."))
idp += 1
partes.append((idp, 20260305, "ruidos", "Hall del instituto",
               "Salta la alarma de incendios sin motivo aparente a las 11:20."))
idp += 1
partes.append((idp, 20260305, "robo", "Hall del instituto",
               "Informe no encontrado."))

# EL PARTE BUENO
idp += 1
PARTE_CLAVE = (idp, 20260305, "robo", "Hall del instituto",
               "Ha desaparecido el trofeo del concurso de robotica de la vitrina. "
               "Hay dos testigos. El primer testigo es la persona de 1BACH-B que ocupa "
               "el numero mas alto de la lista de clase. La segunda testigo se llama "
               "Marisol y vive en la calle Sierra Nevada.")
partes.append(PARTE_CLAVE)

cur.executemany("INSERT INTO parte_incidencia VALUES (?,?,?,?,?)", partes)

# ----------------------------------------------------------------------
# Declaraciones
# ----------------------------------------------------------------------
RELLENO_DECL = [
    "Ese dia no vine a clase, estaba en el dentista.",
    "Yo estaba en el laboratorio con la profesora de Biologia. No vi nada raro.",
    "Vi mucha gente en el pasillo, pero no me fije en nadie en concreto.",
    "Estaba escuchando musica con los auriculares puestos. No me entere de nada.",
    "Creo que oi un ruido, pero pense que era la puerta del gimnasio.",
    "Yo llegue tarde ese dia, ya habia empezado la segunda hora.",
    "Me quede en la biblioteca todo el recreo estudiando para el examen.",
    "Vi a alguien corriendo, pero era Pablo, que siempre llega tarde.",
    "No se nada del trofeo. Ni siquiera sabia que habia una vitrina ahi.",
    "Estaba en la cafeteria. Habia mucha cola y no se veia el hall.",
    "Me sono la alarma del movil y sali al pasillo, pero no vi a nadie.",
    "Ese dia tuvimos examen de Matematicas, no sali del aula en toda la manana.",
]

declaraciones = []
idd = 0
otros = [p for p in personas if p[0] not in (t1[0], t2[0], CULPABLE_ID)]
for p in random.sample(otros, 40):
    idd += 1
    declaraciones.append((idd, p[0], random.choice(RELLENO_DECL)))

idd += 1
declaraciones.append((idd, CULPABLE_ID,
    "Yo ese dia me fui antes de que acabaran las clases, tenia entrenamiento. "
    "No se nada de ningun trofeo."))
idd += 1
declaraciones.append((idd, t1[0],
    "Vi salir a alguien del hall con la mochila muy abultada, casi corriendo. "
    "Llevaba colgada del cuello la tarjeta del gimnasio del instituto y me dio tiempo "
    "a leer el principio del codigo: empezaba por 'GB7'."))
idd += 1
declaraciones.append((idd, t2[0],
    "Yo si reconoci a esa persona, aunque no recuerdo como se llama. Lo que si se es que "
    "se apunto a la excursion a Cordoba del 12 de marzo de 2026."))

cur.executemany("INSERT INTO declaracion VALUES (?,?,?)", declaraciones)

# ----------------------------------------------------------------------
# Socios del gimnasio
# ----------------------------------------------------------------------
socios = []
codigos = set()
socios_ids = random.sample([p[0] for p in personas], 130)
if CULPABLE_ID not in socios_ids:
    socios_ids[0] = CULPABLE_ID

def codigo_nuevo(prefijo=None):
    while True:
        pre = prefijo or random.choice(["GB1", "GB2", "GB3", "GB4", "GB5", "GB6", "GB8", "GB9"])
        c = pre + str(random.randint(1000, 9999))
        if c not in codigos:
            codigos.add(c)
            return c

# 6 socios con codigo GB7..., uno de ellos el culpable
gb7_ids = random.sample([i for i in socios_ids if i != CULPABLE_ID], 5) + [CULPABLE_ID]
for i in socios_ids:
    cod = codigo_nuevo("GB7" if i in gb7_ids else None)
    mes = random.randint(9, 12)
    dia = random.randint(1, 28)
    socios.append((cod, i, 20250000 + mes * 100 + dia,
                   random.choice(["activo", "activo", "activo", "baja"])))

cur.executemany("INSERT INTO socio_gimnasio VALUES (?,?,?,?)", socios)

# ----------------------------------------------------------------------
# Inscripciones a excursiones
# ----------------------------------------------------------------------
DESTINOS = ["Cordoba", "Sierra Nevada", "Cabo de Gata", "Sevilla", "Ronda", "Italica"]
inscripciones = []
idi = 0
for destino in DESTINOS:
    for fecha in (20260212, 20260312, 20260423):
        for i in random.sample([p[0] for p in personas], random.randint(18, 30)):
            idi += 1
            inscripciones.append((idi, i, destino, fecha))

# La excursion clave: exactamente un GB7 dentro
clave = [x for x in inscripciones if x[2] == "Cordoba" and x[3] == 20260312]
inscripciones = [x for x in inscripciones if not (x[2] == "Cordoba" and x[3] == 20260312)]
clave = [x for x in clave if x[1] not in gb7_ids]
idi += 1
clave.append((idi, CULPABLE_ID, "Cordoba", 20260312))
inscripciones.extend(clave)
# Renumeramos para que la fila del culpable no quede delatada por ser la ultima
random.shuffle(inscripciones)
inscripciones = [(n + 1, x[1], x[2], x[3]) for n, x in enumerate(inscripciones)]

cur.executemany("INSERT INTO inscripcion_excursion VALUES (?,?,?,?)", inscripciones)

# ----------------------------------------------------------------------
# Comprobador de la solucion
# ----------------------------------------------------------------------
cur.executescript("""
CREATE TRIGGER comprobar_solucion AFTER INSERT ON solucion
WHEN new.usuario == 1
BEGIN
    DELETE FROM solucion;
    INSERT INTO solucion VALUES (0,
        CASE WHEN lower(trim(new.valor)) == 'marcos delgado rueda'
             THEN 'Correcto: Marcos Delgado Rueda se llevo el trofeo. Caso cerrado, buen trabajo, detective.'
             ELSE 'Esa persona no es. Vuelve a repasar las pistas e intentalo de nuevo.'
        END);
END;
""")

con.commit()

# ----------------------------------------------------------------------
# Verificacion automatica de la cadena de pistas
# ----------------------------------------------------------------------
q = lambda s: cur.execute(s).fetchall()

r = q("SELECT id FROM parte_incidencia WHERE fecha=20260305 AND tipo='robo' AND lugar='Hall del instituto'")
assert len(r) == 2, r                                    # el bueno + 'Informe no encontrado'

r = q("SELECT id, nombre FROM persona WHERE grupo='1BACH-B' ORDER BY num_lista DESC LIMIT 1")
assert r[0][0] == t1[0], r

r = q("SELECT id FROM persona WHERE nombre LIKE 'Marisol%' AND calle='Sierra Nevada'")
assert len(r) == 1 and r[0][0] == t2[0], r

r = q("SELECT id_persona FROM socio_gimnasio WHERE codigo LIKE 'GB7%'")
assert len(r) == 6, r

r = q("""SELECT id_persona FROM inscripcion_excursion
         WHERE destino='Cordoba' AND fecha=20260312
           AND id_persona IN (SELECT id_persona FROM socio_gimnasio WHERE codigo LIKE 'GB7%')""")
assert len(r) == 1 and r[0][0] == CULPABLE_ID, r

n_excursion = q("SELECT count(*) FROM inscripcion_excursion WHERE destino='Cordoba' AND fecha=20260312")[0][0]

print("Base de datos generada:", DB)
print("  personas .................", q("SELECT count(*) FROM persona")[0][0])
print("  partes de incidencia .....", q("SELECT count(*) FROM parte_incidencia")[0][0])
print("  declaraciones ............", q("SELECT count(*) FROM declaracion")[0][0])
print("  socios del gimnasio ......", q("SELECT count(*) FROM socio_gimnasio")[0][0])
print("  inscripciones ............", q("SELECT count(*) FROM inscripcion_excursion")[0][0])
print()
print("  Testigo 1 (1BACH-B, num_lista", str(t1[3]) + ") :", t1[1], "| id", t1[0])
print("  Testigo 2 (Marisol, Sierra Nevada):", t2[1], "| id", t2[0])
print("  Candidatos GB7 ...........", 6)
print("  Inscritos a Cordoba 12/03:", n_excursion)
print("  CULPABLE .................", CULPABLE_NOMBRE, "| id", CULPABLE_ID)

con.close()
