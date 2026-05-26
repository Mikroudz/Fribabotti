
import Toybox.Lang;
using Toybox.Position;



class ThrowData  {
	var par as Number = 0;
	var throws as Array<Float> = [];
	// throw locations where 0 is tee, so 1 is end of 1st throw and start of 2nd throw etc.
	// we COULD store this as dictionary in throws but
	var _throw_locations as Array<Position.Location or Null> = [];



	function initialize(p_par, p_throws){
		par = p_par;
		if(p_throws instanceof Array){
			throws = p_throws;
		}
	}

	const DEG_TO_RAD = Math.PI / 180.0;

	function deg2rad(degrees) {
		return degrees * DEG_TO_RAD;
	}

	function getThrowdistance(loc1, loc2) as Float {
		if(loc2 != null and loc1 != null){
			var x = deg2rad(loc2[1] - loc1[1]) * Math.cos(deg2rad((loc1[0] + loc2[0]) / 2));
			var y = deg2rad(loc2[0] - loc1[0]);
			return Math.sqrt(x * x + y * y) * 6371000; // Result in meters
		} else {
			return 0.1;
		}
	}

	function throwHasStarted() as Boolean {
		return throws.size() >= 1;
	}

	function getThrowCount() as Number {
		return (throws.size() >= 1 && throws[0] != 0.0 ) ? throws.size() : 0;
	}

	function getThrowsOverPar() as Number {
		return getThrowCount() - par;
	}

	function getPar() as Number {
		if(par instanceof Number){
			return par;
		}
		return 0;
	}

	function addThrow(location as Position.Location or Null){
		if(throws.size() == 0){
			throws.add(0.0);
			// starting location
			_throw_locations.add(location);
		}else if(throws.size() == 1 && throws[0] == 0.0 && _throw_locations.size() > 0){
			// edit 1st throw
			throws[0] = getThrowdistance(_throw_locations[0], location);
			// save end position
			_throw_locations.add(location);
		} else {
			// Note: if we dont have locations (data is loaded from existing session with scores on server)
			// we cannot calculate distance
			// there should be one more location than throw
			var throw_distance = 0.0;
			if(throws.size() < _throw_locations.size()){
				throw_distance = getThrowdistance(_throw_locations[_throw_locations.size() - 1], location);
			}

			throws.add(throw_distance);
			_throw_locations.add(location);
		}
	}

	function removeThrow() as Boolean{
		if(throws.size() == 1 && throws[0] != 0.0){
			// IF we have one landing (one throw (distance) and two locations, zero first throw and remove one location)
			throws[0] = 0.0;
			_throw_locations = _throw_locations.slice(0, _throw_locations.size() - 1);
			return true;
		}else if(throws.size() > 0){
			// if we are on first throw, set in to 0.
			throws = throws.slice(0, throws.size() - 1);
			_throw_locations = _throw_locations.slice(0, _throw_locations.size() - 1);
			return true;
		}
		return false;
	}
}
