function actualizar_perio(previous_data = {}) {
  /* Envía un POST a update_perio para actualizar los valores de data
      y obtiene las imágenes en base_64 en la respuesta */
  console.log("Actualizando", previous_data);
  $.post(
    'update_perio',
    previous_data,
    function(response) {
      // Actualiza las imágenes que correspondan
      for (var key in response)
        $('#' + key).attr('src', response[key]);
    },
    "json"
  );
}

$(actualizar_perio());

function next_dato(titulo, valor_actual) {
  /* Devuelve la siguiente posibilidad de valor para el dato */
  const lista_opt = {
    'VITALIDAD': ['-', '+'],
    'IMPLANTE': ['No', 'Si'],
    'MOVILIDAD': ['-', '1', '2', '3'],
    'FURCA': ['-', 'I', 'II', 'III'],
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

function actualizar_dato(elem) {
  /* Se ejecuta cuando se hace clic en el elemento */
  var id = $(elem).attr("id");
  var [diente, titulo] = id.split('_');
  // Actualiza el valor en el perio
  var valor = next_dato(titulo, $(elem).html());
  $(elem).html(valor);
  // Actualiza la imagen
  json_data = {};
  json_data[diente] = {};
  json_data[diente][titulo] = valor;
  actualizar_perio(json_data);
}
