# El Misterio del Trofeo Robado

Caso de iniciación a SQL pensado como **paso previo** a
[El Misterio del Asesinato en SQL](https://juanlu101.github.io/Asesinato-Base-de-Datos/).
Todo funciona en el navegador (SQL.js + WebAssembly), sin servidor ni instalación.

**Se resuelve sin usar `JOIN`.** Cada pista se obtiene con una consulta a una sola tabla;
el alumnado encadena resultados a mano.

---

## Poner en marcha en GitHub Pages

1. Crea un repositorio nuevo (por ejemplo `Misterio-Trofeo`) y sube todo el contenido de esta carpeta a la raíz.
2. *Settings → Pages → Source*: `Deploy from a branch`, rama `main`, carpeta `/ (root)`.
3. En un par de minutos estará en `https://TU-USUARIO.github.io/Misterio-Trofeo/`.

No hace falta tocar nada más: la página carga `misterio-trofeo.db` con una ruta relativa.

---

## Contenido

| Archivo | Qué es |
|---|---|
| `index.html` | La página del caso |
| `misterio-trofeo.db` | Base de datos SQLite |
| `generar_db.py` | Script que genera la base de datos (para regenerarla o modificar el caso) |
| `esquema.svg` | Diagrama del esquema |
| `vitrina.svg` | Ilustración de cabecera |
| `css/`, `scripts/` | Estilos y componentes del editor SQL |

Para regenerar la base de datos tras editar el script: `python3 generar_db.py`
(no necesita librerías externas; el script se autocomprueba y aborta si la cadena de pistas se rompe).

---

## Esquema

```
persona(id, nombre, grupo, num_lista, calle, numero)
parte_incidencia(id, fecha, tipo, lugar, descripcion)
declaracion(id, id_persona→persona, texto)
socio_gimnasio(codigo, id_persona→persona, fecha_alta, estado)
inscripcion_excursion(id, id_persona→persona, destino, fecha)
solucion(usuario, valor)          -- comprobador, con trigger
```

Las fechas son enteros `AAAAMMDD`. Ningún dato lleva tilde, para evitar problemas al teclear.

---

## SOLUCIÓN (para el profesorado)

<details>
<summary>Desplegar</summary>

**Culpable: Marcos Delgado Rueda** (`id` 193, 4ESO-A).

```sql
-- 1. El parte del robo (salen dos; uno dice "Informe no encontrado")
SELECT * FROM parte_incidencia
WHERE fecha = 20260305 AND tipo = 'robo' AND lugar = 'Hall del instituto';

-- 2a. Testigo 1: el último de la lista de 1BACH-B  → Alonso Pineda Barea, id 279
SELECT * FROM persona
WHERE grupo = '1BACH-B'
ORDER BY num_lista DESC
LIMIT 1;

-- 2b. Testigo 2: Marisol de la calle Sierra Nevada → Marisol Cantero Ruiz, id 284
--     (hay 4 Marisol en el centro; solo una vive ahí)
SELECT * FROM persona
WHERE nombre LIKE 'Marisol%' AND calle = 'Sierra Nevada';

-- 3. Las dos declaraciones
SELECT texto FROM declaracion WHERE id_persona = 279;   -- código del gimnasio: empieza por GB7
SELECT texto FROM declaracion WHERE id_persona = 284;   -- excursión a Córdoba del 12/03/2026

-- 4a. Seis candidatos
SELECT * FROM socio_gimnasio WHERE codigo LIKE 'GB7%';

-- 4b. Cruce a mano (21 inscritos a la excursión, solo uno es candidato)
SELECT * FROM inscripcion_excursion
WHERE destino = 'Cordoba' AND fecha = 20260312
  AND id_persona IN (20, 51, 139, 170, 193, 282);

-- 5. El nombre
SELECT * FROM persona WHERE id = 193;

-- 6. Comprobar
INSERT INTO solucion VALUES (1, 'Marcos Delgado Rueda');
SELECT valor FROM solucion;
```

Los `id` del paso 4b son los que devuelve el paso 4a; cambian si se regenera la base de datos
con otra semilla. La comprobación final ignora mayúsculas y espacios sobrantes.

</details>

---

## Qué practica cada paso

| Paso | Contenido de SQL |
|---|---|
| 1 | `SELECT … WHERE` con varias condiciones y `AND` |
| 2a | `ORDER BY … DESC` + `LIMIT` |
| 2b | `LIKE` con comodín `%` |
| 3 | Filtrar por clave ajena (`id_persona`) |
| 4 | `LIKE` de prefijo e `IN` con una lista de valores |

---

## Créditos

Inspirado en el [SQL Murder Mystery](https://mystery.knightlab.com/) del Knight Lab de la
Universidad Northwestern, creado por Joon Park y Cathy He y producido para la web por Joe Germuska
([repositorio original](https://github.com/NUKnightLab/sql-mysteries)).
Componentes del editor de Zi Chong Kao ([Select Star SQL](https://selectstarsql.com/)).
Motor SQL en el navegador: [SQL.js](https://github.com/sql-js/sql.js/).

Código bajo licencia MIT. Textos y contenido bajo
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.es).
