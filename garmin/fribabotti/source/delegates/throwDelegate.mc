import Toybox.Lang;
import Toybox.WatchUi;
using Toybox.Attention;

enum Vibepattern {
	NEXT_HOLE = 0,
	PREV_HOLE,
	ADD_THROW,
	REMOVE_THROW
}


class throwDelegate extends WatchUi.InputDelegate {
	private var _view;
	private var _submitCourse;
	private var _holdStartTimer;
	private var _isHolding as Boolean = true;
	private var _holdKey;
	private var trackTracker;
	private var throwTracker;

	private var vibeData as Array<Array<Attention.VibeProfile>> = [];


    function initialize(view) {
        InputDelegate.initialize();
		_view = view;
		_submitCourse = new SubmitCourseState(method(:onSubmitDone));
		_holdStartTimer = new Timer.Timer();
		initilizeVibes();
    }

	function onKeyPressed(keyEvent as KeyEvent) as Boolean {
		_isHolding = false;
		if(keyEvent.getKey() == KEY_ENTER){
			// start timer'
			_holdKey = keyEvent.getKey();
			_holdStartTimer.start(method(:onHoldStartTimerEnd), 500, false);
		}else if (keyEvent.getKey() == KEY_ESC){
			_holdKey = keyEvent.getKey();
			_holdStartTimer.start(method(:onHoldStartTimerEnd), 500, false);
		}
		return true;
	}

	function onKey(keyEvent as KeyEvent) as Boolean {
		return true;
	}

	function onKeyReleased(keyEvent as KeyEvent) as Boolean {
		if(trackTracker == null or throwTracker == null){ // not so great fix; drawables are not yet initialized when constructor of delegate runs
			// move to view
			trackTracker = _view.findDrawableById("TrackTracker");
			throwTracker = _view.findDrawableById("ThrowTracker");
		}

		if(!_isHolding){
			_holdStartTimer.stop();
			
			// Regular keypress actions
			if(keyEvent.getKey() == KEY_ENTER){
				if(trackTracker.isLastHole()){
					// submit score and return to session selection
					_submitCourse.makeRequest(throwTracker.getCourseStateArray(), sharedData.getCurrentSessionId());
				} else {
					var new_hole = trackTracker.moveNextHole();
					throwTracker.setHoleIndex(new_hole);
					WatchUi.requestUpdate();
					vibrate(NEXT_HOLE);
				}
			}else if (keyEvent.getKey() == KEY_UP){
				var new_hole = trackTracker.movePrevHole();
				throwTracker.setHoleIndex(new_hole);
				WatchUi.requestUpdate();
				vibrate(PREV_HOLE);
			}else if(keyEvent.getKey() == KEY_DOWN){
				var throwRemoved = throwTracker.removeThrow();
				if(throwRemoved){
					vibrate(REMOVE_THROW);
					System.println("Throw removed");
				}
				WatchUi.requestUpdate();
			}else if(keyEvent.getKey() == KEY_ESC){
				var loc = _view.getGpsLocation();
				throwTracker.addThrow(loc);
				WatchUi.requestUpdate();
				vibrate(ADD_THROW);
			}
		}else{
			// calling while progress is active
			var holdProgress = _view.findDrawableById("HoldProgress");
			if(keyEvent.getKey() == KEY_ENTER){
				_holdStartTimer.stop();
				holdProgress.endProgress();
			}else if (keyEvent.getKey() == KEY_DOWN){
				_holdStartTimer.stop();
				holdProgress.endProgress();
			}
		}
		return true;
	}

	function onHoldStartTimerEnd(){
		_isHolding = true;
		var holdProgress = _view.findDrawableById("HoldProgress");
		var hold_msg = _holdKey == KEY_ESC ? "Hold to delete throw..." : "Going to previous hole...";
		
		holdProgress.startProgress(method(:onHoldActionComplete), hold_msg);
	}

	function onHoldActionComplete(){
		if (_holdKey == KEY_ENTER){
			var new_hole = trackTracker.movePrevHole();
			throwTracker.setHoleIndex(new_hole);
			vibrate(PREV_HOLE);
		}else if(_holdKey == KEY_ESC){
			throwTracker.removeThrow();
			vibrate(REMOVE_THROW);
		}
		
		WatchUi.requestUpdate();
	}

	function onSubmitDone(data as Dictionary?){
		var view = new selectSessionView();
        WatchUi.pushView(view, new sessionSelectDelegate(view), WatchUi.SLIDE_UP);
	}

	function initilizeVibes(){
		// NEXT_HOLE
		vibeData.add([new Attention.VibeProfile(20, 100)]);
		// PREV_HOLE
		vibeData.add([new Attention.VibeProfile(40, 150)]);
		// ADD_THROW
		vibeData.add([new Attention.VibeProfile(40, 50)]);
	 	// REMOVE_THROW
		vibeData.add([new Attention.VibeProfile(40, 70)]);
	}

	function vibrate(pattern as Vibepattern){
		if (Attention has :vibrate) {
			// 3. Trigger the vibration
			Attention.vibrate(vibeData[pattern]);
		}
	}
}