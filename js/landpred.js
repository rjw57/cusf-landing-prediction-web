// Use the Google AJAX API to load jQuery and mootools.
google.load("jquery", "1.3.2");
google.load("jqueryui", "1.7.2");
google.load("mootools", "1.2.4");

var newpred_root = 'newpred.cgi/'

function error(title, messageHtml) {
	$('#errordialog').html(messageHtml).dialog('option', 'title', title).dialog('open');
}

function newPredCallback(data, textStatus) {
}

function submitForm() {
	function errFunc(request, textStatus) {
		$('#waitingdialog').dialog('close');
		error('Error running prediction', request.responseText);
	}

	function successFunc(data, textStatus) {
		$('#waitingdialog').dialog('close');
		var pred_root = 'predictions/' + $.trim(data) + '/'
		var html = '<p>Success: <a href="' + pred_root + 'log">log</a>, ' +
			'<a href="' + pred_root + 'output">output</a>, ' +
			'<a href="' + pred_root + 'output.kml">KML output</a></p>';
		$('#success').html(html);
	}

	$('#waitingdialog').dialog('open');
	$.ajax( {
		contentType: 'application/json',
		data: formToJSON('form#scenario'),
		dataType: 'text',
		error: errFunc,
		success: successFunc,
		type: 'POST',
		url: newpred_root
	});
}

function formToJSON(form) {
	// the scenario JSON document.
	var scenario = { };

	// input elements whose name matches this regexp are considered part of
	// the scenario.
	var element_regexp = new RegExp('^([^:]*):([^:]*)$');

	// iterate over each input element in the form...
	$(form).find('input').each(function() {
		// see if the name matches the regexp above.
		var match = element_regexp.exec($(this).attr('name'));

		// if it does, insert the value into the JSON
		if( match != null ) {
			if( scenario[match[1]] == undefined ) {
				scenario[match[1]] = { };
			}
			scenario[match[1]][match[2]] = $(this).attr('value');
		}
	});

	// return the scenario as a JSON document.
	return JSON.encode(scenario);
}

google.setOnLoadCallback(function() {
	$('#errordialog').dialog( { 
		autoOpen: false, 
		modal: true, 
		dialogClass: 'alert',
		width: 640,
		height: 480,
		buttons: 
		  { 
			Ok: function() 
			  { 
				$(this).dialog('close'); 
			  }
		  } 
	} );
	$('#waitingdialog').dialog( {
		autoOpen: false,
		modal: true,
		dialogClass: 'message',
		resizable: false,
		draggable: false,
	})
	$('#scenario input[name=submit]').click(submitForm);
})
