import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { GameSessionList } from "../game_session/GameSessionList";
import { Box, Button, Typography } from "@mui/material";
import { Route as NewGameRoute } from "./gamesession_/new";

import { useGameSessions } from "#/hooks/GameSessionHooks";
import BottomAddButton from "#/components/BottomAddButton";
import { UserGameOverview } from "#/game_session/UserGameOverview";

export const Route = createFileRoute("/")({ component: Home });

function Home() {
    // Make everything a component
    // where we could construct like main view from smaller components easily
    // like sessions, top scores, other fun things
    const { data: gameSessions, status } = useGameSessions();
    const navigate = useNavigate();

    return (
        <Box sx={{ m: 1 }}>
            <UserGameOverview />
            <Typography>Ongoing Games</Typography>
            <GameSessionList gameSessions={gameSessions.filter((val) => val.ended_at === null)} />
            <Typography>Past Games</Typography>
            <GameSessionList gameSessions={gameSessions.filter((val) => val.ended_at)} />

            <BottomAddButton onClick={async () => await navigate({ to: NewGameRoute.to })} extended>
                New Game
            </BottomAddButton>
        </Box>
    );
}
