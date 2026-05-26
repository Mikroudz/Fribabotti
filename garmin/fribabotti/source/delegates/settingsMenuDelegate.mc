import Toybox.WatchUi;
import Toybox.System;
import Toybox.Lang;


class SettingsMenuDelegate extends WatchUi.Menu2InputDelegate {

	private var _registeration_num;
	private var _registeration_timer;
	private var _register_query;
	private var _menu;

    function initialize(menu) {
        Menu2InputDelegate.initialize();
		_menu = menu;
    }

    function onSelect(item) {
        // Use the item's ID to determine which action to take
        if (item.getId().equals("vibrations")) {
            System.println("Selected Item 1");
			if (item instanceof WatchUi.ToggleMenuItem) {
				sharedData.setUseVibrations(item.isEnabled());
			}
        } else if (item.getId().equals("register_device")) {
			if (item instanceof WatchUi.ToggleMenuItem) {
				if (item.isEnabled()){
					_registeration_num = (Math.rand() % (99999 - 10000 + 1)) + 1;
					item.setLabel("Registeration code: " + _registeration_num);
					item.setSubLabel("Input code to bot");
					_register_query = new RegisterDeviceSession(method(:onRegisterQueryDone));

					_registeration_timer = new Timer.Timer();
					_registeration_timer.start(method(:onRegisterCheckTimerEnd), 5000, true);
				} else {
					stopDeviceRegisteration();
					item.setLabel("Enable to start registeration process");
					item.setSubLabel("");
				}
			}
		} else if (item.getId().equals("enable_gps")){
			if (item instanceof WatchUi.ToggleMenuItem) {
				sharedData.setEnableGps(item.isEnabled());
			}
		}
    }

    function onBack() {
		// ensure timer is stopped 
		stopDeviceRegisteration();
        WatchUi.popView(WatchUi.SLIDE_DOWN);
    }

	function onRegisterCheckTimerEnd() as Void {
		if(_register_query instanceof RegisterDeviceSession){
			if(_register_query.state != STATE_PENDING){
				_register_query.makeRequest(_registeration_num);
			}
		}
	}

	function onRegisterQueryDone(data as Dictionary?){
		if(data == null){
			// error case
			_register_query.makeRequest(_registeration_num);
		} else if (data.hasKey("key") && data["key"] != ""){
			System.println("Registeration successfull");
			System.println("key: " + data["key"] + " username: " + data["username"]);
			stopDeviceRegisteration();
			sharedData.setAuthToken(data["key"]);
			var menuIdx = _menu.findItemById("register_device");
			if(menuIdx != -1){
				var menuItem = _menu.getItem(menuIdx);
				menuItem.setLabel("Registered to user " + data["username"]);
				menuItem.setSubLabel("");
				WatchUi.requestUpdate();
			}
		}
	}

	function stopDeviceRegisteration(){
		if(_registeration_timer instanceof Timer.Timer){
			_registeration_timer.stop();
		}
	}
}