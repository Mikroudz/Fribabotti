import { USER_QUERY_KEY } from "./UserHooks";
import { isTelegramApp, TELEGRAM_AUTH_TYPES } from "../utils/telegramHelpers";
import {
    useRawInitData,
    useLaunchParams,
    retrieveRawLaunchParams,
    retrieveLaunchParams,
    retrieveRawInitData,
} from "@tma.js/sdk-react";
import { telegramAuth } from "../utils/api";

export function useLaunchDataTg() {
    if (isTelegramApp()) {
        return useLaunchParams();
    } else {
        return { tgWebAppData: undefined };
    }
}

export function useRawTgInitData() {
    if (isTelegramApp()) {
        return useRawInitData();
    } else {
        return { initdata: undefined };
    }
}

export async function executeTgWebAppAuth(queryClient) {
    if (isTelegramApp()) {
        const launchParam = retrieveRawInitData();
        console.log("Trying to auth via webapp");
        const authData = {
            type: TELEGRAM_AUTH_TYPES.webapp,
            value: launchParam,
        };
        let result;
        try {
            result = await telegramAuth(authData);
        } catch {
            return false;
        }
        queryClient.setQueryData([USER_QUERY_KEY], result);
        return true;
    }
    return false;
}
/*
export function TgWebAppAuth(queryClient, nav) {
    const signInMutation = useSignIn(queryClient, nav);
    const launchData = useLaunchDataTg();
    const launchParamRaw = useRawTgInitData();
    const isSigningIn = useRef(false);

    const signInWithWebApp = useCallback(async () => {
        if (isTelegramApp() && !isSigningIn.current) {
            console.log("logging in to webapp");
            isSigningIn.current = true;
            const initData = launchData.tgWebAppData;
            if (typeof initData?.user !== "undefined") {
                const authData = {
                    type: TELEGRAM_AUTH_TYPES.webapp,
                    value: launchParamRaw,
                };

                try {
                    console.log("trying to sing in with data", authData);
                    await signInMutation(authData);
                    isSigningIn.current = false;
                    return true;
                } catch (error) {
                    console.log(error);
                    isSigningIn.current = false;
                    return false;
                }
            }
        }
        return false;
    }, [signInMutation, launchData, launchParamRaw]);

    return signInWithWebApp;
}*/
