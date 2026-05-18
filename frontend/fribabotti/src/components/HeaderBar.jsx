import { AppBar, IconButton, Toolbar, Typography } from "@mui/material";
import { useCanGoBack, useRouter } from "@tanstack/react-router";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
export function HeaderBar() {
    const router = useRouter();
    const canGoBack = useCanGoBack();

    const handleBack = () => {
        router.history.back();
    };

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
                <Typography variant="h6">Fribabotti</Typography>
            </Toolbar>
        </AppBar>
    );
}
