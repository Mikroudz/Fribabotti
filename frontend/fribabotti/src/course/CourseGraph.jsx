import { getCourseHistoryStats } from "#/utils/api";
import { Box, Link as MuiLink, Typography, useMediaQuery } from "@mui/material";
import { useQuery, useSuspenseQuery } from "@tanstack/react-query";
import { Link, useParams, useRouter } from "@tanstack/react-router";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from "recharts";
import OpenInNewIcon from "@mui/icons-material/OpenInNew";
import { Route as GameSessionRoute } from "#/routes/gamesession_/$gameSessionId/gamesession";
import { PrettyPar } from "#/components/PrettyPar";
import { courseGraphQueryOptions } from "#/hooks/GameSessionHooks";

const formatXAxis = (tickItem) => {
    return new Date(tickItem).toLocaleDateString("fi-FI", {
        month: "short",
        day: "numeric",
    }); // Output example: "Jun 1"
};

function GameTooltip({ active, payload, label }) {
    const firstPayload = payload?.[0];
    const isVisible = active && firstPayload != null;
    const timeLabel = new Date(label).toLocaleDateString("fi-FI", {
        month: "short",
        day: "numeric",
    });
    const isTouchScreen = useMediaQuery("(pointer: coarse)");
    return (
        <Box
            sx={{
                visibility: isVisible ? "visible" : "hidden",
                bgcolor: "primary.main",
                p: 1,
                pointerEvents: "auto",
            }}
        >
            {isVisible && (
                <>
                    <PrettyPar score={payload?.[0]?.payload?.score} wrap={false}></PrettyPar>
                    <br />
                    <MuiLink
                        component={Link}
                        to={GameSessionRoute.to}
                        params={{ gameSessionId: payload?.[0]?.payload?.id }}
                        from=""
                        sx={{ color: "text.primary" }}
                    >
                        {timeLabel} <OpenInNewIcon sx={{ fontSize: "13px" }} />
                    </MuiLink>
                </>
            )}
        </Box>
    );
}

function Graph({ data }) {
    return (
        <LineChart
            key={data?.length}
            style={{
                width: "100%",
                maxWidth: "700px",
                height: "100%",
                minWidth: "300px",
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
                dataKey="started_at"
                stroke="white"
                type="category"
                tickFormatter={formatXAxis}
            />
            <YAxis width="auto" stroke="white" type="number" dataKey="score" />
            <Tooltip content={GameTooltip} />
            <Legend />
            <Line
                type="monotone"
                dataKey="score"
                stroke="white"
                dot={{
                    fill: "white",
                }}
                activeDot={{ r: 8, stroke: "white" }}
            />
        </LineChart>
    );
}

export function CourseGraph() {
    const { courseId } = useParams({ strict: false });

    const { data: course } = useSuspenseQuery(courseGraphQueryOptions(courseId));

    return (
        <Box sx={{ p: 1, width: "100%", minWidth: "300px" }}>
            <Typography variant="h5">{course?.name}</Typography>
            <Box sx={{ height: "500px", width: "100%", minWidth: "300px" }}>
                <Graph
                    data={course?.user_past_rounds?.map((val) => ({
                        ...val,
                        score: val.score - course?.par,
                    }))}
                />
            </Box>
        </Box>
    );
}
