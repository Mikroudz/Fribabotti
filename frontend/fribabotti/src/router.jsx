import { createRouter as createTanStackRouter } from "@tanstack/react-router";
import { routeTree } from "./routeTree.gen";

import { getContext } from "./integrations/tanstack-query/root-provider";
import { useTokens } from "./auth/UseTokens";
import { createAuthManager } from "./auth/authManager";

export function getRouter() {
    const context = getContext();

    const router = createTanStackRouter({
        routeTree,
        context,
        scrollRestoration: true,
        defaultPreload: "intent",
        defaultPreloadStaleTime: 0,
    });

    const authManager = createAuthManager({
        queryClient: context.queryClient,
        router: router,
    });

    context.authHandlerRef.current = authManager.onAuthError;

    return router;
}
