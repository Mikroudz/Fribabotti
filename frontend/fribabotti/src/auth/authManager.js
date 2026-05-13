import { refreshToken } from "../utils/api";
import { executeTgWebAppAuth } from "./TelegramWebappHooks";
import { executeSignOut } from "./UserHooks";

export function createAuthManager({ queryClient, router }) {
    // Replace useRef with standard closure variables
    let refreshPromise = null;
    let signingOut = false;

    const refreshTokens = async () => {
        if (refreshPromise) {
            return refreshPromise;
        }

        await queryClient.cancelQueries();

        // Replace useMutation with standard JS async logic
        refreshPromise = (async () => {
            try {
                // Assuming `refreshToken` is your actual API call function
                await refreshToken();
                console.log("token refresh mutation successfull");
            } catch (error) {
                if (!signingOut) {
                    // NOTE: TgWebAppAuth and useSignOut must be plain JS functions now!
                    const signedIn = await executeTgWebAppAuth(queryClient);

                    if (signedIn) {
                        const navToAfterLogin = queryClient.getQueryData(["AUTH_FAIL_REDIRECT"]);
                        console.log("navigating to", navToAfterLogin);
                        router.navigate({
                            to:
                                navToAfterLogin && !/auth/i.test(navToAfterLogin)
                                    ? navToAfterLogin
                                    : "/",
                        });

                        queryClient.refetchQueries({ stale: true });
                        console.log("signed in with telegram webapp");
                    } else {
                        signingOut = true;
                        try {
                            await executeSignOut();
                        } finally {
                            signingOut = false;
                            navigate({ to: "/auth" });
                        }
                    }
                }
                throw error;
            } finally {
                refreshPromise = null;
            }
        })();

        return refreshPromise;
    };

    const onAuthError = async (error) => {
        const { status, url } = error;
        if (status && [401, 403].includes(status)) {
            const { pathname } = new URL(url);

            if (!/(\/(users|auth\/refresh)$)/i.test(pathname)) {
                try {
                    await refreshTokens();
                    console.log("success token promise");
                    return true;
                } catch (error) {
                    // Access router state directly dynamically
                    queryClient.setQueryData(["AUTH_FAIL_REDIRECT"], router.state.location.href);
                    console.log("failure token promise");
                }
            }
        }
        return false;
    };

    return { onAuthError, refreshTokens };
}
