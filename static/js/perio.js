/* Este diccionario almacena los cambios hasta que se envíen al servidor */
var dict_actualizar = { };
var socket = io();

function enviar_update() {
    // Envía los datos al servidor
    dict_actualizar['tmp'] = tmp;
    socket.emit('update_perio', dict_actualizar);
    dict_actualizar = { };
}

socket.on('response_perio', function(imagenes) {
    // Actualiza las imágenes que correspondan
    console.log(Object.keys(imagenes));
    for (var key in imagenes)
        $('#' + key).attr('src', imagenes[key]);
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
  var [diente, titulo] = id.split('-');
  var valor;

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
    if (mostrar) {
      if (quitar_ausente) {
        celdas_columna.children().show();
        celdas_columna.toggleClass('diente_ausente');
      }
    } else {
      celdas_columna.children().hide();
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
    // Actualiza el N.I.
  } else if (tipo == 'ss') {
    // Sangrado o supuración
    valor = [];
    titulo = titulo.slice(0, -1);
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
