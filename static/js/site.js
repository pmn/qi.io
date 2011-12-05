function savechanges(itemid, raw_body){
    $.post("/save", { 'entry_id': itemid, 'raw_body': raw_body}, 
	   function(data){
	       afterSave(data);
	   },
	  "json"
	  );
}

function updateEntryText(entry){
    $('div[id="' + entry.id + '"]').html(entry.body);
}

function updateEntryTags(entry){
    var tagbox = $('span[id="tags_' + entry.id +'"]');
    tagbox.empty();

    for (var tag in entry.tags){
	thistag = entry.tags[tag];

	tagdata = "<span class='entrytag label' id='topic_" + thistag + "'>";
	tagdata += "<a href='/topic/" + thistag + "'>" + thistag + "</a>";
	tagdata += "</span> ";
	tagbox.append(tagdata);
    }
}

function afterSave(data){
    // Handle anything that occurs after we receive a save. 
    entry = eval("(" + data + ")");
    updateEntryText(entry);
    updateEntryTags(entry);
    completeEdit(entry.id);
    
    notify_save_successful();
}

function beginEdit(entryid){
    // Switch a div to a textbox for editing
    markpagedirty();
    editbox =  $('textarea[id="' + entryid +'"]');
    displaybox = $('div[id="' + entryid +'"]');

    displaybox.hide();
    editbox.show();
    $('textarea[id="' + entryid + '"]').autogrow();
    editbox.focus();
}

function completeEdit(entryid){
    // Switch a textbox back to a rendered div after saving
    markpageclean();
    editbox =  $('textarea[id="' + entryid +'"]');
    displaybox = $('div[id="' + entryid +'"]');

    if (entryid != "scratchpad"){
	editbox.hide();
    };

    displaybox.show();
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

    markpageclean();
}

function deleteEntry(entryid){
    // delete an entry
    var answer = confirm("Really delete this entry?");

    if (answer){
	$.post("/delete", { 'entry_id': entryid }, 
	       function(data){
		   $('div[id="entry_' + entryid + '"]').fadeOut();
	       });
    }
}

$(".editbox").focus(function(e){
    // Nothing to do right now - later this will be used to track whether something has changed
});

// Attach the event handler
$(".editbox").blur(function(e){
    savechanges(e.currentTarget.id, e.currentTarget.value);
});


// Attach the doubleclick handler
$(".displaybox").on("dblclick", function(event){
    beginEdit($(this).attr("id"));
});

// Set up textarea auto-growing
$('textarea[id="scratchpad"]').autogrow();
