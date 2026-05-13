import {
    Box,
    Button,
    ClickAwayListener,
    IconButton,
    MenuItem,
    Select,
    styled,
    Typography,
} from "@mui/material";
import {
    MapContainer,
    TileLayer,
    useMap,
    Marker,
    Popup,
    Polyline,
    LayersControl,
} from "react-leaflet";
import "leaflet/dist/leaflet.css";
import "./mapview.css";
import { useEffect, useMemo, useRef, useState } from "react";
import L from "leaflet";
import NavigateNextIcon from "@mui/icons-material/NavigateNext";
import DeleteIcon from "@mui/icons-material/Delete";
import RoomIcon from "@mui/icons-material/Room";
import { getShortDistance } from "#/utils/helpers";
import { getPositionAsync } from "#/hooks/usePosition";

const createNumberedIcon = (number, selected) => {
    return L.divIcon({
        className: `custom-number-icon ${selected ? "selected" : ""}`,
        html: `<span>${number}</span>`,
        iconSize: [24, 38],
        iconAnchor: [0, 38],
    });
};

function RecenterMap({ markers }) {
    const map = useMap();

    useEffect(() => {
        if (markers.length > 0) {
            const bounds = L.latLngBounds(markers);
            map.fitBounds(bounds, { padding: [50, 50] });
        }
    }, [markers, map]);

    return null;
}

const StyledContentBox = styled(Box)(({ theme }) => ({
    border: "2px solid",
    borderColor: theme.palette.divider,
    borderRadius: "5px",
    backgroundColor: theme.palette.background.paper,
    padding: theme.spacing(1),
}));

function SelectHole() {
    const [hole, setHole] = useState(1);
    const [selectOpen, setSelectOpen] = useState(false);

    const data = [
        { track_number: 1, par: 3, throws: [1, 3, 5] },
        { track_number: 2, par: 3, throws: [1, 3, 5] },
        { track_number: 3, par: 3, throws: [1, 3, 5] },
        { track_number: 4, par: 3, throws: [1, 3, 5] },
        { track_number: 5, par: 3, throws: [1, 3, 5] },
        { track_number: 6, par: 3, throws: [1, 3, 5] },
        { track_number: 7, par: 3, throws: [1, 3, 5] },
        { track_number: 8, par: 3, throws: [1, 3, 5] },
        { track_number: 9, par: 3, throws: [1, 3, 5] },
        { track_number: 10, par: 3, throws: [1, 3, 5] },
        { track_number: 11, par: 3, throws: [1, 3, 5] },
    ];

    const handleClose = () => {
        console.log("closing");
        setSelectOpen(false);
    };
    const handleOpen = () => {
        console.log("opening");
        setSelectOpen(true);
    };

    const handleBoxClick = (e) => {
        // e.currentTarget is the StyledContentBox.
        // e.target is what the user actually clicked.
        // If the click came from the React Portal (the dropdown menu or backdrop),
        // it will NOT be a physical DOM child of the StyledContentBox.
        if (!e.currentTarget.contains(e.target)) {
            return; // It's a portal event, ignore it!
        }

        setSelectOpen(true);
    };
    return (
        <StyledContentBox
            onClick={handleBoxClick}
            sx={{
                position: "absolute",
                bottom: 0,
                left: 0,
                zIndex: 1000,
                ml: 1,
                mb: 8,
                pr: 1.5,
                pl: 1.5,
            }}
        >
            <Box>
                <Select
                    variant="standard"
                    value={hole}
                    open={selectOpen}
                    onOpen={handleOpen}
                    onClose={handleClose}
                    onChange={(e) => setHole(e.target.value)}
                    renderValue={(val) => (
                        <Typography sx={{ color: "text.secondary" }}>{`Hole ${val}`}</Typography>
                    )}
                    sx={{
                        "& .MuiSelect-icon": {
                            color: "text.secondary",
                        },
                    }}
                    MenuProps={{
                        anchorOrigin: {
                            vertical: "bottom",
                            horizontal: "right",
                        },
                        transformOrigin: {
                            vertical: "top",
                            horizontal: "left",
                        },
                    }}
                >
                    {data.map((val) => (
                        <MenuItem
                            key={val.track_number}
                            value={val.track_number}
                        >{`Hole ${val.track_number}`}</MenuItem>
                    ))}
                </Select>

                <Typography variant="h6">Par 3</Typography>
            </Box>
        </StyledContentBox>
    );
}

function ThrowInfo({ currentThrow }) {
    const distance =
        currentThrow?.start_pos && currentThrow?.end_pos
            ? getShortDistance(
                  currentThrow?.start_pos.latitude,
                  currentThrow?.start_pos.longitude,
                  currentThrow?.end_pos.latitude,
                  currentThrow?.end_pos.longitude,
              )
            : 0;

    return (
        <StyledContentBox
            sx={{ position: "absolute", top: 0, right: 0, zIndex: 1000, mr: 1, mt: 1 }}
        >
            <Typography component="span">Throw {currentThrow?.throw_number}</Typography>
            <Box sx={{ display: "flex", flexDirection: "column" }}>
                <Typography component="span" color="secondary" sx={{ fontSize: "13px" }}>
                    DISTANCE
                </Typography>
                <Box>
                    <Typography component="span" variant="h4">
                        {distance ? distance : "-"}
                    </Typography>
                    <Typography component="span">M</Typography>
                </Box>
            </Box>
        </StyledContentBox>
    );
}

function GameControls({ throws, currentThrow }) {
    const handleNewThrow = () => {
        // TODO: prompt user to allow location if we dont get it
        getPositionAsync({ enableHighAccuracy: true }).then((data) => console.log(data));
    };
    return (
        <>
            <ThrowInfo currentThrow={currentThrow} />
            <SelectHole />
            <Box
                sx={{
                    width: "100%",
                    position: "absolute",
                    bottom: 0,
                    left: 0,
                    zIndex: 1000,
                    p: 1,
                    display: "flex",
                    flexDirection: "row",
                    gap: 1,
                    height: "64px",
                }}
            >
                <Button
                    variant="contained"
                    sx={{
                        bgcolor: "secondary.main",
                        pr: 0.5,
                        pl: 0.5,
                        minWidth: "48px",
                    }}
                >
                    <DeleteIcon />
                </Button>

                <Button
                    sx={{
                        bgcolor: "secondary.main",
                        width: "100%",
                        fontSize: "16px",
                    }}
                    variant="contained"
                    onClick={handleNewThrow}
                >
                    Record throw
                </Button>
                <Button
                    variant="contained"
                    sx={{
                        bgcolor: "secondary.main",
                        pr: 0.5,
                        pl: 1.5,
                        minWidth: "64px",
                    }}
                >
                    Next
                    <NavigateNextIcon />
                </Button>
            </Box>
        </>
    );
}

const data = {
    throws: [
        {
            start_pos: { latitude: 65.044602, longitude: 25.428256 },
            end_pos: { latitude: 65.046602, longitude: 25.429256 },
            throw_number: 1,
        },
        {
            start_pos: { latitude: 65.046602, longitude: 25.429256 },
            end_pos: { latitude: 65.044602, longitude: 25.426256 },
            throw_number: 2,
        },
    ],
};

function ThrowMarker({ thrownum, position, onClick, isSelected, isMoving, onDragEnd }) {
    const markerRef = useRef(null);
    const [dragPosition, setDragPosition] = useState(position);

    const eventHandlers = useMemo(
        () => ({
            dragend() {
                const marker = markerRef.current;
                if (marker != null) {
                    // do we need this is parent updates position?
                    setDragPosition(marker.getLatLng());
                    onDragEnd(marker.getLatLng(), thrownum);
                }
            },
            click: (e) => {
                onClick(thrownum);
            },
        }),
        [thrownum],
    );

    return (
        <Marker
            ref={markerRef}
            position={dragPosition}
            icon={createNumberedIcon(thrownum, isSelected)}
            eventHandlers={eventHandlers}
            draggable={isMoving}
        ></Marker>
    );
}

export function MapView() {
    const [selectedThrowNum, setSelectedThrowNum] = useState(1);
    const [isMoving, setMoving] = useState(false);

    // temporary hold in state
    const [throwData, setThrowData] = useState(data);

    const markerCoords = useMemo(
        () =>
            throwData.throws.reduce((acc, val, idx) => {
                if (idx === 0) {
                    acc.push([val.start_pos.latitude, val.start_pos.longitude]);
                }
                acc.push([val.end_pos.latitude, val.end_pos.longitude]);
                return acc;
            }, []),
        [throwData],
    );

    const handleEndMoving = () => {
        // todo: send new positions to backend
    };

    const handleDragEnd = (position, thrownum) => {
        // todo: handle thrownum somehow differently? just use indexes??
        const throwIdx = thrownum - 1;
        const pos = { latitude: position.lat, longitude: position.lng };
        if (throwIdx === 0) {
            // if starting pos moved only
            setThrowData((prev) => {
                const [first, ...rest] = prev.throws;
                return {
                    ...prev,
                    throws: [
                        {
                            ...first,
                            start_pos: pos,
                        },
                        ...rest,
                    ],
                };
            });
        } else if (throwData.throws.length <= throwIdx) {
            // if on last item
            setThrowData((prev) => {
                const last = prev.throws.at(-1);

                return {
                    ...prev,
                    throws: [...prev.throws.slice(0, -1), { ...last, end_pos: pos }],
                };
            });
        } else {
            // all other cases we need to move end and start position of adjacent items
            setThrowData((prev) => {
                const newThrows = prev.throws;
                newThrows[throwIdx - 1].end_pos = pos;
                newThrows[throwIdx].start_pos = pos;
                return {
                    ...prev,
                    throws: newThrows,
                };
            });
        }
    };

    const throwMarkers = useMemo(() => {
        return (
            <>
                {markerCoords.map((val, idx) => (
                    <ThrowMarker
                        key={idx}
                        position={val}
                        thrownum={idx + 1}
                        onClick={(num) => setSelectedThrowNum(num)}
                        isSelected={idx + 1 === selectedThrowNum}
                        isMoving={idx + 1 === selectedThrowNum && isMoving}
                        onDragEnd={handleDragEnd}
                    />
                ))}
                <Polyline
                    positions={markerCoords}
                    pathOptions={{ color: "red", dashArray: "10, 10", dashOffset: "0" }}
                />
            </>
        );
    }, [markerCoords, selectedThrowNum, isMoving]);

    return (
        <Box sx={{ height: "100%", width: "100%", overflow: "hidden", position: "relative" }}>
            <MapContainer
                zoom={19}
                scrollWheelZoom={false}
                style={{ height: "100%", width: "100%" }}
            >
                <LayersControl position="bottomright">
                    <LayersControl.BaseLayer checked name="OpenStreetMap">
                        <TileLayer
                            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        />
                    </LayersControl.BaseLayer>
                    <LayersControl.BaseLayer name="Satellite">
                        <TileLayer
                            url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                            attribution="Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EBP, and the GIS User Community"
                        />
                    </LayersControl.BaseLayer>
                </LayersControl>

                {throwMarkers}
                <RecenterMap markers={markerCoords} />
            </MapContainer>
            <GameControls currentThrow={data.throws[selectedThrowNum - 1]} />
            <Button
                sx={{
                    fontSize: "16px",
                    position: "absolute",
                    top: 0,
                    right: 0,
                    mt: 14,
                    mr: 1,
                    zIndex: 1000,
                }}
                variant="contained"
                startIcon={<RoomIcon />}
                onClick={() => setMoving((prev) => !prev)}
            >
                {isMoving ? "Moving!" : "Move"}
            </Button>
        </Box>
    );
}
