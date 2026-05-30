
import Toybox.Lang;
using Toybox.Position;



class ThrowData  {
	var par as Number = 0;
	var distances as Array<Float> = [];
	// throw locations where 0 is tee, so 1 is end of 1st throw and start of 2nd throw etc.
	// we COULD store this as dictionary in throws but
	var _throw_locations as Array<Array<Double> or Null> = [];



	function initialize(p_par, p_throws as Null or Array<Dictionary<String, Float>>){
		par = p_par;
		System.println(p_throws);
		if(p_throws instanceof Array){
			for(var i = 0; i < p_throws.size(); i++){
				var pos = null;
				if (p_throws[i] instanceof Dictionary and p_throws[i].hasKey("lat")) {
					// we could also send the array position directly from backend
					pos = [p_throws[i]["lat"], p_throws[i]["lng"]];
				}
				
				_throw_locations.add(pos);
				
				if(i > 0){
					distances.add(getThrowdistance(_throw_locations[i-1], pos));
				}
			}
		}
	}

	const DEG_TO_RAD = Math.PI / 180.0;

	function deg2rad(degrees as Float) as Float {
		return degrees * DEG_TO_RAD;
	}

	function getThrowdistance(loc1 as Position.Location or Null, loc2 as Position.Location or Null) as Float {
		if(loc2 != null and loc1 != null){
			var x = deg2rad(loc2[1] - loc1[1]) * Math.cos(deg2rad((loc1[0] + loc2[0]) / 2));
			var y = deg2rad(loc2[0] - loc1[0]);
			return Math.sqrt(x * x + y * y) * 6371000; // Result in meters
		} else {
			return 0.1;
		}
	}

	function throwHasStarted() as Boolean {
		return distances.size() >= 1;
	}

	function getThrowCount() as Number {
		return (distances.size() >= 1 && distances[0] != 0.0 ) ? distances.size() : 0;
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

	function addThrow(location as Array<Double> or Null){
		if(distances.size() == 0){
			distances.add(0.0);
			// starting location
			_throw_locations.add(location);
		}else if(distances.size() == 1 && distances[0] == 0.0 && _throw_locations.size() > 0){
			// edit 1st throw
			distances[0] = getThrowdistance(_throw_locations[0], location);
			// save end position
			_throw_locations.add(location);
		} else {
			// Note: if we dont have locations (data is loaded from existing session with scores on server)
			// we cannot calculate distance
			// there should be one more location than throw
			var throw_distance = 0.0;
			if(distances.size() < _throw_locations.size()){
				throw_distance = getThrowdistance(_throw_locations[_throw_locations.size() - 1], location);
			}

			distances.add(throw_distance);
			_throw_locations.add(location);
		}
	}

	function removeThrow() as Boolean{
		if(distances.size() == 1 && distances[0] != 0.0){
			// IF we have one landing (one throw (distance) and two locations, zero first throw and remove one location)
			distances[0] = 0.0;
			_throw_locations = _throw_locations.slice(0, _throw_locations.size() - 1);
			return true;
		}else if(distances.size() > 0){
			// if we are on first throw, set in to 0.
			distances = distances.slice(0, distances.size() - 1);
			_throw_locations = _throw_locations.slice(0, _throw_locations.size() - 1);
			return true;
		}
		return false;
	}
}
