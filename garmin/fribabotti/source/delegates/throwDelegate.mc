import Toybox.Lang;
import Toybox.WatchUi;
using Toybox.Attention;
using Toybox.Timer;

enum Vibepattern {
	NEXT_HOLE = 0,
	PREV_HOLE,
	ADD_THROW,
	REMOVE_THROW
}


class throwDelegate extends WatchUi.InputDelegate {
	private var _view;
	private var _holdStartTimer as Timer.Timer?;
	private var _holdKey;
	private var trackTracker;
	private var throwTracker;
	private var holdProgress as ButtonHoldProgressDrawable?;
	private var _had_hold_progress as Boolean = false;

	private var vibeData as Array<Array<Attention.VibeProfile>> = [];
	// no other way to track this for dismissing the game
	private var _endGameDialogOpen as Boolean = false;


    function initialize(view) {
        InputDelegate.initialize();
		_view = view;
		_holdStartTimer = new Timer.Timer();
		initilizeVibes();
    }

	function onKeyPressed(keyEvent as KeyEvent) as Boolean {
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
			holdProgress = _view.findDrawableById("HoldProgress");
		}
		//System.println("Key release event");
		//System.println(keyEvent.getKey());

		// we need to skip release event after progress has finished to prevent extra presses from occurring on release
		if(_had_hold_progress){
			_had_hold_progress = false;
			return true;
		}

		if(!holdProgress.isHolding()){
			_holdStartTimer.stop();
			
			// Regular keypress actions
			if(keyEvent.getKey() == KEY_ENTER){
				if(trackTracker.isLastHole()){
					_endGameDialogOpen = true;
					var message = "Submit scores to Fribabotti? ";
        			var dialog = new WatchUi.Confirmation(message);
					// Push the view onto the screen along with its dedicated delegate
					WatchUi.pushView(
						dialog, 
						new ConfirmSubmitScoresDelegate(throwTracker.getCourseStateArray()), 
						WatchUi.SLIDE_IMMEDIATE
					);
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
				if(_endGameDialogOpen){
					System.println("User selected NO");
					_endGameDialogOpen = false;
					// Handle the cancellation here
					var view = new selectSessionView();
        			WatchUi.switchToView(view, new sessionSelectDelegate(view), WatchUi.SLIDE_UP);
				}else{
					var loc = _view.getGpsLocation();
					throwTracker.addThrow(loc);
					WatchUi.requestUpdate();
					vibrate(ADD_THROW);
				}
			}
		}else{
			// calling while progress is active
			_holdStartTimer.stop();
			holdProgress.endProgress();
		}
		return true;
	}

	function onHoldStartTimerEnd() as Void{
		var hold_msg = _holdKey == KEY_ESC ? "Hold to delete throw..." : "Going to previous hole...";
		
		
		holdProgress.startProgress(method(:onHoldActionComplete), hold_msg);
	}

	function onHoldActionComplete() as Void {
		_had_hold_progress = true;
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
		if(!sharedData.getUseVibrations()){ return; }
		if (Attention has :vibrate) {
			// 3. Trigger the vibration
			Attention.vibrate(vibeData[pattern]);
		}
	}
}