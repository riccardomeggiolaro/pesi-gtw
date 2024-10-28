$(document).ready(function() {
    var table = $('#example').DataTable( {
        lengthChange: true,
        "searching": false,
        order: []
    } );
 
    table.buttons().container()
        .appendTo( '#example_wrapper .col-md-6:eq(0)' );
} );

// Seleziona la tabella
const table = document.querySelector('table');

// Aggiungi un gestore di eventi per ogni cella
table.querySelectorAll('td').forEach(cell => {
  cell.addEventListener('keydown', function(event) {
    if (event.key === '-') {
      event.preventDefault();
      // Esegui qui il tuo codice personalizzato se necessario
    }
  });
});
