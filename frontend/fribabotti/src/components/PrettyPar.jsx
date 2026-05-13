import { Typography, useTheme } from "@mui/material";

export function PrettyPar({ score, par = 0, ...rest }) {
    const theme = useTheme();
    const color = score > par ? theme.palette.error.light : "text";
    const isOverPar = score > par;
    return (
        <Typography component="span" color={color} {...rest}>
            {score === par ? "E" : `${isOverPar ? "+" : ""}${score - par}`}
        </Typography>
    );
}
