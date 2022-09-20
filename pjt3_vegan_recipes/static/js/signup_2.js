$(document).ready(function(){
    for (var i=1; i < 6; i++){
        $('#pic' + i).click(function(e){
            alert(this.id);
        });
    }
});