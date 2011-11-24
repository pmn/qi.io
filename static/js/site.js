function savechanges(itemid, raw_body){
    console.log(itemid);
    console.log(raw_body);

    $.post("/save", { 'entry_id': itemid, 'raw_body': raw_body}, function(data){
	console.log(data);
    });
}

// Attach the event handler
$(".edit_area").blur(function(e){
    savechanges(e.currentTarget.id, e.currentTarget.innerHTML);
});
