notices = [];
checkactive = false;

function savechanges(itemid, raw_body){
    $.post("/save", { 'entry_id': itemid, 'raw_body': raw_body}, function(data){
	markpageclean();
	notify_save_successful(itemid);
	setTimeout(function(){
	    spanid = "notice_" + itemid.replace(".","");
	    $("#" + spanid).fadeOut(300, function() {$("#" + spanid).remove()});
	}, 2000);
    });
}

function markpagedirty(){
    document.title += " *";
}

function markpageclean(){
    document.title = document.title.replace(" *", "");
}

function checker(){
    if (notices.length > 0){
	console.log("# of notices:" + notices.length);
	console.log(notices);
    }
}

function notify_save_successful(itemid){
    spanid = "notice_" + itemid.replace(".","");
    notice = "<span id='" + spanid + "' class='notice'>save complete!</span>";
    $("#notifications").prepend(notice);


}


$(".editbox").focus(function(e){
    markpagedirty();
});

// Attach the event handler
$(".editbox").blur(function(e){
    savechanges(e.currentTarget.id, e.currentTarget.innerHTML);
});
