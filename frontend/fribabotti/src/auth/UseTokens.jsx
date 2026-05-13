import { useCallback, useRef } from "react";
import { useSignOut } from "./UserHooks";
import { useMutation } from "@tanstack/react-query";
import { refreshToken } from "../utils/api";
import { TgWebAppAuth } from "./TelegramWebappHooks";

const REFRESH_QUERY_KEY = "refresh_token";

export function useTokens({ queryClient, navigate, route_state }) {
    const refreshPromiseRef = useRef(null);
    const signingOutRef = useRef(false);
    const signOutMutation = useSignOut(queryClient, navigate);
    const signInWithWebApp = TgWebAppAuth(queryClient, navigate);

    const { mutateAsync: refreshMutation } = useMutation(
        {
            mutationFn: refreshToken,
            mutationKey: [REFRESH_QUERY_KEY],
            onSuccess: () => {
                console.log("token refresh mutation successfull");
            },
        },
        queryClient,
    );

    const refreshTokens = useCallback(async () => {
        if (refreshPromiseRef.current) {
            return refreshPromiseRef.current;
        }

        await queryClient.cancelQueries();

        refreshPromiseRef.current = refreshMutation()
            .then(() => {})
            .catch(async (error) => {
                refreshPromiseRef.current = null;
                if (!signingOutRef.current) {
                    // need to reauth with telegram/login
                    if (await signInWithWebApp()) {
                        queryClient.refetchQueries({ stale: true });
                        console.log("signed in with telegram webapp");
                    } else {
                        signingOutRef.current = true;

                        try {
                            await signOutMutation();
                        } finally {
                            signingOutRef.current = false;
                        }
                    }
                }
                throw error;
            })
            .finally(() => {
                refreshPromiseRef.current = null;
            });

        return refreshPromiseRef.current;
    }, [queryClient, signOutMutation]);

    const onAuthError = useCallback(
        async (error) => {
            const { status, url } = error;
            if (status && [401, 403].includes(status)) {
                const { pathname } = new URL(url);

                if (!/(\/(users|auth\/refresh)$)/i.test(pathname)) {
                    try {
                        await refreshTokens();
                        console.log("success token promise");
                        return true;
                    } catch (error) {
                        queryClient.setQueryData(["AUTH_FAIL_REDIRECT"], route_state.location.href);
                        console.log("failure token promise");
                    }
                }
            }
            return false;
        },
        [refreshTokens],
    );

    return { onAuthError, refreshTokens };
}
