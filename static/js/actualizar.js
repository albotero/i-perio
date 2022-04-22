const sleep = ms => new Promise(r => setTimeout(r, ms));
var socket = io();

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

function redirect(url, method, datos) {
  html = `<form action="${url}" method="${method}">`;
  for (var key in datos) {
    html += `<input type="hidden" name="${key}" value="${datos[key]}" />`
  }
  html += `</form>`
  $(html).appendTo('body').submit().remove();
}

socket.on('redirect', function(datos) {
  try {
    redirect(datos.url, 'post', {'tmp': tmp}, 'get');
  }
  catch {}
});
