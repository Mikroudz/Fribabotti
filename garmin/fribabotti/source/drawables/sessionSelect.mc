import Toybox.WatchUi;
using Toybox.StringUtil;
import Toybox.Lang;
import Toybox.Graphics;

class SelectSessionDrawable extends WatchUi.Drawable {

	var _selectables = [];
	var _currentlySelectedItemIdx = 0;

    public function initialize(params as Dictionary) {
        // You should always call the parent's initializer and
        // in this case you should pass the params along as size
        // and location values may be defined.
        Drawable.initialize(params);
		setSelectables([]);
    }
	function setSelectables(data as Array<Dictionary>){
		_selectables = data;
		_selectables.add({"id" => "refresh", "name" => "Refresh"});
	}

	function goUp(){
		if(_currentlySelectedItemIdx < 1){
			return;
		}
		_currentlySelectedItemIdx--;
	}

	function goDown(){
		if(_currentlySelectedItemIdx >= _selectables.size() - 1){
			return;
		}
		_currentlySelectedItemIdx++;
	}

	function getCurrentItem() as String {
		return _selectables[_currentlySelectedItemIdx]["id"];
	}



	function draw(dc as Dc) as Void {
		dc.setColor(Graphics.COLOR_BLUE, Graphics.COLOR_TRANSPARENT);
		dc.fillRectangle(0, 35 + 35 * _currentlySelectedItemIdx, 300, 30);

		var textPosH = 50;
		dc.setColor(Graphics.COLOR_WHITE, Graphics.COLOR_TRANSPARENT);
		for(var i = 0; i < _selectables.size(); i++){
			dc.drawText(dc.getWidth() * 0.5, textPosH, Graphics.FONT_XTINY, _selectables[i]["name"], Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER);
			textPosH += 35;
		}
    }
}