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

  // ---------- 3. Tablero de pruebas ----------
  // Tres tiempos: el parte lleva a los testigos, cada testigo a una lista,
  // y las dos listas coinciden en el culpable.
  var tablero = document.getElementById('tablero');
  var botonTablero = document.getElementById('ver-tablero');
  var corcho = tablero && tablero.querySelector('.corcho');
  var hilosSvg = tablero && tablero.querySelector('.hilos');

  // [desde, hasta, momento en ms en que empieza a tenderse el hilo]
  var HILOS = [
    ['parte', 't1', 650], ['parte', 't2', 650],
    ['t1', 'gb7', 1750], ['t2', 'cordoba', 1750],
    ['gb7', 'culpable', 3200], ['cordoba', 'culpable', 3200]
  ];
  // momento en que se clava cada pieza
  var PIEZAS = { parte: 150, t1: 1150, t2: 1150, gb7: 2250, cordoba: 2250, culpable: 3700 };
  var T_COINCIDE = 2850;
  var T_SELLO = 4300;
  var NS = 'http://www.w3.org/2000/svg';

  var chincheta = function (nombre) {
    var c = tablero.querySelector('[data-pieza="' + nombre + '"] .chincheta').getBoundingClientRect();
    var base = corcho.getBoundingClientRect();
    return { x: c.left + c.width / 2 - base.left, y: c.top + c.height / 2 - base.top };
  };

  var dibujarHilos = function () {
    hilosSvg.innerHTML = '';
    HILOS.forEach(function (h) {
      var a = chincheta(h[0]);
      var b = chincheta(h[1]);
      var comba = Math.min(40, Math.hypot(b.x - a.x, b.y - a.y) * 0.12); // el hilo cuelga un poco
      var path = document.createElementNS(NS, 'path');
      path.setAttribute('class', 'hilo');
      path.setAttribute('d', 'M' + a.x + ',' + a.y + ' Q' + (a.x + b.x) / 2 + ',' + ((a.y + b.y) / 2 + comba) + ' ' + b.x + ',' + b.y);
      hilosSvg.appendChild(path);
      path.style.setProperty('--largo', Math.ceil(path.getTotalLength()) + 'px');
      path.style.setProperty('--t', h[2] + 'ms');
    });
  };

  // En pantallas pequeñas el tablero no cabe entero: lo desplazamos para que
  // cada pieza nueva se vea en el momento en que se clava.
  var temporizadores = [];
  var pararSeguimiento = function () {
    temporizadores.forEach(clearTimeout);
    temporizadores = [];
  };
  var seguir = function (nombre, ms) {
    temporizadores.push(setTimeout(function () {
      var pieza = tablero.querySelector('[data-pieza="' + nombre + '"]');
      var r = pieza.getBoundingClientRect();
      var v = tablero.getBoundingClientRect();
      if (r.bottom > v.bottom || r.top < v.top) {
        var suave = !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        pieza.scrollIntoView({ behavior: suave ? 'smooth' : 'auto', block: 'center' });
      }
    }, ms));
  };

  var abrirTablero = function () {
    if (tablero.open) { return; }
    tablero.classList.remove('reproducir', 'saltar');
    Object.keys(PIEZAS).forEach(function (n) {
      tablero.querySelector('[data-pieza="' + n + '"]').style.setProperty('--t', PIEZAS[n] + 'ms');
    });
    tablero.style.setProperty('--t-coincide', T_COINCIDE + 'ms');
    tablero.style.setProperty('--t-sello', T_SELLO + 'ms');
    tablero.showModal();
    dibujarHilos();
    void tablero.offsetWidth; // reinicia las animaciones si se vuelve a abrir
    tablero.classList.add('reproducir');
    tablero.scrollTop = 0;
    pararSeguimiento();
    seguir('gb7', PIEZAS.gb7 - 350);
    seguir('culpable', PIEZAS.culpable - 450);
  };

  if (tablero) {
    tablero.querySelector('[data-cerrar]').addEventListener('click', function () { tablero.close(); });
    tablero.addEventListener('close', function () { pararSeguimiento(); botonTablero.focus(); });
    // Clic en el corcho o fuera del tablero: se salta la animación / se cierra
    corcho.addEventListener('click', function () { pararSeguimiento(); tablero.classList.add('saltar'); });
    tablero.addEventListener('click', function (e) { if (e.target === tablero) { tablero.close(); } });
    botonTablero.addEventListener('click', abrirTablero);
    window.addEventListener('resize', function () { if (tablero.open) { dibujarHilos(); } });
  }

  comprobar.addEventListener('sql-resultado', function (e) {
    var datos = e.detail;
    var mensaje = (datos && datos.length && datos[0].values.length) ? String(datos[0].values[0][0]) : '';
    comprobar.classList.remove('acierto', 'fallo');

    if (/^Correcto/.test(mensaje)) {
      comprobar.classList.add('acierto');
      ponerSello('Caso cerrado', true);
      if (tablero) {
        botonTablero.hidden = false;
        setTimeout(abrirTablero, 700);
      }
    } else if (/no es/.test(mensaje)) {
      comprobar.classList.add('fallo');
    }
  });
})();
