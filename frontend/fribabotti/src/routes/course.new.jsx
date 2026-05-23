import { CourseEditor } from "#/course/CourseEditor";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/course/new")({
    component: RouteComponent,
    beforeLoad: () => ({
        headerTitle: "Create Course",
    }),
});

function RouteComponent() {
    return <CourseEditor course={null} />;
}
