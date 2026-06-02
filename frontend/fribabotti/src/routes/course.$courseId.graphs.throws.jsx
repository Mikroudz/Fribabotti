import { CourseTrackScatter } from "#/course/CourseTrackScatter";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/course/$courseId/graphs/throws")({
    component: RouteComponent,
});

function RouteComponent() {
    const { courseId } = Route.useParams();
    return <CourseTrackScatter course_id={courseId} />;
}
