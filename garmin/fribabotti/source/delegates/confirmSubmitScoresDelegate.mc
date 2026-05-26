

import Toybox.Lang;
import Toybox.WatchUi;

class ConfirmSubmitScoresDelegate extends WatchUi.ConfirmationDelegate {
	private var _submitCourse;
	private var _throwData;

    function initialize(throwData as Array<Dictionary<String, Array<Dictionary<String, Float or Number or Null>>>>) {
        ConfirmationDelegate.initialize();
		_throwData = throwData;
		_submitCourse = new SubmitCourseState(method(:onSubmitDone));
    }


    function onResponse(response) {
		System.println("dialog callback");
		System.println(response);

        if (response == WatchUi.CONFIRM_YES) {
            System.println("User selected YES");
            // submit score
			_submitCourse.makeRequest(_throwData, sharedData.getCurrentSessionId());
        } 
		// NOTE: there is bug in garmin sdk where on some devices WONT GET THE CONFIRM_NO callback on the dialog screen and the key is send to underlying view/delegate! So "cancel" case is handled in throwdelegate
		
		else if (response == WatchUi.CONFIRM_NO) {
            System.println("User selected NO");
            // Handle the cancellation here
			var transitionTimer = new Timer.Timer();
            transitionTimer.start(method(:delayedViewChange), 100, false);
        }
        // Return true to indicate the input was handled
        return true;
    }

	function onSubmitDone(data as Dictionary?){
		// Todo: push state to onsubmitcallback directly
		if(_submitCourse.state == STATE_OK){
			var transitionTimer = new Timer.Timer();
            transitionTimer.start(method(:delayedViewChange), 100, false);
		}else{
			// tell user we failed
			WatchUi.popView(WatchUi.SLIDE_IMMEDIATE);
            var newMessage = "Submit failed! Try again?";
            // kinda hacky way but 
            WatchUi.pushView(
                new WatchUi.Confirmation(newMessage), 
                new ConfirmSubmitScoresDelegate(_throwData), 
                WatchUi.SLIDE_IMMEDIATE
            );
		}
	}

	function delayedViewChange() as Void{
		_throwData = null;
		_submitCourse = null;
		var view = new selectSessionView();
        WatchUi.switchToView(view, new sessionSelectDelegate(view), WatchUi.SLIDE_UP);
	}

}