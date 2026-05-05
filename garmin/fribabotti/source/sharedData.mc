

import Toybox.Lang;

class SharedData {
	var _selected_session_id;
	var _course_data;

	function initialize(){
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

}

var sharedData = new SharedData();