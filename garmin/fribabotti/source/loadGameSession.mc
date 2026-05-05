import Toybox.System;
import Toybox.Communications;
import Toybox.Lang;

class LoadGameSession {

	var state as RequestState = STATE_IDLE;
	var _callback;

	function initialize() {
	}


	function onReceive(responseCode as Number, data as Dictionary?) as Void {
        if (responseCode == 200) {
            System.println("Request Successful");                   // print success
			state = STATE_OK;
			_callback.invoke(data);
        } else {
            System.println("Response: " + responseCode);            // print response code
			state = STATE_ERROR;
        }

    }

	function makeRequest(session_id, callback) as Void {
        var url = "https://kiisu.club/fribabotti/game/" + session_id; 
        var options = {                                             // set the options
            :method => Communications.HTTP_REQUEST_METHOD_GET,      // set HTTP method
            :headers => {                                           // set headers
            "Content-Type" => Communications.REQUEST_CONTENT_TYPE_JSON},
            // set response type
            :responseType => Communications.HTTP_RESPONSE_CONTENT_TYPE_JSON
        };
		state = STATE_PENDING;
        _callback = callback;
        
        Communications.makeWebRequest(url, {}, options, method(:onReceive));
    }
}

var session_fetcher = new LoadGameSession();