window.post = async (url, json_data) => {
  /* Envía un POST a la url y obtiene una respuesta */
  post = fetch(url, {
    method: "POST",
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(json_data)
    })
    .then(response => response.json())
    .then(jsonResponse => jsonResponse)
    .catch(error => console.log(error))
  return post;
}

async function actualizar_perio() {
  /* Envía un POST a update_perio para actualizar los valores de data
      y obtiene las imágenes en base_64 en la respuesta */

  let previous_data = {};
  fetched_data = await post('update_perio', previous_data);

  // Actualiza las imágenes que correspondan
  for (var key in fetched_data) {
    $('#' + key).attr('src', fetched_data[key]);
  }
}

$(actualizar_perio);
