(function(){
    htmx.defineExtension('my-ext', {
        onEvent : function(name, evt) {
            console.log("Fired event: " + name, evt);
        }
    })
})()