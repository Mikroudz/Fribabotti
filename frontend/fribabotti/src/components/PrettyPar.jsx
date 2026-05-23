import { Box, Typography, useTheme } from "@mui/material";

export function prettyParFormat(score, par = 0) {
    const isInt = score % 1 === 0; //? Number(score.toFixed(1)) : score;

    if (score === 0) {
        return "-";
    } else if (score === par) {
        return "E";
    } else if (score > par) {
        const ret = !isInt ? Number((score - par).toFixed(1)) : score - par;
        return `+${ret}`;
    } else {
        return !isInt ? Number((score - par).toFixed(1)) : score - par;
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
