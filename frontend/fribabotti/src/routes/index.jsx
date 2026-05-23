import { createFileRoute, Link } from "@tanstack/react-router";
import { GameSessionList } from "../game_session/GameSessionList";
import { Button } from "@mui/material";
import { Route as CourseRoute } from "./course.index";
import { useGameSessions } from "#/hooks/GameSessionHooks";

export const Route = createFileRoute("/")({ component: Home });

function Home() {
    // Make everything a component
    // where we could construct like main view from smaller components easily
    // like sessions, top scores, other fun things
    const { data: gameSessions, status } = useGameSessions();

    return (
        <>
            <GameSessionList gameSessions={gameSessions} />
            <Button
                nativeButton={false}
                variant="contained"
                sx={{ bgcolor: "secondary.main", width: "100%" }}
                component={Link}
                to={CourseRoute.to}
            >
                Courses
            </Button>
        </>
    );
}
