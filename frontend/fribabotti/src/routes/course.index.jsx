import BottomAddButton from "#/components/BottomAddButton";
import { CourseList, CourseListMap } from "#/course/CourseList";
import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { Route as NewCourseRoute } from "./course.new";
import { Box, Chip } from "@mui/material";
import { useState } from "react";

export const Route = createFileRoute("/course/")({
    component: RouteComponent,
    beforeLoad: () => ({
        headerTitle: "Courses",
    }),
});

function SelectListMap({ selectedChip, onChipClicked }) {
    return (
        <Box sx={{ gap: 1, display: "flex", mt: 1, mb: 1, width: "100%", justifyContent: "center" }}>
            <Chip
                onClick={() => onChipClicked("list")}
                label="List"
                sx={{ bgcolor: selectedChip === "list" ? "primary.500" : "primary.main", fontSize: "16px" }}
            ></Chip>
            <Chip
                onClick={() => onChipClicked("map")}
                label="Map"
                sx={{ bgcolor: selectedChip === "map" ? "primary.500" : "primary.main", fontSize: "16px" }}
            ></Chip>
        </Box>
    );
}

function RouteComponent() {
    const navigate = useNavigate();
    const [selectedChip, setSelectedChip] = useState("list");

    // TODO: split map and list to own routes

    return (
        <>
            <SelectListMap selectedChip={selectedChip} onChipClicked={setSelectedChip} />
            {selectedChip === "list" && <CourseList />}
            {selectedChip === "map" && <CourseListMap />}

            <BottomAddButton onClick={async () => await navigate({ to: NewCourseRoute.to })} />
        </>
    );
}
