import { createFileRoute } from "@tanstack/react-router";
import { CourseEditor } from "#/course/CourseEditor";
import { courseQueryOptions } from "#/hooks/GameSessionHooks";
import { useSuspenseQuery } from "@tanstack/react-query";

export const Route = createFileRoute("/course/$courseId/edit")({
    component: RouteComponent,
    loader: ({ context: { queryClient }, params: { courseId } }) =>
        queryClient.ensureQueryData(courseQueryOptions(courseId)),
});

function RouteComponent() {
    const { courseId } = Route.useParams();

    const { data: course } = useSuspenseQuery(courseQueryOptions(courseId));

    return <CourseEditor course={course} />;
}
