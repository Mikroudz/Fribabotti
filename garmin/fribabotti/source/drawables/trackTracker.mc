import Toybox.WatchUi;
using Toybox.StringUtil;
import Toybox.Lang;
import Toybox.Graphics;

class TracKTrackerDrawable extends WatchUi.Drawable {

	private var _holes = [];
	private var _current_hole_index = 0;

    public function initialize(params as Dictionary) {
        Drawable.initialize(params);
    }

	public function setHoles(holes as Array<Number>) as Void {
		_holes = holes;
	}
	public function setCurrentHole(hole as Number) as Void {
		_current_hole_index = hole;
	}

	public function getHoleIndex() as Number{
		return _current_hole_index;
	}

	public function isLastHole() as Boolean {
		return _current_hole_index + 1 >= _holes.size();
	}

	public function moveNextHole() as Number {
		if(_current_hole_index < _holes.size()-1){
			_current_hole_index += 1;
		}
		return _current_hole_index;
	}

	public function movePrevHole() as Number {
		if(_current_hole_index > 0){
			_current_hole_index -= 1;
		}
		return _current_hole_index;
	}

	function drawNumber(dc as Dc, offset as Number, num as Number){
		dc.drawText(dc.getWidth() * 0.5 + offset, 30, Graphics.FONT_MEDIUM , num.toString(), Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER);
	}

	function draw(dc as Dc) as Void {
		// add square to current hole in center
		dc.setColor(Graphics.COLOR_BLUE, Graphics.COLOR_TRANSPARENT);
		dc.fillRectangle(dc.getWidth() * 0.5 - 9, 20, 18, 24);

		// draw numbers
		var start = _current_hole_index < 2 ? 0 : _current_hole_index - 2;
		var end = _holes.size() - 3 > _current_hole_index ? _current_hole_index + 3 : _holes.size();
		

		dc.setColor(Graphics.COLOR_WHITE, Graphics.COLOR_TRANSPARENT);
		// current (center)
		drawNumber(dc, 0, _holes[_current_hole_index]);
		// prev
		var offs = -30;
		for(var i = _current_hole_index - 1; i >= start; i--){
			drawNumber(dc, offs, _holes[i]);
			offs-=30;
		}
		// next
		offs = 30;
		for(var i = _current_hole_index + 1; i < end; i++){
			drawNumber(dc, offs, _holes[i]);
			offs+=30;
		}
		// upper button will exit round if track is in last position so add indication
		if(_current_hole_index + 1 >= _holes.size()){
			dc.drawText(dc.getWidth() * 0.8, dc.getHeight() / 5, Graphics.FONT_MEDIUM, "Exit", Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER);
		}
    }
}