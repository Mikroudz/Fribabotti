import { GameSessionContextProvider } from "#/context/GameSessionData";
import { createFileRoute, Outlet } from "@tanstack/react-router";

export const Route = createFileRoute("/gamesession_/$gameSessionId/_sessionlayout")({
    component: RouteComponent,
});

function RouteComponent() {
    return (
        <GameSessionContextProvider>
            <Outlet />
        </GameSessionContextProvider>
    );
}
