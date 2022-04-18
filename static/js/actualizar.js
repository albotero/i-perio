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

function redirect_post(url, datos) {
  html = `<form action="${url}" method="post">`;
  for (var key in datos) {
    html += `<input type="hidden" name="${key}" value="${datos[key]}" />`
  }
  html += `</form>`
  $(html).appendTo('body').submit().remove();
}

socket.on('redirect', function(datos) {
  redirect_post(datos.url, {'tmp': tmp});
});
