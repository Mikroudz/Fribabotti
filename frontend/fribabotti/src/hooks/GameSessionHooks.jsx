import { useQuery } from "@tanstack/react-query";
import { getGameSession, getGameSessions } from "../utils/api";

export const useGameSessions = (notifyOnChangeProps) => {
    return useQuery({
        queryKey: ["gamesessions"],
        queryFn: getGameSessions,
        notifyOnChangeProps,
    });
};

export const useGameSession = (game_session_id, notifyOnChangeProps) => {
    return useQuery({
        queryKey: ["gamesession", game_session_id],
        queryFn: getGameSession,
        notifyOnChangeProps,
    });
};
