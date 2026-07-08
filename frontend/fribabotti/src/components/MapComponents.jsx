import { Box, IconButton } from "@mui/material";
import { MapContainer, TileLayer, useMap, Marker, LayersControl } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import "./mapview.css";
import { useEffect, useRef, useState } from "react";
import L from "leaflet";

import { stopPositionWatch } from "#/hooks/usePosition";

import MyLocationIcon from "@mui/icons-material/MyLocation";

export function RecenterMap({ markers }) {
    const map = useMap();
    const currentBounds = useRef(null);

    useEffect(() => {
        if (markers && markers.length > 0) {
            map.invalidateSize();
            currentBounds.current = L.latLngBounds(markers);
            map.fitBounds(currentBounds.current, { padding: [50, 50] });
            // ensure bounds. this is not good solution but fixes map not centering in producrtion
            const timer = setTimeout(() => {
                if (!map.getBounds().contains(markers[0])) {
                    map.fitBounds(currentBounds.current, { padding: [50, 50] });
                }
            }, 500);
            return () => clearTimeout(timer);
        }
    }, [markers, map]);

    return null;
}

const createMeIcon = () => {
    return L.divIcon({
        className: `custom-me-icon`,
        iconSize: [20, 20],
        iconAnchor: [10, 10],
    });
};

function LocateSelfButton() {
    const map = useMap();
    const [position, setPosition] = useState(null);

    useEffect(() => {
        map.on("locationfound", (e) => {
            setPosition(e.latlng);
            map.setView(e.latlng, 16);
        });

        map.on("locationerror", (e) => {
            alert(`Geolocation error: ${e.message}`);
        });
    }, [map]);

    const handleLocate = () => {
        map.locate({ setView: false, maxZoom: 16 });
    };

    useEffect(() => {
        return stopPositionWatch;
    }, []);

    return (
        <>
            {/* Custom Button Placed in a Leaflet Control Container Slot */}
            <Box className="leaflet-right" sx={{ pointerEvents: "auto", bottom: 160, position: "absolute" }}>
                <Box className="leaflet-control leaflet-bar">
                    <IconButton
                        onClick={handleLocate}
                        sx={{
                            backgroundColor: "background.paper",
                            borderRadius: "4px",

                            width: "44px",
                            height: "44px",
                            lineHeight: "44px",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            border: "none",
                            cursor: "pointer",
                            fontSize: "18px",
                        }}
                    >
                        <MyLocationIcon sx={{ color: "text.primary" }} />
                    </IconButton>
                </Box>
            </Box>

            {/* Render a marker at the user's location once it is found */}
            {position && <Marker position={position} icon={createMeIcon()}></Marker>}
        </>
    );
}

export function Map({ children }) {
    return (
        <MapContainer
            zoom={19}
            scrollWheelZoom={false}
            center={[62.290715, 25.007085]}
            style={{ height: "100%", width: "100%", position: "relative" }}
        >
            <LayersControl position="bottomright">
                <LayersControl.BaseLayer checked name="OpenStreetMap">
                    <TileLayer
                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        referrerPolicy={"strict-origin-when-cross-origin"}
                    />
                </LayersControl.BaseLayer>
                <LayersControl.BaseLayer name="Satellite">
                    <TileLayer
                        url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                        attribution="Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EBP, and the GIS User Community"
                    />
                </LayersControl.BaseLayer>
            </LayersControl>
            <LocateSelfButton />
            {children}
        </MapContainer>
    );
}
