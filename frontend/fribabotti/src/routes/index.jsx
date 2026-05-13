import { createFileRoute } from "@tanstack/react-router";
import { GameSessionList } from "../game_session/GameSessionList";

export const Route = createFileRoute("/")({ component: Home });

function Home() {
    // Make everything a component
    // where we could construct like main view from smaller components easily
    // like sessions, top scores, other fun things

    return <GameSessionList />;
}
