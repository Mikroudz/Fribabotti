import { Box, styled } from "@mui/material";

export const StyledAnyContentBox = styled(Box)(({ theme }) => ({
    margin: theme.spacing(1),
    padding: theme.spacing(1),

    backgroundColor: theme.palette.background.paper,
    border: "1px solid",
    borderColor: theme.palette.divider,
    borderRadius: "7px",
}));
