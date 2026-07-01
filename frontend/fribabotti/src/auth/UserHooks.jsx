import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { getUser, signOut, telegramAuth } from "../utils/api";
import { useNavigate } from "@tanstack/react-router";
import { useEffect } from "react";

export const USER_QUERY_KEY = "CURRENT_USER";
export const LOGOUT_QUERY_KEY = "LOGOUT";

export const useUser = () => {
    const { data: user } = useQuery({
        queryKey: [USER_QUERY_KEY],
        queryFn: getUser,
        refetchOnMount: true,
        refetchOnWindowFocus: false,
        refetchOnReconnect: false,
        initialData: readUser,
    });

    useEffect(() => {
        if (!user) storageRemoveUser();
        else storeUser(user);
    }, [user]);

    return { user: user ?? null };
};

export function useSignIn() {
    const queryClient = useQueryClient();

    const navigate = useNavigate();

    const { mutateAsync: signInMutation } = useMutation(
        {
            mutationFn: (data) => telegramAuth(data),
            onSuccess: (data) => {
                queryClient.setQueryData([USER_QUERY_KEY], data);
                //storeUser(data);
                const navToAfterLogin = queryClient.getQueryData(["AUTH_FAIL_REDIRECT"]);
                console.log("navigating to", navToAfterLogin);

                navigate({
                    to: navToAfterLogin && !/auth/i.test(navToAfterLogin) ? navToAfterLogin : "/",
                });
            },
            onError: () => {
                //showSnack("Login failed", "error");
            },
        },
        queryClient,
    );
    return signInMutation;
}

export async function executeSignOut() {
    try {
        await signOut();
    } catch (e) {
        console.log(e);
    }
    storageRemoveUser();
    queryClient.setQueryData([USER_QUERY_KEY], null);
}

export function useSignOut(client = null, nav_router = null) {
    const queryClient = client ? client : useQueryClient();
    const navigate = nav_router ? nav_router : useNavigate();

    const { mutateAsync: signOutMutation } = useMutation(
        {
            mutationFn: signOut,
            mutationKey: [LOGOUT_QUERY_KEY],
            onSuccess: () => {
                console.log("Logout success");
            },
            onError: () => {
                console.log("logout error");
            },
            onSettled: () => {
                console.log("logout settled");
                storageRemoveUser();
                queryClient.setQueryData([USER_QUERY_KEY], null);
                navigate({ to: "/auth" });
                //throw redirect({ to: "/auth", search: { redirect: location.href } });
            },
        },
        queryClient,
    );
    return signOutMutation;
}

export function storeUser(data) {
    localStorage.setItem(USER_QUERY_KEY, JSON.stringify(data));
}

export function readUser() {
    const user = localStorage.getItem(USER_QUERY_KEY);
    return user ? JSON.parse(user) : undefined;
}

export function storageRemoveUser() {
    localStorage.removeItem(USER_QUERY_KEY);
}
