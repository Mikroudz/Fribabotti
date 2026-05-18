import { Box, Typography, useTheme } from "@mui/material";

export function prettyParFormat(score, par = 0) {
    if (score === 0) {
        return "-";
    } else if (score === par) {
        return "E";
    } else if (score > par) {
        return `+${score - par}`;
    } else {
        return score - par;
    }
}

export function getScoreColor(score, palette) {
    const colorMap = {
        "-3": palette.primary[100],
        "-2": palette.primary[200],
        "-1": palette.primary[400],
        0: "",
        1: palette.secondary[400],
        2: palette.secondary[600],
        3: palette.secondary[700],
        4: palette.secondary[800],
    };
    if (score > 4) {
        return colorMap[4];
    }
    return colorMap[score];
}

export function PrettyPar({ score, par = 0, coloredContainer = false, wrap = true, ...rest }) {
    const theme = useTheme();

    const bgColor =
        coloredContainer && score !== 0 ? getScoreColor(score - par, theme.palette) : "";

    const formatted = (
        <Typography component="span" {...rest}>
            {prettyParFormat(score, par)}
        </Typography>
    );

    if (wrap) {
        return (
            <Box
                sx={{ bgcolor: bgColor, width: "100%", justifyContent: "center", display: "flex" }}
            >
                {formatted}
            </Box>
        );
    } else {
        return formatted;
    }
}
