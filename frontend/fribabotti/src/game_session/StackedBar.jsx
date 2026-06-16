import { getScoreColor } from "#/components/PrettyPar";
import { Box, useTheme } from "@mui/material";

export function groupScores(scores) {
    const countedScores = scores
        .filter((val) => val.score !== 0)
        .reduce((acc, val) => {
            const vsPar = val.score - val.par;
            if (acc[vsPar]) {
                acc[vsPar]++;
            } else {
                acc[vsPar] = 1;
            }
            return acc;
        }, {});
    const countTotal = Object.values(countedScores).reduce((sum, val) => sum + val, 0);
    return [countedScores, countTotal];
}

export function StackedBarChart({ scores }) {
    const theme = useTheme();
    if (!scores || !Array.isArray(scores)) {
        return null;
    }
    const [countedScores, countTotal] = groupScores(scores);
    return (
        <Box
            sx={{
                display: "flex",
                overflow: "hidden",
                height: "24px",
                width: "100%",
                m: 0.5,
                ml: 0,
                pl: 0,
                pr: 0.5,
            }}
        >
            {Object.keys(countedScores)
                .sort((a, b) => a - b)
                .map((val) => (
                    <Box
                        key={`bar-${val}`}
                        sx={{
                            height: "100%",
                            flex: countedScores[val] / countTotal,
                            bgcolor: getScoreColor(val, theme.palette),
                            textAlign: "right",
                            alignContent: "center",
                            pr: 0.5,
                        }}
                    >
                        {countedScores[val]}
                    </Box>
                ))}
        </Box>
    );
}
