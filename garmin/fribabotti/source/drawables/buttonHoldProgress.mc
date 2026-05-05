import Toybox.WatchUi;
using Toybox.StringUtil;
import Toybox.Lang;
import Toybox.Graphics;
using Toybox.Timer;

class ButtonHoldProgressDrawable extends WatchUi.Drawable {

	var _isProgressing as Boolean = false;
	var _progressLevel as Number = 0;
	var _timer;
	var _progressEndCallback;
	var _msg;

    public function initialize(params as Dictionary) {
        // You should always call the parent's initializer and
        // in this case you should pass the params along as size
        // and location values may be defined.
        Drawable.initialize(params);
		_timer = new Timer.Timer();
    }

	public function startProgress(progressEndCallback, msg as String){
		_isProgressing = true;
		_msg = msg;
		_progressLevel = 0;
		_progressEndCallback = progressEndCallback;
		_timer.start(method(:onTimerUpdate), 500, true);
		// start timer
	}

	public function endProgress(){
		_isProgressing = false;
		// stop timer
		_timer.stop();
	}

	function onTimerUpdate(){
		if(_progressLevel > 2){
			// call callback
			_timer.stop();
			_progressEndCallback.invoke();
			_isProgressing = false;
			return; // return here; some other place will update UI
		}
		_progressLevel += 1;
		WatchUi.requestUpdate();
	}

	function onHide() {
        _timer.stop();
    }

	function draw(dc as Dc) as Void {
		if(_isProgressing){
			dc.setColor(Graphics.COLOR_BLACK, Graphics.COLOR_TRANSPARENT);
			dc.fillRectangle(0, dc.getHeight() * 0.4, 300, 100);

			dc.setColor(Graphics.COLOR_DK_RED, Graphics.COLOR_TRANSPARENT);
			if(_progressLevel > 0){
				dc.fillRectangle(dc.getWidth() * 0.5 - 80, dc.getHeight() * 0.6, 50, 3);
			}
			if(_progressLevel > 1){
				dc.fillRectangle(dc.getWidth() * 0.5 - 25, dc.getHeight() * 0.6, 50, 3);
			}
			if(_progressLevel > 2){
				dc.fillRectangle(dc.getWidth() * 0.5 + 30, dc.getHeight() * 0.6, 50, 3);
			}
			dc.drawText(
				dc.getWidth() * 0.5, 
				(dc.getHeight() * 0.45), 
				Graphics.FONT_TINY,
				_msg,
				Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER
			);
		}
    }
}