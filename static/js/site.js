function savechanges(itemid, raw_body){
    $.post("/save", { 'entry_id': itemid, 'raw_body': raw_body}, function(data){
	markpageclean();
    });
}

function markpagedirty(){
    document.title += " *";
}

function markpageclean(){
    document.title = document.title.replace(" *", "");
}

$(".editbox").focus(function(e){
    markpagedirty();
});

// Attach the event handler
$(".editbox").blur(function(e){
    savechanges(e.currentTarget.id, e.currentTarget.innerHTML);
});
