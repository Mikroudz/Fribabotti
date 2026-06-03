import { Box, Typography, useTheme } from "@mui/material";
import { LineChart, XAxis, YAxis, Line, CartesianGrid, Tooltip, Legend } from "recharts";
import { PrettyPar } from "./PrettyPar";

function GameTooltip({ active, payload, label }) {
    const firstPayload = payload?.[0];
    const isVisible = active && firstPayload != null;

    return (
        <Box
            sx={{
                visibility: isVisible ? "visible" : "hidden",
                bgcolor: "primary.main",
                p: 1,
                pointerEvents: "auto",
                borderRadius: "6px",
            }}
        >
            {isVisible && (
                <>
                    <Typography>Hole {payload?.[0]?.payload?.track_number}</Typography>
                    <PrettyPar score={payload?.[0]?.payload?.user_avg} wrap={false}></PrettyPar>
                </>
            )}
        </Box>
    );
}

export function AverageChart({ data }) {
    const theme = useTheme();

    return (
        <LineChart
            style={{
                width: "350px",
                height: "100%",
                minWidth: "300px",
                minHeight: "400px",
            }}
            responsive
            data={data}
            margin={{
                top: 5,
                right: 0,
                left: 0,
                bottom: 5,
            }}
        >
            <CartesianGrid strokeDasharray="3 3" stroke="#8f8f8f" vertical={false} />

            <XAxis
                dataKey="track_number"
                stroke="white"
                type="category"
                axisLine={false}
                tickLine={false}
                tickMargin={5}
                minTickGap={5}
            />
            <YAxis
                width="auto"
                stroke="white"
                type="number"
                dataKey="user_avg"
                axisLine={false}
                tickLine={false}
            />
            <Legend />
            <Tooltip content={<GameTooltip />} />

            <Line
                type="monotone"
                dataKey="user_avg"
                stroke={theme.palette.secondary.main}
                name="Average vsPar"
                strokeWidth={2}
                dot={{
                    fill: theme.palette.secondary.main,
                }}
                activeDot={{ r: 8, stroke: "white" }}
            />
        </LineChart>
    );
}
