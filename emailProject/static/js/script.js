function recieveData(){
    $.post("/login_auth", function(data) {
       message = $.parseJSON(data);
       console.log(message);
    })
 }