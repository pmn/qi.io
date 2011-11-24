function savechanges(itemid, data){
    console.log(itemid);
    console.log(data);
}

// Attach the event handler
$(".edit_area").blur(function(e){
    console.log('blur event fired:');
    console.log(e);
    savechanges(e.currentTarget.id, e.currentTarget.innerHTML);
});
