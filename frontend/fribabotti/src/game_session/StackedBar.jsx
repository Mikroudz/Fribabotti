import { Box, useTheme } from "@mui/material";

export function StackedBarChart() {
    const data = [
        { score: 0, count: 4 },
        { score: -1, count: 4 },
        { score: 1, count: 3 },
        { score: 2, count: 3 },
    ];
    const counTotal = data.reduce((sum, val) => sum + val.count, 0);
    const theme = useTheme();

    const colorMap = {
        "-1": theme.palette.primary[400],
        0: "",
        1: theme.palette.primary[600],
        2: theme.palette.primary[700],
    };

    return (
        <Box
            sx={{
                display: "flex",
                overflow: "hidden",
                height: "24px",
                width: "100%",
                m: 0.5,
                pl: 0.5,
                pr: 0.5,
            }}
        >
            {data
                .sort((a, b) => a.score - b.score)
                .map((val, idx) => (
                    <Box
                        key={`bar-${idx}`}
                        sx={{
                            height: "100%",
                            flex: val.count / counTotal,
                            bgcolor: colorMap[val.score],
                            textAlign: "right",
                            alignContent: "center",
                        }}
                    >
                        {val.count}
                    </Box>
                ))}
        </Box>
    );
}
