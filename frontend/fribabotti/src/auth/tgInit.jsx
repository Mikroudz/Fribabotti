import {
    viewport,
    themeParams,
    miniApp,
    initData,
    setDebug,
    init as initSDK,
} from "@tma.js/sdk-react";

/**
 * Initializes the application and configures its dependencies.
 */
export function tgInit(debug = false) {
    console.log("initing tg webapp");
    try {
        initSDK();
    } catch (e) {
        console.log(e);
    }
    setDebug(debug);

    if (!miniApp.mount.isAvailable()) {
        return;
    }
    miniApp.mount();
    themeParams.mount();
    initData.restore();
    void viewport.mount().catch((e) => {
        console.error("Something went wrong mounting the viewport", e);
    });
    //if (backButton.isSupported()) {
    //    backButton.mount();
    //}

    // Define components-related CSS variables.
    viewport.bindCssVars();
    miniApp.bindCssVars();
    themeParams.bindCssVars();
    if (miniApp.ready.isAvailable()) {
        miniApp.ready();
    }
    console.log("webapp init done");
}
