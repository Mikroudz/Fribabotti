import { List, ListItemSecondaryAction, ListItemText } from "@mui/material";
import { useCourses } from "../hooks/GameSessionHooks";
import { StyledListItem, StyledListItemButton } from "#/components/List";
import { Link, useLocation } from "@tanstack/react-router";
import { Route as CourseRoute } from "#/routes/course.$courseId.index";
import { Map, RecenterMap } from "#/components/MapComponents";
import { useMemo } from "react";
import { Marker } from "react-leaflet";

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

export function CourseListMap() {
    const { data: courses, status } = useCourses();

    const markers = useMemo(() => {
        return courses?.map((course) => (
            <Marker key={`${course.lat}-${course.lng}`} position={[course.lat, course.lng]}></Marker>
        ));
    }, [courses]);

    return (
        <Map>
            {markers}
            <RecenterMap markers={markers} />
        </Map>
    );
}
