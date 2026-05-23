import { GameTitleInformation } from "#/game_session/GameTitle";
import { ScoreCard } from "#/game_session/Scorecard";
import { Button, useTheme } from "@mui/material";
import { createFileRoute, Link } from "@tanstack/react-router";
import { Route as MapRoute } from "./_sessionlayout.map";
import { useGameSession } from "#/hooks/GameSessionHooks";

export const Route = createFileRoute("/gamesession_/$gameSessionId/gamesession")({
    component: RouteComponent,
});

function RouteComponent() {
    const { gameSessionId } = Route.useParams();
    const { data, status } = useGameSession(gameSessionId);
    const theme = useTheme();
    console.log(data);

    return (
        <>
            <GameTitleInformation data={data} />
            <ScoreCard data={data} />
            <Button
                variant="contained"
                sx={{ bgcolor: "secondary.main", width: "100%", mt: 2 }}
                component={Link}
                to={MapRoute.to}
                params={{ gameSessionId }}
            >
                Map
            </Button>
        </>
    );
}
