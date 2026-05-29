import { createFileRoute } from "@tanstack/react-router";

import { useEffect, useRef } from "react";
import { Box, Grid, Typography } from "@mui/material";
import { TELEGRAM_AUTH_TYPES } from "../utils/telegramHelpers";
import { useSignIn } from "../auth/UserHooks";
import FribaIcon from "../utils/FribaIcon";

export const Route = createFileRoute("/auth/")({
    component: AuthPage,
});

function AuthPage() {
    const signInMutation = useSignIn();

    const handleLogin = (data) => {
        //console.log(data);
        signInMutation({ type: TELEGRAM_AUTH_TYPES.auth_widget, ...data });
    };

    return (
        <Grid
            sx={{
                height: "100vh",
                width: "100%",
                display: "flex",
                direction: "column",
                alignItems: "center",
                justifyContent: "center",
            }}
        >
            <Box
                sx={{
                    display: "flex",
                    flexDirection: "column",
                    width: "auto",
                    justifyContent: "center",
                    alignItems: "center",
                }}
            >
                <FribaIcon sx={{ fontSize: "64", color: "secondary" }} />
                <Typography variant="h4" sx={{ pb: 3 }}>
                    Login
                </Typography>
                <TelegramAuth onAuthentication={handleLogin} />
            </Box>
        </Grid>
    );
}

function TelegramAuth({ onAuthentication }) {
    const ref = useRef(null);

    useEffect(() => {
        window.TelegramLoginWidget = {
            dataOnauth: (user) => onAuthentication(user),
        };

        const script = document.createElement("script");

        script.src = "https://telegram.org/js/telegram-widget.js?22";
        script.setAttribute("async", true);
        script.setAttribute("data-telegram-login", import.meta.env.VITE_TELEGRAM_BOT_NAME);
        script.setAttribute("data-size", "large");
        script.setAttribute("data-request-access", "write");
        script.setAttribute("property", "csp-nonce");

        script.setAttribute("data-onauth", "TelegramLoginWidget.dataOnauth(user)");

        if (ref.current) {
            ref.current.appendChild(script);
        }
        return () => {
            if (ref.current) {
                ref.current.removeChild(script);
            }
            delete window.TelegramLoginWidget;
        };
    }, []);

    return <div ref={ref}></div>;
}
