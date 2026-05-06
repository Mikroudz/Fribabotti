import Toybox.Lang;
import Toybox.Application.Storage;

class SharedData {
	var _selected_session_id;
	var _course_data;
	var _vibration_enabled = true;
	var _auth_token as String = "";

	function initialize(){
		var vibRead = Storage.getValue("vibrations");
		if(vibRead != null){
			_vibration_enabled = vibRead;
		}
		var token = Storage.getValue("auth_token");
		if(token != null){
			_auth_token = token;
		}

	}

	function setCurrentSessionId(id as Number){
		_selected_session_id = id;
	}

	function getCurrentSessionId() as Number{
		return _selected_session_id;
	}

	function setCurrentCourse(data as Dictionary?){
		_course_data = data;
	}
	
	function getCurrentCourse() as Dictionary{
		return _course_data;
	}

	function setUseVibrations(value as Boolean){
		Storage.setValue("vibrations", value);
		_vibration_enabled = value;
	}

	function getUseVibrations() as Boolean {
		return _vibration_enabled;
	}

	function setAuthToken(token as String) {
		_auth_token = token;
		Storage.setValue("auth_token", token);
	}

	function getAuthToken() as String {
		return _auth_token;
	}

}

var sharedData = new SharedData();