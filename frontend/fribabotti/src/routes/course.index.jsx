import BottomAddButton from "#/components/BottomAddButton";
import { CourseList } from "#/course/CourseList";
import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { Route as NewCourseRoute } from "./course.new";

export const Route = createFileRoute("/course/")({
    component: RouteComponent,
    beforeLoad: () => ({
        headerTitle: "Courses",
    }),
});

function RouteComponent() {
    const navigate = useNavigate();

    return (
        <>
            <CourseList />
            <BottomAddButton onClick={async () => await navigate({ to: NewCourseRoute.to })} />
        </>
    );
}
