import { useEffect, useState } from "react";

const defaultSettings = {
    enableHighAccuracy: false,
    timeout: Infinity,
    maximumAge: 0,
    targetAccuracy: 20, // in meters
};

export const usePosition = (userSettings = {}) => {
    const settings = {
        ...defaultSettings,
        ...userSettings,
    };

    const [position, setPosition] = useState({});
    const [error, setError] = useState(null);

    const onChange = ({ coords, timestamp }) => {
        setPosition({
            latitude: coords.latitude,
            longitude: coords.longitude,
            accuracy: coords.accuracy,
            speed: coords.speed,
            heading: coords.heading,
            timestamp,
        });
    };

    const onError = (error) => {
        setError(error.message);
    };

    useEffect(() => {
        if (!navigator || !navigator.geolocation) {
            setError("Geolocation is not supported");
            return;
        }
        navigator.geolocation.getCurrentPosition(onChange, onError, settings);
    }, [settings.enableHighAccuracy, settings.timeout, settings.maximumAge]);

    return { ...position, error };
};

export const getPositionAsync = async (userSettings = {}) => {
    if (!navigator || !navigator.geolocation) {
        console.log("no geolocation");
        return null;
    }
    const settings = {
        ...defaultSettings,
        ...userSettings,
    };
    try {
        const permission = await navigator.permissions.query({ name: "geolocation" });
        console.log(permission);
        if (permission.state !== "granted") {
            return null;
        }
    } catch (e) {
        console.error(e);
        return null;
    }

    return new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject, settings);
    });
};

let watchId;
let callback;
let startTime;

export const getPositionWithCallback = async (cb, userSettings = {}) => {
    if (!navigator || !navigator.geolocation) {
        console.log("no geolocation");
        return null;
    }
    const settings = {
        ...defaultSettings,
        ...userSettings,
    };
    try {
        const permission = await navigator.permissions.query({ name: "geolocation" });
        console.log(permission);
        if (permission.state !== "granted") {
            return null;
        }
    } catch (e) {
        console.error(e);
        return null;
    }
    callback = cb;
    startTime = Date.now();
    const checkAccuracy = (pos) => {
        const currentAccuracy = pos.coords.accuracy;
        if (
            currentAccuracy <= settings.targetAccuracy ||
            Date.now() - startTime >= settings.timeout * 1000
        ) {
            console.log("High accuracy location achieved:", pos.coords);
            navigator.geolocation.clearWatch(watchId);
            callback(pos);
        }
    };
    const fail = () => {};

    watchId = navigator.geolocation.watchPosition(checkAccuracy, fail, settings);
};

export const stopPositionWatch = () => {
    if (watchId !== undefined) {
        navigator.geolocation.clearWatch(watchId);
    }
};
