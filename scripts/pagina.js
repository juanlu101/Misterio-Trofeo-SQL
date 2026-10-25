// Interacciones propias de esta página:
//  1. En el esquema, al señalar una tabla se resaltan sus relaciones.
//  2. Al comprobar la solución, el sello de la portada cambia de estado.

(function () {
  // ---------- 1. Esquema ----------
  var svg = document.querySelector('.esquema-svg');
  if (svg) {
    var limpiar = function () {
      svg.classList.remove('enfoque');
      svg.querySelectorAll('.activa').forEach(function (el) { el.classList.remove('activa'); });
    };

    var resaltar = function (nombre) {
      limpiar();
      svg.classList.add('enfoque');
      svg.querySelector('[data-tabla="' + nombre + '"]').classList.add('activa');
      svg.querySelectorAll('.relacion').forEach(function (rel) {
        var tablas = rel.dataset.tablas.split(' ');
        if (tablas.indexOf(nombre) !== -1) {
          rel.classList.add('activa');
          tablas.forEach(function (t) {
            svg.querySelector('[data-tabla="' + t + '"]').classList.add('activa');
          });
        }
      });
    };

    svg.querySelectorAll('.tabla').forEach(function (tabla) {
      var nombre = tabla.dataset.tabla;
      tabla.addEventListener('mouseenter', function () { resaltar(nombre); });
      tabla.addEventListener('focus', function () { resaltar(nombre); });
      tabla.addEventListener('mouseleave', limpiar);
      tabla.addEventListener('blur', limpiar);
    });
  }

  // ---------- 2. Sello ----------
  var sello = document.getElementById('sello');
  var comprobar = document.getElementById('comprobar');
  if (!sello || !comprobar) { return; }

  var ponerSello = function (texto, cerrado) {
    if (sello.textContent === texto) { return; }
    sello.textContent = texto;
    sello.classList.toggle('cerrado', cerrado);
    sello.classList.remove('reestampar');
    void sello.offsetWidth; // reinicia la animación
    sello.classList.add('reestampar');
  };

  comprobar.addEventListener('sql-resultado', function (e) {
    var datos = e.detail;
    var mensaje = (datos && datos.length && datos[0].values.length) ? String(datos[0].values[0][0]) : '';
    comprobar.classList.remove('acierto', 'fallo');

    if (/^Correcto/.test(mensaje)) {
      comprobar.classList.add('acierto');
      ponerSello('Caso cerrado', true);
    } else if (/no es/.test(mensaje)) {
      comprobar.classList.add('fallo');
    }
  });
})();
