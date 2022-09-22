let socket = io();

function redirect(url, method, datos) {
  html = `<form action="${url}" method="${method}">`;
  for (var key in datos) {
    html += `<input type="hidden" name="${key}" value="${datos[key]}" />`
  }
  html += `</form>`
  $(html).appendTo('body').submit().remove();
}

async function submit_form(url, form) {
  return await fetch(url, {
    method : "POST",
    body: new FormData(form)
  }).then(
    response => response.text()
  ).then(
    res => res
  );
}

$.extend({
  confirm: function(titulo, mensaje, texto_si, funcion_si, texto_no, cerrar=true) {
    $('<div></div>').dialog({
      // Remove the closing 'X' from the dialog
      open: function(event, ui) { $('.ui-dialog-titlebar-close').hide(); },
      width: 400,
      buttons: [{
        text: texto_si,
        click: function() {
          funcion_si();
          if (cerrar) $(this).dialog('close');
        }
      },
      {
        text: texto_no,
        click: function() {
          $(this).dialog('close');
        }
      }],
      close: function(event, ui) { $(this).remove(); },
      resizable: false,
      title: titulo,
      modal: true
    }).html(mensaje);
  }
});

$.extend({
  alert: function(titulo, mensaje, texto_ok) {
    $('<div></div>').dialog({
      // Remove the closing 'X' from the dialog
      open: function(event, ui) { $('.ui-dialog-titlebar-close').hide(); },
      width: 400,
      buttons: [{
        text: texto_ok,
        click: function() {
          $(this).dialog('close');
        }
      }],
      close: function(event, ui) { $(this).remove(); },
      resizable: false,
      title: titulo,
      modal: true
    }).html(mensaje);
  }
});
