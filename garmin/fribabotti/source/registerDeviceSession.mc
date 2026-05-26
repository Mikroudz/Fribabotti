import Toybox.System;
import Toybox.Communications;
import Toybox.Lang;

class RegisterDeviceSession {

	var state as RequestState = STATE_IDLE;
	var _callback;

	function initialize(callback) {
		_callback = callback;
	}

	function onReceive(responseCode as Number, data as Dictionary?) as Void {
        if (responseCode == 200) {
            System.println("Post Successful");                   // print success
			state = STATE_OK;
			_callback.invoke(data);
        } else {
            System.println("Response: " + responseCode);            // print response code
			state = STATE_ERROR;
            _callback.invoke({});
        }

    }

	function makeRequest(device_id as Number) as Void {
        var url = "https://kiisu.club/fribabotti/api/v1/auth/";

        var params = {"device_id" => device_id};
        var options = {                                             // set the options
            :method => Communications.HTTP_REQUEST_METHOD_POST,      // set HTTP method
            :headers => {                                           // set headers
            "Content-Type" => Communications.REQUEST_CONTENT_TYPE_JSON},
            // set response type
            :responseType => Communications.HTTP_RESPONSE_CONTENT_TYPE_JSON
        };
		state = STATE_PENDING;
        // onReceive() method
        // Make the Communications.makeWebRequest() call
        Communications.makeWebRequest(url, params, options, method(:onReceive));
    }
}