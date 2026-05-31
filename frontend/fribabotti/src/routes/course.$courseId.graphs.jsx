import { CourseGraph } from "#/course/CourseGraph";
import { courseGraphQueryOptions } from "#/hooks/GameSessionHooks";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/course/$courseId/graphs")({
    component: RouteComponent,
    loader: ({ context: { queryClient }, params: { courseId } }) =>
        queryClient.ensureQueryData(courseGraphQueryOptions(courseId)),
});

function RouteComponent() {
    return <CourseGraph />;
}
