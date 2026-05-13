import { MutationCache, QueryCache, QueryClient } from "@tanstack/react-query";

export const checkThrowQuery = (error) => {
    const { status } = error;
    console.log("checkthrow", status);
    if (status && [401, 403, 413, 415].includes(status)) {
        return false;
    }
    return false;
};

const createQueryClient = (getAuthErrorFn, options = {}) => {
    const queryClient = new QueryClient({
        defaultOptions: {
            queries: {
                retry: (failureCount, error) => {
                    console.log("got reply", error);
                    const { status } = error;
                    if (status && [401, 403].includes(status)) {
                        return false;
                    }

                    return failureCount <= 3;
                },
                throwOnError: checkThrowQuery,
            },
            mutations: {
                throwOnError: checkThrowQuery,
            },
        },
        queryCache: new QueryCache({
            onError: async (error, query) => {
                console.log("query:", query, error);
                const onAuthError = getAuthErrorFn();
                if (onAuthError && (await onAuthError(error))) {
                    //console.log("restarting queries");
                    await queryClient.refetchQueries(query.queryKey);
                    // For "users" we need to check if query can be removed because will cause infinite queries in auth window.
                } else if (
                    !(Array.isArray(query.queryKey) && query.queryKey.includes("CURRENT_USER"))
                ) {
                    //console.log("removing failed query", query.queryKey);
                    queryClient.removeQueries({ queryKey: query.queryKey });
                }
            },
        }),
        mutationCache: new MutationCache({
            onError: async (error, variables, context, mutation) => {
                const onAuthError = getAuthErrorFn();
                if (onAuthError && (await onAuthError(error))) {
                    //console.log("restarting mutations");
                    await mutation.execute(variables, context);
                }
            },
        }),
        ...options,
    });
    return queryClient;
};

export function getContext() {
    const authHandlerRef = { current: null };
    const queryClient = createQueryClient(() => authHandlerRef.current);

    return { queryClient, authHandlerRef };
}
export default function TanstackQueryProvider() {}
