function savechanges(itemid, raw_body){
    $.post("/save", { 'entry_id': itemid, 'raw_body': raw_body}, function(data){
	markpageclean();
	notify_save_successful();
    });
}

function markpagedirty(){
    document.title += " *";
}

function markpageclean(){
    document.title = document.title.replace(" *", "");
}

function notify_save_successful(){
    $("#savecomplete").show();
    
    setTimeout(function(){
	$("#savecomplete").fadeOut(300);
    }, 2000);

}

$(".editbox").focus(function(e){
    markpagedirty();
});

// Attach the event handler
$(".editbox").blur(function(e){
    savechanges(e.currentTarget.id, e.currentTarget.innerHTML);
});
