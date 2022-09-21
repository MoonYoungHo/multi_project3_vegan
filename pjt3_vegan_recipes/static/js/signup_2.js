$(window).on('load', function() {
    for (var i = 1; i < 6; i++) {
        $('#choose' + i).click(function() {
            alert("선택" + i);
        });
    }
});