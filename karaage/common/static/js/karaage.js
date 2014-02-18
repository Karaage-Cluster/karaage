
function showHidden() {
  $("#hidden-link").hide("fast");
  $("#hidden").slideDown("slow");
}

$( document ).ready(function() {
    $('.object-tools li').each(function() {
        $(this).click(function(ev) {
            ev.preventDefault();
            var a = $(this).find("a");
            if (a.length > 0) {
                window.location.href = a.attr('href');
            }
        });
    });
});
