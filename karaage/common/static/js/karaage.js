$( document ).ready(function() {
    $.each($(".hidden-link"), function (index, element) {
        $(this).find("a").on("click", function(ev) {
            var hl = $(this).parent().parent()
            var next = hl.next()
            while (next.length > 0) {
                next.show("slow");
                next = next.next();
            }
            hl.remove();
            ev.preventDefault();
        })
        var next = $(this).next()
        while (next.length > 0) {
            next.hide();
            next = next.next();
        }
    })
})
