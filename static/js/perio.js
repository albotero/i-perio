const sleep = ms => new Promise(r => setTimeout(r, ms));

/* Muestra animación cargando durante mínimo 3 segundos o hasta que cargue la página*/
$(async function() {
  var curr_time = (new Date()).getTime();
  while (curr_time < initial_time + 3000) {
    curr_time = (new Date()).getTime();
    await sleep(500);
  }
  $('div.cargando').toggleClass('cargando');
});


/* Este diccionario almacena los cambios hasta que se envíen al servidor */
var dict_actualizar = { };
var socket = io();

function enviar_update() {
  // Envía los datos al servidor
  dict_actualizar['tmp'] = tmp;
  console.log('enviando...', dict_actualizar);
  socket.emit('update_perio', dict_actualizar);
  dict_actualizar = { };
}

socket.on('response_perio', function(datos) {
  // Actualiza las imágenes que correspondan
  for (var key in datos) {
    console.log('recibido...', Object.keys(datos));

    // Imágenes en la respuesta
    if (key.includes('sup_') || key.includes('inf_'))
      $('#' + key).attr('src', datos[key]);

    // Nivel de inserción
    else if (key.includes('NI'))
      $('#' + key).html(datos[key]);
  }
});

function next_dato(titulo, valor_actual) {
  /* Devuelve la siguiente posibilidad de valor para el dato */
  const lista_opt = {
    'atributos': ['Normal', 'Ausente', 'Extruido', 'Intruido'],
    'VITALIDAD': ['-', '+'],
    'IMPLANTE': ['No', 'Si'],
    'MOVILIDAD': ['-', '1', '2', '3'],
    'PLACA': ['0', '1']
  }[titulo.replace('_', '')];

  // Index actual, si no existe devuelve -1
  var index = lista_opt.indexOf(valor_actual);

  // Si es el último valor, resetea el index
  if (index == lista_opt.length - 1)
    index = -1;

  // Devuelve el siguiente valor
  index++;
  return lista_opt[index];
}

function actualizar_dato(elem, tipo) {
  /* Se ejecuta cuando se hace clic en el elemento */
  var id = $(elem).attr('id');
  var [titulo, diente] = id.split('-');
  var valor;

  $('#frm_perio')[0].reportValidity();

  if (tipo == 'attr') {
    // Atributos
    var quitar_ausente = false;
    // Obtiene el valor siguiente y actualiza el elemento
    if ($(elem).attr('tag') === undefined) {
      valor = next_dato(titulo, next_dato(titulo, $(elem).attr('tag')));
    } else {
      quitar_ausente = $(elem).attr('tag') == 'Ausente';
      valor = next_dato(titulo, $(elem).attr('tag'));
    }
    $(elem).attr('tag', valor);

    // Modifica la columna si el diente es Ausente
    mostrar = valor != 'Ausente';
    celdas_columna = $('td[id^="col' + diente + '"]');
    // Muestra u oculta todos los elementos de esa columna
    // Pinta u oculta un patrón negro en los espacios de los elementos
    if ((mostrar && quitar_ausente) || !mostrar) {
      celdas_columna.toggleClass('diente_ausente');
    }

  } else if (tipo == 'vimp') {
    // Vitalidad, implante, movilidad, placa
    // Obtiene el valor siguiente y actualiza el elemento
    valor = next_dato(titulo, $(elem).html());
    $(elem).html(valor);

  } else if (tipo == 'lmg') {
    // LMG
    valor = $(elem).val();

  } else if (tipo == 'ms') {
    // Margen, Sondaje
    valor = $(elem).val();

  } else if (tipo == 'furca') {
    // Furca
    $(elem).val(function() { return this.value.toUpperCase(); });
    valor = $(elem).val();

  } else if (tipo == 'ss') {
    // Sangrado o supuración
    valor = [];
    diente = diente.slice(0, -1);
    for (var i = 0; i < 3; i++) {
      var checkbox = id.slice(0, -1) + i;
      valor.push($('#' + checkbox).prop('checked'));
    }
  }

  // Agrega los datos al diccionario
  dict_actualizar[diente] = {};
  dict_actualizar[diente][titulo] = valor;
  enviar_update();
}
