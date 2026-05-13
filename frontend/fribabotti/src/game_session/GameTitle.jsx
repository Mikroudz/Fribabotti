import { dateTimeNice } from "#/utils/helpers";
import { Box, Typography, useTheme } from "@mui/material";
import { StackedBarChart } from "./StackedBar";

export function GameTitleInformation() {
    const data = {
        started_at: Date.now(),
        course_name: "Meri-Toppila Frisbeegolf",
        par: 54,
        score: 62,
    };

    return (
        <Box
            sx={{
                display: "flex",
                flexDirection: "column",
                m: 1,
                p: 1,
                alignItems: "center",
                bgcolor: "background.paper",
                border: "1px solid",
                borderColor: "divider",
                borderRadius: "7px",
            }}
        >
            <Typography component="span" variant="h4">
                Round
            </Typography>
            <Typography component="span">Meri-Toppila Frisbeegolf</Typography>
            <Typography component="span" sx={{ color: "text.secondary", fontSize: "14px" }}>
                {dateTimeNice(Date.now())}
            </Typography>
            <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
                <Typography component="span" variant="h6">
                    Total
                </Typography>

                <Typography component="span" variant="h6">
                    -6
                </Typography>
            </Box>
            <Box sx={{ display: "flex", flexDirection: "row", gap: 1 }}>
                <Typography component="span" sx={{ textAlign: "center" }}>
                    Par <br /> 51
                </Typography>
                <Typography component="span" sx={{ textAlign: "center" }}>
                    Score <br />
                    45
                </Typography>
                <Typography component="span" sx={{ textAlign: "center" }}>
                    Birdie <br />6
                </Typography>
            </Box>
            <StackedBarChart />
        </Box>
    );
}
