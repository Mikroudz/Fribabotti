import { EditGameSession } from "#/game_session/EditGameSession";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/gamesession_/new")({
    component: RouteComponent,
});

function RouteComponent() {
    return <EditGameSession />;
}
