import { MapView } from "#/game_session/MapView";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/gamesession_/$gameSessionId/_sessionlayout/map")({
    component: RouteComponent,
});

function RouteComponent() {
    return <MapView />;
}
