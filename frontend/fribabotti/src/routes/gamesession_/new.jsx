import { EditGameSession } from "#/game_session/EditGameSession";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/gamesession_/new")({
    component: RouteComponent,
    validateSearch: (search) => {
        const ret = { course_id: null };
        if (Object.hasOwn(search, "course_id") && !isNaN(search.course_id)) {
            ret.course_id = search.course_id;
        } else {
            return "";
        }
        return ret;
    },
});

function RouteComponent() {
    const { course_id } = Route.useSearch();
    const prefill = course_id === null ? null : { course_id: course_id };
    return <EditGameSession gameSession={prefill} />;
}
