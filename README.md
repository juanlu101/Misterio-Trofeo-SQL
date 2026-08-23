# El Misterio del Trofeo Robado

Caso de iniciación a SQL pensado como **paso previo** a
[El Misterio del Asesinato en SQL](https://juanlu101.github.io/Asesinato-Base-de-Datos/).
Todo funciona en el navegador (SQL.js + WebAssembly), sin servidor ni instalación.

**Se resuelve sin usar `JOIN`.** Cada pista se obtiene con una consulta a una sola tabla;
el alumnado encadena resultados a mano.

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

## Créditos

Realizado por Juan Luis Torralbo e inspirado en el [SQL Murder Mystery](https://mystery.knightlab.com/) del Knight Lab de la
Universidad Northwestern, creado por Joon Park y Cathy He y producido para la web por Joe Germuska
([repositorio original](https://github.com/NUKnightLab/sql-mysteries)).
Componentes del editor de Zi Chong Kao ([Select Star SQL](https://selectstarsql.com/)).
Motor SQL en el navegador: [SQL.js](https://github.com/sql-js/sql.js/).

Código bajo licencia MIT. Textos y contenido bajo
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.es).
