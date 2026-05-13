import { GameTitleInformation } from "#/game_session/GameTitle";
import { ScoreCard } from "#/game_session/Scorecard";
import { Button, useTheme } from "@mui/material";
import { createFileRoute, Link } from "@tanstack/react-router";
import { Route as MapRoute } from "./map";

export const Route = createFileRoute("/gamesession_/$gameSessionId/gamesession")({
    component: RouteComponent,
});

function RouteComponent() {
    const { gameSessionId } = Route.useParams();
    const theme = useTheme();

    return (
        <>
            <GameTitleInformation />
            <ScoreCard />
            <Button
                variant="contained"
                sx={{ bgcolor: "secondary.main", width: "100%" }}
                component={Link}
                to={MapRoute.to}
                params={{ gameSessionId }}
            >
                Map
            </Button>
        </>
    );
}
