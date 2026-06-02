import { createFileRoute } from "@tanstack/react-router";
import { CourseGraph } from "#/course/CourseGraph";

export const Route = createFileRoute("/course/$courseId/graphs/score")({
    component: RouteComponent,
});

function RouteComponent() {
    return <CourseGraph />;
}
