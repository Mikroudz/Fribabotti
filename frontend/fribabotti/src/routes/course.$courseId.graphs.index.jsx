import { createFileRoute, redirect } from "@tanstack/react-router";
import { Route as RouteScore } from "#/routes/course.$courseId.graphs.score";

export const Route = createFileRoute("/course/$courseId/graphs/")({
    loader: () => {
        throw redirect({
            to: RouteScore.to,
            replace: true,
        });
    },
});
