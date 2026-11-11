// Set up DB
function loadData(dbFile) {
  if (!dbFile) { return; }
  window.worker = new Worker("scripts/worker.sql.js");
  var xhr = new XMLHttpRequest();
  xhr.open('GET', dbFile, true);
  xhr.responseType = 'arraybuffer';
  xhr.onload = () => {
    var uInt8Array = new Uint8Array(xhr.response);
    worker.onmessage = event => {
       if (event.data.ready) {
         query('SELECT 1', (e) => {
           console.log('DB initialization successful');
           document.querySelectorAll("input.sql-exercise-submit").forEach(
             (button) => {button.disabled = false;});
         });
       } else {
         console.log('DB initialization failed');
       }
    }

    worker.postMessage({
      id:1,
      action:'open',
      buffer: uInt8Array,
    });
  }
  xhr.send();
}

function query(sql, cb, err_cb) {
  if (err_cb) {
    worker.onerror = e => err_cb(e);
  } else {
    worker.onerror = e => { throw new Error(e.message); }
  }

  worker.onmessage = event => {
    cb(event.data.results);
  }
  worker.postMessage({
      id: 2,
      action: 'exec',
      sql: sql
  });
}

function datatable (data) {
  var columns = data[0].columns;
  var rows = data[0].values;

  var wrapper = document.createElement('div');
  wrapper.className = 'tabla-scroll';

  var tbl = document.createElement('table');
  tbl.className = 'datatable';

  // cabecera
  var headRow = tbl.createTHead().insertRow();
  columns.forEach((name) => {
    var th = document.createElement('th');
    th.scope = 'col';
    th.textContent = name;
    headRow.appendChild(th);
  });

  // cuerpo
  var tbody = document.createElement('tbody');
  rows.forEach((values) => {
    var tr = tbody.insertRow();
    values.forEach((value) => {
      var td = tr.insertCell();
      if (typeof value === 'number') { td.className = 'numero'; }
      td.textContent = value === null ? 'NULL' : value;
    });
  });
  tbl.appendChild(tbody);
  wrapper.appendChild(tbl);

  var fragment = document.createDocumentFragment();
  fragment.appendChild(wrapper);
  var count = document.createElement('p');
  count.className = 'recuento';
  count.textContent = rows.length === 1 ? '1 fila' : rows.length.toLocaleString('es-ES') + ' filas';
  fragment.appendChild(count);
  return fragment;
}


//////////////////////////
// SQL Exercise Component
//////////////////////////

class sqlExercise extends HTMLElement {
  constructor() {
    super();
  }

  connectedCallback() {
    var question = this.getAttribute('data-question') || '';
    var comment = this.getAttribute('data-comment') || '';
    var defaultText = this.getAttribute('data-default-text') || '';
    var solution = this.getAttribute('data-solution') || '';
    var orderSensitive = this.getAttribute('data-orderSensitive') || false;

    var homeDiv = document.createElement('div');
    homeDiv.className = 'sqlExHomeDiv';

    if (question) {
      var caption = `<div class="sqlExQuestion">${question}</div>`;
      homeDiv.insertAdjacentHTML("beforeend", caption);
    }

    if (comment) {
      var commentbox = `<div class = 'sqlExComment'>${comment}</div>`;
      homeDiv.insertAdjacentHTML("beforeend", commentbox);
    }

    var form = document.createElement('form');

    // Input Area
    var inputArea = document.createElement('div');
    inputArea.className = 'sqlExInputArea';

    var textArea = document.createElement('textarea');
    textArea.textContent = defaultText;
    textArea.name = 'input';
    inputArea.appendChild(textArea);

    var editor = CodeMirror.fromTextArea(textArea, {
      mode: 'text/x-sql',
      indentWithTabs: true,
      smartIndent: true,
      lineNumbers: true,
      textWrapping: false,
      autoRefresh: true,
      theme: 'expediente',
      viewportMargin: Infinity
    });

    editor.setSize('100%', 'auto');
    editor.refresh();

    var runButton = `<input class="sql-exercise-submit" type="submit" value="Ejecutar" disabled>`;
    inputArea.insertAdjacentHTML("beforeend", runButton);

    form['onsubmit'] = (e) => {
      e && e.preventDefault();
      var result_div = document.createElement('div');

      var handleSubmit = (submission_data) => {
        result_div.className = 'returnOkay';

        if (solution) {
          var verdict_div = document.createElement('div');
          result_div.appendChild(verdict_div);

          query(solution, (solution_data) => {
            var submission_u = submission_data[0].values;
            var solution_u = solution_data[0].values;
            if (!orderSensitive) {
                submission_u.sort();
                solution_u.sort();
            }
            var verdict = arraysEqual(submission_u, solution_u) ? "Correcto" : "Incorrecto";
            // http://adripofjavascript.com/blog/drips/object-equality-in-javascript.html
            verdict_div.innerText = verdict;
          });
        }
        if (submission_data.length > 0) {
          result_div.appendChild(datatable(submission_data));
        } else {
          result_div.insertAdjacentHTML("beforeend", `<p class="sin-datos">No se han devuelto datos.</p>`);
        }
        // Avisa a la página del resultado (lo usa scripts/pagina.js para el sello)
        this.dispatchEvent(new CustomEvent('sql-resultado', { detail: submission_data, bubbles: true }));
      }

      var handleError = (e) => {
        result_div.className = 'returnError';
        result_div.innerText = 'Error: ' + e.message.replace(/^Uncaught (Error: )?/, '');
      }

      query(editor.getValue(), handleSubmit, handleError);
      outputBox.innerHTML = '';
      outputBox.appendChild(result_div);
    };

    form['onkeydown'] = (e) => {
      if (e.keyCode == 13 && e.shiftKey) {
        e.preventDefault();
        form.onsubmit();
      };
    };

    if (solution) {
      var solutionButton = document.createElement('input');
      solutionButton.name = 'solution';
      solutionButton.type = 'button';
      solutionButton.value = 'Ver solución';
      solutionButton.onclick = (e) => {
        var existingCode = editor.getValue();
        editor.setValue(existingCode + "\n/* " + solution);
      };
      inputArea.appendChild(solutionButton);
    };

    var resetButton = document.createElement('input');
    resetButton.type = 'button';
    resetButton.value = 'Reiniciar';
    resetButton.onclick = (e) => {
      editor.setValue(defaultText);
      outputBox.textContent = '';
    };
    inputArea.appendChild(resetButton);
    form.appendChild(inputArea);

    // Output Area
    var outputArea = document.createElement('div');
    outputArea.className = 'sqlExOutputArea';

    var outputBox = document.createElement('output');
    outputBox.name = 'output';
    outputArea.appendChild(outputBox);
    form.appendChild(outputArea);

    homeDiv.appendChild(form);
    this.appendChild(homeDiv);
  }
}

customElements.define('sql-exercise', sqlExercise);


//////////////////////////
// Utility functions
//////////////////////////

function arraysEqual(a,b) {
  /*
  https://stackoverflow.com/questions/3115982/how-to-check-if-two-arrays-are-equal-with-javascript
  Array-aware equality checker:
  Returns whether arguments a and b are == to each other;
  however if they are equal-lengthed arrays, returns whether their
  elements are pairwise == to each other recursively under this
  definition.
  */
  if (a instanceof Array && b instanceof Array) {
    if (a.length != b.length) { // assert same length
      return false;
    }
    for (var i=0; i<a.length; i++) { // assert each element equal
      if (!arraysEqual(a[i],b[i]))
        return false;
    }
    return true;
  } else {
    return a == b;  // if not both arrays, should be the same
  }
}
