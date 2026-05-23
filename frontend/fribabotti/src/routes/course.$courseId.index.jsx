import { CourseMainPage } from "#/course/CourseMainPage";
import { courseQueryOptions } from "#/hooks/GameSessionHooks";
import { useSuspenseQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/course/$courseId/")({
    component: RouteComponent,
    loader: ({ context: { queryClient }, params: { courseId } }) =>
        queryClient.ensureQueryData(courseQueryOptions(courseId)),
});

// Todo: show some fun stats about this track
// possible best score, start new round, weather
// average score per hole graph and best per hole (new view)
// later: best in group, latest group games
function RouteComponent() {
    const { courseId } = Route.useParams();

    const { data: course } = useSuspenseQuery(courseQueryOptions(courseId));

    return <CourseMainPage course={course} />;
}
