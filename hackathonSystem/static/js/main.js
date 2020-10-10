$(function() {
    if ((location.pathname.split("/")[1]) !== ""){
        $('nav a[href^="/' + location.pathname.split("/")[1] + '"]').addClass('active');
    }
});

// $(document).ready(function () {
//     window.setTimeout(function() {
//       $(".alert-fade").fadeTo(1000, 0).slideUp(1000, function(){
//         $(this).remove();
//       });
//     }, 1000);
//   });

$('#redirect').on('change', function() {
  window.location.replace(this.value);
});