import Toybox.Graphics;
import Toybox.WatchUi;
using Toybox.Position;

class throwView extends WatchUi.View {

    var _has_gps_fix = false;
    var _last_location;

    function initialize() {
        View.initialize();
    }

    // Load your resources here
    function onLayout(dc as Dc) as Void {
        setLayout(Rez.Layouts.ThrowLayout(dc));
        var trackTracker = View.findDrawableById("TrackTracker") as TracKTrackerDrawable;
		var throwTracker = View.findDrawableById("ThrowTracker") as ThrowTrackerDrawable;
		var courseData = sharedData.getCurrentCourse();
		throwTracker.initializeCourse(courseData);
		var holes = [];
		for(var i = 0; i < courseData.size(); i++){
			holes.add(i+1);
		}
		trackTracker.setHoles(holes);
        // we have to use continuous gps so we get good accuracy and no time delay
        startGps();
    }

    function updateClock(){
        var clockTime = System.getClockTime();
        var timeString = Lang.format("$1$:$2$", [clockTime.hour, clockTime.min.format("%02d")]);
        var view = View.findDrawableById("TimeLabel") as Text or Null;
        if(view != null){
            view.setText(timeString);
        }
    }

    function getGpsLocation() as Position.Location or Null {
        if(_has_gps_fix){
            return _last_location;
        } else {
            return null;
        }
    }

    function startGps(){
        var options = {
            :acquisitionType => Position.LOCATION_CONTINUOUS
        };

        System.println("GPS is STARTED");

        if (Position has :hasConfigurationSupport) {
            if (Position has :CONFIGURATION_GPS_GLONASS_GALILEO_BEIDOU_L1_L5 and Position.hasConfigurationSupport(Position.CONFIGURATION_GPS_GLONASS_GALILEO_BEIDOU_L1_L5)) {
                options[:configuration] = Position.CONFIGURATION_GPS_GLONASS_GALILEO_BEIDOU_L1_L5;
            } else if (Position has :CONFIGURATION_GPS_GLONASS_GALILEO_BEIDOU_L1 and Position.hasConfigurationSupport(Position.CONFIGURATION_GPS_GLONASS_GALILEO_BEIDOU_L1)) {
                options[:configuration] = Position.CONFIGURATION_GPS_GLONASS_GALILEO_BEIDOU_L1;
            } else if (Position has :CONFIGURATION_GPS and Position.hasConfigurationSupport(Position.CONFIGURATION_GPS)) {
                options[:configuration] = Position.CONFIGURATION_GPS;
            }
        } else {
            options = Position.LOCATION_CONTINUOUS;
        }

        Position.enableLocationEvents(options, method(:onPosition));
    }

    function stopGps(){
        System.println("GPS is STOPPED");
        Position.enableLocationEvents(Position.LOCATION_DISABLE, method(:onPosition));
    }

    function onPosition(info as Position.Info) as Void {
        if (info.accuracy >= Position.QUALITY_POOR) {
            _last_location = info.position.toDegrees();
            //System.println("Lat: " + _last_location[0] + ", Lon: " + _last_location[1]);
            _has_gps_fix = true;
        }else{
            _has_gps_fix = false;
        }
    }

    // Called when this View is brought to the foreground. Restore
    // the state of this View and prepare it to be shown. This includes
    // loading resources into memory.
    function onShow() as Void {
    }


    // Update the view
    function onUpdate(dc as Dc) as Void {
        // Call the parent onUpdate function to redraw the layout'
        updateClock();
        View.onUpdate(dc);
    }

    // Called when this View is removed from the screen. Save the
    // state of this View here. This includes freeing resources from
    // memory.
    function onHide() as Void {
        stopGps();
    }

}
