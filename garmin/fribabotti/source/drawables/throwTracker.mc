import Toybox.WatchUi;
using Toybox.StringUtil;
import Toybox.Lang;
import Toybox.Graphics;

class ThrowTrackerDrawable extends WatchUi.Drawable {

	//[{par: 1, throws: [20, 30, 40], }]

	private var _total = 3;
	private var _total_over_par = 0;
	private var _throws as Array<ThrowData> = [];
	// TODO: move this to somewhere else
	private var _current_hole_index = 0;

    public function initialize(params as Dictionary) {
        // You should always call the parent's initializer and
        // in this case you should pass the params along as size
        // and location values may be defined.
        Drawable.initialize(params);

        // Get any extra values you wish to use out of the params Dictionary
		//initializeCourse([{"par" => 3, "throws" => []}, {"par" => 5, "throws" => []}, {"par" => 4, "throws" => []},{"par" => 2, "throws" => []},{"par" => 4, "throws" => []},{"par" => 5, "throws" => []}]);

    }

	function initializeCourse(data as Array<Dictionary>){
		// initialize throws from course data received from backend session
		for(var i = 0; i < data.size(); i++){
			_throws.add(new ThrowData(data[i]["par"], data[i]["throws"]));
		}
	}

	function getCourseStateArray() as Array<Array<Number>> {
		var out = [];
		for(var i = 0; i < _throws.size(); i++){
			out.add(_throws[i].throws);
		}
		return out;
	}

	function setHoleIndex(hole_idx as Number) {
		_current_hole_index = hole_idx;
	}

	function addThrow(location){
		// we should always be inside the array but test still
		if(_throws.size() <= _current_hole_index) {return;}
		_throws[_current_hole_index].addThrow(location);
	}

	function removeThrow() as Boolean{
		if(_throws.size() <= _current_hole_index) {return false;}
		return _throws[_current_hole_index].removeThrow();
	}

	function calcTotal() {
		// make course dataclass to hold this?
		_total = 0;
		_total_over_par = 0;
		for(var i = 0; i < _throws.size(); i++){
			var throw_cnt = _throws[i].getThrowCount();
			_total += throw_cnt;
			if (throw_cnt > 0){
				_total_over_par += throw_cnt - _throws[i].getPar();
			}
		}
	}


	function drawNumber(dc as Dc, offset as Number, num as Number){
		dc.drawText(dc.getWidth() * 0.5 + offset, 30, Graphics.FONT_MEDIUM , num.toString(), Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER);
	}

	function draw(dc as Dc) as Void {
		calcTotal();

		// par display
		dc.setColor(Graphics.COLOR_WHITE, Graphics.COLOR_TRANSPARENT);
		dc.drawText(dc.getWidth() * 0.5 - 20, 80, Graphics.FONT_MEDIUM , "Par " + _throws[_current_hole_index].getPar().toString(), Graphics.TEXT_JUSTIFY_RIGHT | Graphics.TEXT_JUSTIFY_VCENTER);
		// throws - par
		var currentParNum = _throws[_current_hole_index].getThrowsOverPar();
		var currentPar = currentParNum > 0 ? "+" + currentParNum.toString() : currentParNum.toString();

		dc.drawText(dc.getWidth() * 0.5 - 40, 107, Graphics.FONT_MEDIUM, currentPar, Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER);


		dc.drawText(dc.getWidth() * 0.5, 80, Graphics.FONT_MEDIUM , "|", Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER);


		var totalStr = _total_over_par > 0 ? "+" + _total_over_par.toString() : _total_over_par.toString();

		dc.drawText(dc.getWidth() * 0.5 + 10, 80, Graphics.FONT_MEDIUM , "Total " + totalStr, Graphics.TEXT_JUSTIFY_LEFT | Graphics.TEXT_JUSTIFY_VCENTER);

		// throw count
		dc.drawText(dc.getWidth() * 0.5, 140, Graphics.FONT_MEDIUM , "Throws", Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER);
		

		if(_throws[_current_hole_index].throwHasStarted()){
			dc.drawText(dc.getWidth() * 0.5, 176, Graphics.FONT_NUMBER_MEDIUM , _throws[_current_hole_index].getThrowCount().toString(), Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER);

			// draw add
			dc.drawText(
				dc.getWidth() - 25, 
				(dc.getHeight() * 3) / 4, 
				Graphics.FONT_TINY, 
				"+", 
				Graphics.TEXT_JUSTIFY_RIGHT | Graphics.TEXT_JUSTIFY_VCENTER
			);
			// draw remove throws
			dc.drawText(
				25,
				(dc.getHeight() * 3) / 4,
				Graphics.FONT_TINY,
				"-",
				Graphics.TEXT_JUSTIFY_LEFT | Graphics.TEXT_JUSTIFY_VCENTER
			);

		} else {
			dc.drawText(dc.getWidth() * 0.5, 176, Graphics.FONT_XTINY, "Press at tee to start throw", Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER);
			dc.drawText(
				dc.getWidth() - 10, 
				160, 
				Graphics.FONT_TINY, 
				"Start", 
				Graphics.TEXT_JUSTIFY_RIGHT | Graphics.TEXT_JUSTIFY_VCENTER
			);
		}
		
		// throw distances
		var distString = "";
		for(var i = 0; i < _throws[_current_hole_index].throws.size(); i++){
			distString += _throws[_current_hole_index].throws[i].format("%.0f") + "M·";
		}
		dc.drawText(dc.getWidth() * 0.5, 196, Graphics.FONT_XTINY, distString, Graphics.TEXT_JUSTIFY_CENTER);
    }
}