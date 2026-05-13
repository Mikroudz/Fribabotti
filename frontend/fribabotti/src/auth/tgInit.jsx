import {
    viewport,
    themeParams,
    miniApp,
    initData,
    setDebug,
    init as initSDK,
    backButton,
} from "@tma.js/sdk-react";

/**
 * Initializes the application and configures its dependencies.
 */
export function tgInit(debug = false) {
    setDebug(debug);

    initSDK();

    if (!miniApp.mount.isAvailable()) {
        return;
    }
    miniApp.mount();
    themeParams.mount();
    initData.restore();
    void viewport.mount().catch((e) => {
        console.error("Something went wrong mounting the viewport", e);
    });
    if (backButton.isSupported()) {
        backButton.mount();
    }

    // Define components-related CSS variables.
    viewport.bindCssVars();
    miniApp.bindCssVars();
    themeParams.bindCssVars();
}
