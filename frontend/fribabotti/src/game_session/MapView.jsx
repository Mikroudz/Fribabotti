import { Box, Button, MenuItem, Select, styled, Typography } from "@mui/material";
import { Marker, Polyline, Circle, LayerGroup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { useEffect, useMemo, useRef, useState } from "react";
import L from "leaflet";
import NavigateNextIcon from "@mui/icons-material/NavigateNext";
import DeleteIcon from "@mui/icons-material/Delete";
import RoomIcon from "@mui/icons-material/Room";
import { getShortDistance } from "#/utils/helpers";
import { getPositionWithCallback } from "#/hooks/usePosition";
import { GameScoreDrawer } from "./GameScoreDrawer";
import {
    GAME_SESSION_KEY,
    useGameSession,
    useHoleChanger,
    useSelectedHole,
} from "#/hooks/GameSessionHooks";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createThrow } from "#/utils/api";
import { useParams } from "@tanstack/react-router";
import { Map, RecenterMap } from "#/components/MapComponents";

const createNumberedIcon = (number, selected) => {
    return L.divIcon({
        className: `custom-number-icon ${selected ? "selected" : ""}`,
        html: `<span>${number}</span>`,
        iconSize: [24, 38],
        iconAnchor: [0, 38],
    });
};

const StyledContentBox = styled(Box)(({ theme }) => ({
    border: "2px solid",
    borderColor: theme.palette.divider,
    borderRadius: "5px",
    backgroundColor: theme.palette.background.paper,
    padding: theme.spacing(1),
}));

function SelectHole({ data }) {
    const [selectOpen, setSelectOpen] = useState(false);
    const queryClient = useQueryClient();
    const { track_number } = useSelectedHole();

    const handleClose = () => {
        setSelectOpen(false);
    };
    const handleOpen = () => {
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
    useEffect(() => {
        if (
            (track_number === "" ||
                track_number === undefined ||
                (Array.isArray(data?.scores) &&
                    data?.scores.findIndex((val) => val.track_number === track_number) === -1)) &&
            Array.isArray(data?.scores)
        ) {
            //console.log("setting track number", data.scores[0].track_number);
            handleSelectHole({ target: { value: data.scores[0].track_number } });
        }
    }, [data]);

    const handleSelectHole = (e) => {
        queryClient.setQueryData(["CURRENT_SELECTED_HOLE"], (prev) => ({
            ...prev,
            track_number: e.target.value,
        }));
    };

    const hole_idx = data?.scores?.findIndex((val) => val.track_number === track_number);
    const current_hole_par =
        hole_idx !== undefined && hole_idx !== -1 ? data.scores[hole_idx].par : 0;
    const current_hole_dist =
        hole_idx !== undefined && hole_idx !== -1
            ? getShortDistance(
                  data.scores[hole_idx].tee_lat,
                  data.scores[hole_idx].tee_lng,
                  data.scores[hole_idx].basket_lat,
                  data.scores[hole_idx].basket_lng,
                  0,
              )
            : 0;

    return (
        <StyledContentBox
            onClick={handleBoxClick}
            sx={{
                position: "absolute",
                bottom: 0,
                left: 0,
                zIndex: 1000,
                pt: 0,
                pb: 0,
                ml: 1,
                mb: 12,
                pr: 1.5,
                pl: 1.5,
            }}
        >
            <Select
                variant="standard"
                value={track_number ?? ""}
                open={selectOpen}
                onOpen={handleOpen}
                onClose={handleClose}
                onChange={handleSelectHole}
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
                {data?.scores.map((val) => (
                    <MenuItem
                        selected={track_number === val.track_number}
                        key={val.track_number}
                        value={val.track_number}
                        sx={{
                            "&.Mui-selected": {
                                bgcolor: "primary.400",
                            },
                        }}
                    >{`Hole ${val.track_number}`}</MenuItem>
                ))}
            </Select>

            <Typography variant="h6" sx={{ lineHeight: "1.25em" }}>
                {`Par ${current_hole_par}`}
                <br />
                {`${current_hole_dist}M`}
            </Typography>
        </StyledContentBox>
    );
}

function calculateThrowDistance(t) {
    if (!t?.start_lat || !t?.start_lng || !t?.end_lat || !t?.end_lng) return "-";
    return getShortDistance(t.start_lat, t.start_lng, t.end_lat, t.end_lng);
}

function ThrowInfo({ currentThrow }) {
    const distance = calculateThrowDistance(currentThrow);

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

const testPos = [65.045512, 25.427889];

function useMutateThrow() {
    const queryClient = useQueryClient();
    const params = useParams({ strict: false });
    const { gameSessionId } = params;

    const { mutate } = useMutation({
        mutationFn: createThrow,
        onSuccess: (data) => {
            queryClient.setQueryData([GAME_SESSION_KEY, String(gameSessionId)], (oldSession) => {
                return oldSession
                    ? {
                          ...oldSession,
                          user_score: {
                              ...oldSession?.user_score,
                              scores: oldSession?.user_score?.scores?.map((score) =>
                                  score.track_number === data.track_number
                                      ? { ...score, ...data }
                                      : score,
                              ),
                          },
                      }
                    : {};
            });
        },
    });
    return mutate;
}

function GameControls({ scoreData }) {
    const queryClient = useQueryClient();
    const params = useParams({ strict: false });
    const { gameSessionId } = params;
    const mutate = useMutateThrow();
    const { moveToNextHole } = useHoleChanger();

    const handleNewThrow = (pos) => {
        // TODO: prompt user to allow location if we dont get it

        const selectedTrack = queryClient.getQueryData(["CURRENT_SELECTED_HOLE"]);

        const lat = import.meta.env.DEV ? testPos[0] - Math.random() * 0.005 : pos.coords.latitude;
        const lng = import.meta.env.DEV ? testPos[1] - Math.random() * 0.005 : pos.coords.longitude;

        mutate({
            data: {
                track_number: selectedTrack.track_number,
                game_session_id: gameSessionId,
                start_lat: lat,
                start_lng: lng,
            },
        });
    };

    const handleDeleteThrow = () => {
        // deletes last throw. Should we actually delete selected throw?
        const selectedTrack = queryClient.getQueryData(["CURRENT_SELECTED_HOLE"]);
        const holeScore = scoreData?.scores.find(
            (val) => val.track_number === selectedTrack.track_number,
        );
        if (!holeScore) {
            return;
        }

        const throw_id = holeScore?.throws
            .sort((a, b) => a.throw_number - b.throw_number)
            .at(-1)?.id;
        if (throw_id) {
            mutate({
                data: {
                    id: throw_id,
                },
                method: "DELETE",
            });
        }
    };

    const handleThrowButton = async () => {
        if (import.meta.env.DEV) {
            handleNewThrow();
        } else {
            await getPositionWithCallback(handleNewThrow, {
                timeout: 10,
                enableHighAccuracy: true,
            });
        }
    };

    return (
        <>
            <Box
                sx={{
                    width: "100%",
                    position: "absolute",
                    bottom: 36,
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
                    onClick={handleDeleteThrow}
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
                    onClick={handleThrowButton}
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
                    onClick={moveToNextHole}
                >
                    Next
                    <NavigateNextIcon />
                </Button>
            </Box>
        </>
    );
}

function ThrowMarker({ thrownum, position, onClick, isSelected, isMoving, onDragEnd, markerIdx }) {
    const markerRef = useRef(null);
    const [dragPosition, setDragPosition] = useState(position);

    const eventHandlers = useMemo(
        () => ({
            dragend() {
                const marker = markerRef.current;
                if (marker != null) {
                    // do we need this is parent updates position?
                    setDragPosition(marker.getLatLng());
                    onDragEnd(marker.getLatLng(), markerIdx);
                }
            },
            click: (e) => {
                onClick(thrownum);
            },
        }),
        [thrownum, markerIdx],
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

const createStartIcon = (number = null) => {
    return L.divIcon({
        className: `custom-tee-icon`,
        ...(number && { html: `<span>${number}</span>` }),
        iconSize: [20, 20],
        iconAnchor: [10, 10],
    });
};

export function StartMarker({ position, number = null }) {
    if (position) {
        return <Marker position={position} icon={createStartIcon(number)}></Marker>;
    }
}

export function BasketMarker({ position }) {
    return (
        <>
            <Circle center={position} radius={10} />
            <Circle center={position} radius={20} />
        </>
    );
}

function SessionMap({ sessionData }) {
    const [selectedThrowNum, setSelectedThrowNum] = useState(1);
    const [isMoving, setMoving] = useState(false);
    const selectedHole = useSelectedHole();
    const mutate = useMutateThrow();
    // temporary hold in state
    const [localScoreData, setLocalScoreData] = useState(null);
    const [markerCoords, setMarkerCoords] = useState([]);
    const originalPositionRef = useRef(null);

    useEffect(() => {
        const currentScore = sessionData?.user_score?.scores.find(
            (val) => val.track_number === selectedHole?.track_number,
        );
        // if we have more or less throws disable moving
        if (
            isMoving &&
            originalPositionRef.current &&
            originalPositionRef.current.length !== currentScore?.throws?.length
        ) {
            setMoving(false);
        }
        setLocalScoreData(currentScore);

        if (currentScore) {
            const markers = currentScore.throws.reduce((acc, val, idx) => {
                if (idx === 0 && val.start_lat && val.start_lng) {
                    acc.push([val.start_lat, val.start_lng]);
                }
                if (val.end_lat && val.end_lng) {
                    acc.push([val.end_lat, val.end_lng]);
                }
                return acc;
            }, []);
            setMarkerCoords(markers);
        }
    }, [selectedHole, sessionData]);

    const handleEndMoving = () => {
        // todo: send new positions to backend
        // check which ones have changed
        let updatedthrows = [];
        for (const [idx, val] of markerCoords.entries()) {
            // check if changed
            // get full throw object by id
            // update start position
            // add to array
            if (
                val[0] !== originalPositionRef.current[idx][0] ||
                val[1] !== originalPositionRef.current[idx][1]
            ) {
                const updateThrow = localScoreData.throws[idx];
                updatedthrows.push({ ...updateThrow, start_lat: val[0], start_lng: val[1] });
            }
        }
        if (updatedthrows.length > 0) {
            mutate({ data: updatedthrows, method: "PATCH" });
        }
    };

    const handleMovingStart = () => {
        if (isMoving) {
            setMoving(false);
            handleEndMoving();
        } else {
            // if throw is added during moving end moving
            // TODO: what if user changes hole during moving? -> maybe stop moving and discard
            originalPositionRef.current = markerCoords;
            setMoving(true);
        }
    };

    const handleDragEnd = (position, throwIdx) => {
        const pos = [position.lat, position.lng];
        if (markerCoords.length > throwIdx) {
            setMarkerCoords((prev) => {
                return prev.map((val, i) => (i === throwIdx ? pos : val));
            });
        }
    };

    const [startEndmarkers, startEndPositions] = useMemo(() => {
        if (localScoreData?.tee_lat == null) return [null, []];

        const startmarker = [localScoreData?.tee_lat, localScoreData?.tee_lng];
        const endMarker = [localScoreData?.basket_lat, localScoreData?.basket_lng];

        return [
            <>
                <StartMarker position={startmarker} />
                <BasketMarker position={endMarker} />
            </>,
            [startmarker, endMarker],
        ];
    }, [localScoreData]);

    const throwMarkers = useMemo(() => {
        return (
            <>
                {markerCoords.map((val, idx) => {
                    // should show last marker only when moving
                    const showMarker =
                        markerCoords.length === 1 || idx !== markerCoords.length - 1 || isMoving;
                    return (
                        showMarker && (
                            <ThrowMarker
                                key={`coordinate-${val[0]}-${val[1]}`}
                                position={val}
                                thrownum={idx + 1}
                                markerIdx={idx}
                                onClick={(num) => setSelectedThrowNum(num)}
                                isSelected={idx + 1 === selectedThrowNum}
                                isMoving={idx + 1 === selectedThrowNum && isMoving}
                                onDragEnd={handleDragEnd}
                            />
                        )
                    );
                })}
                {/* TODO: add distance labels to each line*/}
                <Polyline
                    positions={markerCoords}
                    pathOptions={{ color: "red", dashArray: "10, 10", dashOffset: "0" }}
                ></Polyline>
            </>
        );
    }, [markerCoords, selectedThrowNum, isMoving]);

    return (
        <>
            <Map>
                <LayerGroup key={selectedHole.track_number}>
                    {throwMarkers}
                    {startEndmarkers}
                </LayerGroup>
                <RecenterMap markers={[...markerCoords, ...startEndPositions]} />
            </Map>
            <ThrowInfo
                currentThrow={localScoreData?.throws?.find(
                    (val) => val.throw_number === selectedThrowNum,
                )}
            />
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
                onClick={handleMovingStart}
            >
                {isMoving ? "Moving!" : "Move"}
            </Button>
        </>
    );
}

export function MapView() {
    const { data: sessionData } = useGameSession();

    return (
        <Box sx={{ height: "100%", width: "100%", overflow: "hidden", position: "relative" }}>
            <SessionMap sessionData={sessionData} />
            <GameControls scoreData={sessionData?.user_score} />
            <SelectHole data={sessionData?.user_score} />

            <GameScoreDrawer />
        </Box>
    );
}
