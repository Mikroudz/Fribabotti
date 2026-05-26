import Toybox.Lang;
import Toybox.WatchUi;

class sessionSelectDelegate extends WatchUi.BehaviorDelegate {
    var _view;

    function initialize(view) {
        BehaviorDelegate.initialize();
        _view = view;
    }




    function onKeyReleased(keyEvent as KeyEvent) as Boolean {
        if(keyEvent.getKey() == KEY_ENTER){
            _view.onSelectListItem();
            return true;
        }
        return false;
    }

    function onTap(clickEvent as ClickEvent) as Boolean {
        if(clickEvent.getType() == CLICK_TYPE_TAP){
            _view.onSelectListItem();
            return true;
        }

        return false;
    }

    function onBack() as Boolean {
        // exit with back
        System.exit();
        return true;
    }

    function onNextPage() as Boolean {
        _view.listGoDown();

        return true;
    }

    function onPreviousPage() as Boolean {
        _view.listGoUp();
        return true;
    }

}