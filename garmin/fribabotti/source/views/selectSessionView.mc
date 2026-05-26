import Toybox.Graphics;
import Toybox.WatchUi;
import Toybox.Lang;

class selectSessionView extends WatchUi.View {
    private var sessionSelect as SelectSessionDrawable?;
    private var _sessions_fetcher;

    function initialize() {
        View.initialize();
    }

    // Load your resources here
    function onLayout(dc as Dc) as Void {
        setLayout(Rez.Layouts.SessionSelectLayout(dc));
        sessionSelect = findDrawableById("SessionSelect");
        _sessions_fetcher = new LoadGameSessions(method(:onSessionsFetchComplete));
        // try loading data
        _sessions_fetcher.makeRequest();
    }

    function onSessionsFetchComplete(data as Dictionary?) as Void{
        sessionSelect.setSelectables(data);
        WatchUi.requestUpdate();
    }


    public function listGoDown() as Void{
        sessionSelect.goDown();
        WatchUi.requestUpdate();
    }

    public function listGoUp() as Void{
        sessionSelect.goUp();
        WatchUi.requestUpdate();
    }

    public function onSelectListItem(){
        var session_id = sessionSelect.getCurrentItem();
        if(session_id.equals("refresh")){
            updateList();
        } else if (session_id.equals("settings")) {
            var menu = new WatchUi.Menu2({:title=>"Settings"});
            menu.addItem(new WatchUi.ToggleMenuItem("Vibrations", "Enable vibrations", "vibrations", sharedData.getUseVibrations(), null));
            menu.addItem(new WatchUi.ToggleMenuItem("Use GPS for throws", "Increases battery usage", "enable_gps", sharedData.getEnableGps(), null));
            menu.addItem(new WatchUi.ToggleMenuItem("Register device to bot", "Enable to start registeration process", "register_device", false, null));
            
            
            WatchUi.pushView(menu, new SettingsMenuDelegate(menu), WatchUi.SLIDE_UP);
        } else {
            sharedData.setCurrentSessionId(session_id);
            // start fetching session and show progress bar
            gamesession_fetcher.makeRequest(session_id, method(:onSessionLoaded));

            var progressBar = new ProgressBar("Loading game...", null);
            WatchUi.pushView(progressBar, null, SLIDE_DOWN);
        }
    }

    public function updateList() as Void {
        if(_sessions_fetcher.state != STATE_PENDING){
            _sessions_fetcher.makeRequest();
        }
    }

    function onSessionLoaded(data as Dictionary?){
        if(data.hasKey("holes")){
            sharedData.setCurrentCourse(data["holes"]);
        }
        var view = new throwView();
        WatchUi.pushView(view, new throwDelegate(view), WatchUi.SLIDE_UP);
    }


    // Called when this View is brought to the foreground. Restore
    // the state of this View and prepare it to be shown. This includes
    // loading resources into memory.
    function onShow() as Void {
    }

    // Update the view
    function onUpdate(dc as Dc) as Void {
        // Call the parent onUpdate function to redraw the layout
        View.onUpdate(dc);
    }

    // Called when this View is removed from the screen. Save the
    // state of this View here. This includes freeing resources from
    // memory.
    function onHide() as Void {
    }

}
