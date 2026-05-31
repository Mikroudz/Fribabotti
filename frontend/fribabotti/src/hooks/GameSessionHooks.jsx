import { queryOptions, useQuery, useQueryClient } from "@tanstack/react-query";
import {
    getGameSession,
    getGameSessions,
    getCourses,
    getCourse,
    getUserStats,
    getCourseHistoryStats,
} from "../utils/api";
import { useParams } from "@tanstack/react-router";
import { useCallback, useEffect } from "react";

export const GAME_SESSIONS_KEY = "gamesessions";
export const GAME_SESSION_KEY = "gamesession";
export const CURRENT_SELECTED_HOLE = "CURRENT_SELECTED_HOLE";

export const COURSES_KEY = "ALL_COURSES";

export const USER_GROUPS_KEY = "ALL_USER_GROUPS";

export const USER_STATS = "USER_STATS";

export const useGameSessions = (notifyOnChangeProps) => {
    return useQuery({
        queryKey: [GAME_SESSIONS_KEY],
        queryFn: () => getGameSessions({ limit: 15 }),
        initialData: [],
        notifyOnChangeProps,
    });
};

export const useCourses = (notifyOnChangeProps) => {
    // TODO: this really should be server side searchable and load only few tracks at a time

    return useQuery({
        queryKey: [COURSES_KEY],
        queryFn: getCourses,
        initialData: [],
        notifyOnChangeProps,
    });
};

export const useUserStats = (notifyOnChangeProps) => {
    return useQuery({
        queryKey: [USER_STATS],
        queryFn: getUserStats,
        notifyOnChangeProps,
    });
};

export const courseQueryOptions = (queryId) =>
    queryOptions({
        queryKey: ["COURSE", queryId],
        queryFn: getCourse,
    });

export const courseGraphQueryOptions = (queryId) =>
    queryOptions({
        queryFn: getCourseHistoryStats,
        queryKey: ["COURSE_HISTORY_STATS", queryId],
    });

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
    const { data } = useQuery({
        queryKey: ["CURRENT_SELECTED_HOLE"],
        enabled: false,
        staleTime: Infinity,
        gcTime: Infinity,
        initialData: { track_number: "", hole_count: null },
        queryFn: () => Promise.resolve({ track_number: "", hole_count: null }),
    });

    return data;
};

export const useHoleChanger = () => {
    const queryClient = useQueryClient();
    const params = useParams({ strict: false });
    const { gameSessionId } = params;

    const moveToNextHole = useCallback(() => {
        queryClient.setQueryData(["CURRENT_SELECTED_HOLE"], (prev) => {
            const { user_score: scoreData } = queryClient.getQueryData([
                "gamesession",
                gameSessionId,
            ]);

            let next_track_num = 1;
            if (Array.isArray(scoreData?.scores)) {
                const track_num_idx = scoreData?.scores.findIndex(
                    (val) => val.track_number === prev.track_number,
                );
                next_track_num = prev.track_number;
                if (scoreData?.scores.length > track_num_idx + 1) {
                    next_track_num = scoreData?.scores[track_num_idx + 1].track_number;
                }
            }

            return { ...prev, track_number: next_track_num };
        });
    }, [gameSessionId, queryClient]);

    const moveToPreviousHole = useCallback(() => {
        queryClient.setQueryData(["CURRENT_SELECTED_HOLE"], (prev) => {
            const { user_score: scoreData } = queryClient.getQueryData([
                "gamesession",
                gameSessionId,
            ]);

            let next_track_num = 1;
            if (Array.isArray(scoreData?.scores)) {
                const track_num_idx = scoreData?.scores.findIndex(
                    (val) => val.track_number === prev.track_number,
                );
                next_track_num = prev.track_number;
                if (track_num_idx - 1 >= 0) {
                    next_track_num = scoreData?.scores[track_num_idx - 1].track_number;
                }
            }

            return { ...prev, track_number: next_track_num };
        });
    }, [gameSessionId, queryClient]);

    return { moveToNextHole, moveToPreviousHole };
};
