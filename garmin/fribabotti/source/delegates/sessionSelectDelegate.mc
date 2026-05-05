import Toybox.Lang;
import Toybox.WatchUi;

class sessionSelectDelegate extends WatchUi.BehaviorDelegate {
    var _view;
    var _sessions_fetcher;

    function initialize(view) {
        BehaviorDelegate.initialize();
        _view = view;
        _sessions_fetcher = new LoadGameSessions(method(:onSessionsFetchComplete));

        // try loading data
        _sessions_fetcher.makeRequest();
    }

    function onSessionsFetchComplete(data as Dictionary?){
        var sessionSelect = _view.findDrawableById("SessionSelect");
        sessionSelect.setSelectables(data);
        WatchUi.requestUpdate();
    }

    function onSessionLoaded(data as Dictionary?){
        if(data.hasKey("holes")){
            sharedData.setCurrentCourse(data["holes"]);
        }
        var view = new throwView();
        WatchUi.pushView(view, new throwDelegate(view), WatchUi.SLIDE_UP);
    }

    function onSelect() as Boolean {
        var sessionSelect = _view.findDrawableById("SessionSelect");
        // save to global memory
        var session_id = sessionSelect.getCurrentItem();
        if(session_id.equals("refresh")){
            if(_sessions_fetcher.state != STATE_PENDING){
                _sessions_fetcher.makeRequest();
            }
        } else {
            sharedData.setCurrentSessionId(session_id);
            // start fetching session and show progress bar
            session_fetcher.makeRequest(session_id, method(:onSessionLoaded));

            var progressBar = new ProgressBar("Loading game...", null);
            WatchUi.pushView(progressBar, null, SLIDE_DOWN);
        }
        return true;
    }

    function onBack() as Boolean {
        // exit with back
        System.exit();
        return true;
    }

    function onNextPage() as Boolean {
        var sessionSelect = _view.findDrawableById("SessionSelect");
        sessionSelect.goDown();
        WatchUi.requestUpdate();

        return true;
    }

    function onPreviousPage() as Boolean {
        var sessionSelect = _view.findDrawableById("SessionSelect");
        sessionSelect.goUp();
        WatchUi.requestUpdate();
        return true;
    }

}