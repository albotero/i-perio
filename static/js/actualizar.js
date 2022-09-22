socket.on('response_time', function(datos) {
  // Actualiza hora y créditos
  for (var val in datos) {
    $(`#${val}`).text(datos[val]);
  }

  if ($('#cred').text().replace('.', '') <= 15) {
    $('#cred').toggleClass('alerta');
    $('#cred-tiempo').toggleClass('alerta');
  }
});

socket.on('redirect', function(datos) {
  try {
    redirect(datos.url, 'post', {'tmp': tmp}, 'get');
  }
  catch {}
});
