import { List, ListItemSecondaryAction, ListItemText, Typography } from "@mui/material";
import { useCourses } from "../hooks/GameSessionHooks";
import { StyledListItem, StyledListItemButton } from "#/components/List";
import { Link, useLocation } from "@tanstack/react-router";
import { Route as CourseRoute } from "#/routes/course.$courseId.index";
import { Map, RecenterMap } from "#/components/MapComponents";
import { useMemo } from "react";
import { Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

export function CourseList() {
    const { data: courses, status } = useCourses();
    const location = useLocation();

    return (
        <List dense sx={{ m: 1 }}>
            {courses?.map((val) => (
                <StyledListItem key={val.id} sx={{ alignItems: "center" }}>
                    <StyledListItemButton
                        component={Link}
                        to={CourseRoute.to}
                        params={{ courseId: val.id }}
                        from={location.pathname}
                    >
                        <ListItemText primary={val?.name} />
                        <ListItemSecondaryAction>{val?.holes} holes</ListItemSecondaryAction>
                    </StyledListItemButton>
                </StyledListItem>
            ))}
        </List>
    );
}

const createIcon = () => {
    return L.divIcon({
        className: `custom-trackmap-marker`,
        iconSize: [24, 38],
        iconAnchor: [0, 38],
    });
};

export function CourseListMap() {
    const { data: courses, status } = useCourses();

    const [markers, markerCoords] = useMemo(() => {
        const pos = courses?.filter((val) => val.lat && val.lng);

        return [
            pos.map((course) => (
                <Marker
                    key={`${course.lat}-${course.lng}`}
                    position={[course.lat, course.lng]}
                    icon={createIcon()}
                >
                    <Popup>
                        <Typography
                            component={Link}
                            to={CourseRoute.to}
                            params={{ courseId: course.id }}
                            sx={{ fontWeight: 600 }}
                        >
                            {course.name}
                        </Typography>
                    </Popup>
                </Marker>
            )),
            pos,
        ];
    }, [courses]);

    return (
        <Map>
            {markers}
            <RecenterMap markers={markerCoords} />
        </Map>
    );
}
