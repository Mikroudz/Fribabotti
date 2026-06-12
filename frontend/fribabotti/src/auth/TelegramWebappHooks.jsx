import { USER_QUERY_KEY } from "./UserHooks";
import { isTelegramApp, TELEGRAM_AUTH_TYPES } from "../utils/telegramHelpers";
import { useRawInitData, useLaunchParams, retrieveRawInitData } from "@tma.js/sdk-react";
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
    if (await isTelegramApp()) {
        console.log("Trying to auth via webapp");
        const launchParam = retrieveRawInitData();

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
