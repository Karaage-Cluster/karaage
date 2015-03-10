$( document ).ready(function() {
    $.each($(".hidden-link"), function (index, element) {
        void index;
        void element;
        $(this).find("a").on("click", function(ev) {
            var hl = $(this).parent().parent();
            var next = hl.next();
            while (next.length > 0) {
                next.show("slow");
                next = next.next();
            }
            hl.remove();
            ev.preventDefault();
        });
        var next = $(this).next();
        while (next.length > 0) {
            next.hide();
            next = next.next();
        }
    });

    var dialog = $( "#dialog-modal" ).dialog({
        autoOpen: false,
        height: 480,
        width: 400,
        modal: true,
        buttons: {
            "ok": function() {
                $( "#dialog-modal" ).submit();
            },
            "cancel": function() {
                $( this ).dialog( "close" );
            }
        }
    });

    dialog.keyup(function (event) {
        if (event.keyCode == 13) {
            $( "#dialog-modal" ).submit();
            event.preventDefault();
        }
    });

    $( "#opener" ).click(function() {
        dialog.dialog( "open" );
    });

});
