import { queryOptions, useQuery, useQueryClient } from "@tanstack/react-query";
import {
    getGameSession,
    getGameSessions,
    getCourses,
    getCourse,
    getUserGroups,
    getUserStats,
    getUserGroup,
    getGroupInvite,
} from "../utils/api";
import { useParams } from "@tanstack/react-router";
import { useCallback, useEffect } from "react";

export const USER_GROUPS = "USER_GROUPS";
export const USER_GROUP = "USER_GROUP";
export const GROUP_INVITE = "GROUP_INVITE";

export const useUserGroups = (notifyOnChangeProps) => {
    return useQuery({
        queryKey: [USER_GROUPS],
        queryFn: getUserGroups,
        initialData: [],
        notifyOnChangeProps,
    });
};

export const useUserGroup = (group_id, notifyOnChangeProps) => {
    return useQuery({
        queryKey: [USER_GROUP, group_id],
        queryFn: getUserGroup,
        notifyOnChangeProps,
    });
};

export const useGetGroupInvite = (invite, notifyOnChangeProps) => {
    return useQuery({
        queryKey: [GROUP_INVITE, invite],
        queryFn: getGroupInvite,
        notifyOnChangeProps,
    });
};
