import { AppBar, IconButton, Toolbar, Typography } from "@mui/material";
import { useCanGoBack, useMatches, useRouter } from "@tanstack/react-router";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
export function HeaderBar() {
    const router = useRouter();
    const canGoBack = useCanGoBack();

    const handleBack = () => {
        router.history.back();
    };
    const matches = useMatches();
    // 2. Find the lowest-level matched route that defines a headerTitle
    const currentTitle =
        [...matches].reverse().find((match) => match.context?.headerTitle)?.context?.headerTitle ||
        "Fribabotti";

    return (
        <AppBar position="static" sx={{ flexShrink: 0 }}>
            <Toolbar>
                {canGoBack && (
                    <IconButton
                        size="large"
                        edge="start"
                        color="inherit"
                        aria-label="back"
                        onClick={handleBack}
                        sx={{ mr: 2 }}
                    >
                        <ArrowBackIcon />
                    </IconButton>
                )}
                <Typography variant="h6">{currentTitle}</Typography>
            </Toolbar>
        </AppBar>
    );
}
