/* Este diccionario almacena los cambios hasta que se envíen al servidor */
var dict_actualizar = { };
var actualizando = false;

function actualizar_perio(previous_data = {}) {
  /* Envía un POST a update_perio para actualizar los valores de data
      y obtiene las imágenes en base_64 en la respuesta */
  console.log("Actualizando", previous_data);
  $.ajax({
    type: "POST",
    url: "update_perio",
    // The key needs to match your method's input parameter (case-sensitive).
    data: JSON.stringify(previous_data),
    contentType: "application/json; charset=utf-8",
    dataType: "json",
    success: function(response) {
      // Actualiza las imágenes que correspondan
      console.log(Object.keys(response));
      for (var key in response)
        $('#' + key).attr('src', response[key]);
      // Indica que ya terminó
      actualizando = false;
    },
    error: function(errMsg) {console.log(errMsg);}
  });
}

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
  var id = $(elem).attr("id");
  var [diente, titulo] = id.split('-');
  var valor;

  if (tipo == 'attr') {
    // Atributos
    // Obtiene el valor siguiente y actualiza el elemento
    if ($(elem).attr('tag') === undefined)
      valor = next_dato(titulo, next_dato(titulo, $(elem).attr('tag')));
    else
      valor = next_dato(titulo, $(elem).attr('tag'));
    $(elem).attr('tag', valor);
  } else if (tipo == 'vimp') {
    // Vitalidad, implante, movilidad, placa
    // Obtiene el valor siguiente y actualiza el elemento
    valor = next_dato(titulo, $(elem).html());
    $(elem).html(valor);
  } else if (tipo == 'ms') {
    // Margen, Sondaje
    // Actualiza el N.I.
    valor = $(elem).val();
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
}

setInterval(function enviar_datos_servidor() {
  /* Se ejecuta cada 2000ms, si hay datos para enviar los envía */
  if ($.isEmptyObject(dict_actualizar)) return;
  if (actualizando) return;
  // Prepara los datos para enviar
  json_data = dict_actualizar;
  json_data['tmp'] = tmp;
  // Quita los cambios de la variable
  dict_actualizar = { };
  actualizando = true;
  // Envía los datos al servidor
  actualizar_perio(json_data);
}, 2000);
