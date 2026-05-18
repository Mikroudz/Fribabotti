import { useQuery, useQueryClient } from "@tanstack/react-query";
import { getGameSession, getGameSessions } from "../utils/api";
import { useParams } from "@tanstack/react-router";
import { useEffect } from "react";

export const GAME_SESSIONS_KEY = "gamesessions";
export const GAME_SESSION_KEY = "gamesession";
export const CURRENT_SELECTED_HOLE = "CURRENT_SELECTED_HOLE";

export const useGameSessions = (notifyOnChangeProps) => {
    return useQuery({
        queryKey: [GAME_SESSIONS_KEY],
        queryFn: getGameSessions,
        notifyOnChangeProps,
    });
};

export const useTracks(){
    return useQuery({
        queryKey: [GAME_SESSIONS_KEY],
        queryFn: getGameSessions,
        notifyOnChangeProps,
    });
}


// can pass id manually or get from route
export const useGameSession = (game_session_id = null, notifyOnChangeProps) => {
    const params = useParams({ strict: false });
    const { gameSessionId } = params;
    const queryClient = useQueryClient();

    const { data, ...rest } = useQuery({
        queryKey: ["gamesession", game_session_id !== null ? game_session_id : gameSessionId],
        queryFn: getGameSession,
        notifyOnChangeProps,
    });

    useEffect(() => {
        // TODO: get hole count from some other data than the user score
        // TODO: we really need to set max track count when moving to session path, not every time gamesession data changes, but this is simple solution for now
        const holeCount = data?.user_score?.scores ? data?.user_score?.scores?.length : null;
        queryClient.setQueryData(["CURRENT_SELECTED_HOLE"], (prev) => ({
            ...prev,
            hole_count: holeCount,
        }));
    }, [data]);

    return { data, ...rest };
};

export const useSelectedHole = () => {
    const { data: selectedHole } = useQuery({
        queryKey: ["CURRENT_SELECTED_HOLE"],
        enabled: false,
        staleTime: Infinity,
        initialData: { track_number: "", hole_count: null },
        queryFn: () => Promise.resolve([]),
    });

    return selectedHole;
};
