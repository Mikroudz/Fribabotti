import { courseGraphQueryOptions } from "#/hooks/GameSessionHooks";
import { InfoBox } from "#/routes/profile";
import { getTrackHistoryStats } from "#/utils/api";
import { Box, MenuItem, Select, Typography, useTheme } from "@mui/material";
import { useQuery, useSuspenseQuery } from "@tanstack/react-query";
import { useTags } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import {
    Label,
    ReferenceArea,
    ReferenceDot,
    Scatter,
    ScatterChart,
    Tooltip,
    useXAxisScale,
    useYAxisScale,
    XAxis,
    YAxis,
} from "recharts";

const coordsToMeters = (lat, lng) => {
    return {
        x: lng * 111320 * Math.cos(lat * (Math.PI / 180)),
        y: lat * 111320,
    };
};

const rotPoint = (p, angle) => ({
    x: p.x * Math.cos(angle) - p.y * Math.sin(angle),
    y: p.x * Math.sin(angle) - p.y * Math.cos(angle),
});

const HalfCircleDot = (props) => {
    const { cx, cy, fill, stroke, rx, ry } = props;
    const pathData = `
    M ${cx - (rx - cx)} ${cy}
    A ${rx - cx} ${cy - ry} 0 0 1 ${rx} ${cy}
    Z
  `;

    return <path d={pathData} fill={fill} stroke={stroke} />;
};

function DistanceMarkers() {
    const xScale = useXAxisScale();
    const yScale = useYAxisScale();

    if (!xScale || !yScale) return null;
    return [20, 40, 60, 80, 100].map((radius) => (
        <ReferenceDot
            key={radius}
            x={0}
            y={0}
            rx={xScale(radius)}
            ry={yScale(radius)}
            fill="none"
            stroke="grey"
            shape={HalfCircleDot}
        >
            <Label
                position="inside"
                content={
                    <RenderOuterRimLabel value={`${radius}m`} cy={yScale(radius)} cx={xScale(0)} />
                } // Injecting the custom label renderer
            />
        </ReferenceDot>
    ));
}

const RenderOuterRimLabel = (props) => {
    const { cx, cy, value } = props;
    // Define the angle in radians (e.g., 45 degrees for top-right)

    // Calculate coordinates right on the outer rim (plus a 5px padding)

    return (
        <text
            x={cx}
            y={cy}
            fill="#a3a3a3"
            fontSize={12}
            dominantBaseline="central"
            textAnchor="middle"
        >
            {value}
        </text>
    );
};

function SelectHole({ course_id, onSelected, value }) {
    const { data: course } = useSuspenseQuery(courseGraphQueryOptions(course_id));

    return (
        <Select
            variant="standard"
            value={value ?? ""}
            onChange={(e) => onSelected(e.target.value)}
            renderValue={(val) => (
                <Typography sx={{ color: "text.secondary" }}>{`Hole ${val}`}</Typography>
            )}
            sx={{
                "& .MuiSelect-icon": {
                    color: "text.secondary",
                },
            }}
            MenuProps={{
                anchorOrigin: {
                    vertical: "bottom",
                    horizontal: "right",
                },
                transformOrigin: {
                    vertical: "top",
                    horizontal: "left",
                },
            }}
        >
            {course?.tracks?.map((val) => (
                <MenuItem
                    selected={value === val}
                    key={val}
                    value={val}
                    sx={{
                        "&.Mui-selected": {
                            bgcolor: "primary.400",
                        },
                    }}
                >{`Hole ${val}`}</MenuItem>
            ))}
        </Select>
    );
}

export function CourseTrackScatter({ course_id }) {
    const [selectedHole, setSelectedHole] = useState(1);
    const theme = useTheme();

    const { data: holeData } = useQuery({
        queryFn: getTrackHistoryStats,
        queryKey: ["COURSE_HISTORY_STATS", course_id, selectedHole],
    });

    const [scaledData, hole_pos, throw_avg, longest_throw] = useMemo(() => {
        if (!holeData) return [];
        const tee_meters_y = holeData.tee_lat * 111320;
        const tee_meters_x =
            holeData.tee_lng * (111320 * Math.cos(holeData.tee_lat * (Math.PI / 180)));
        const basket = coordsToMeters(holeData.basket_lat, holeData.basket_lng);
        // todo: calculate z score filtering or just remove over 100 meters from average
        const points = holeData?.throws?.map((val) => {
            const c = coordsToMeters(val.lat, val.lng);
            return { x: c.x - tee_meters_x, y: c.y - tee_meters_y };
        });

        const avg_throws = points.reduce(
            (acc, val, _, arr) => {
                acc.x += val.x / arr.length;
                acc.y += val.y / arr.length;
                return acc;
            },
            { x: 0, y: 0 },
        );

        const angle_to_rotate_rad = Math.atan2(avg_throws.x, avg_throws.y);

        const points_rotated = points.map((p) => rotPoint(p, angle_to_rotate_rad));
        const idxLargest = points_rotated
            .map((p) => Math.pow(p.x, 2) + Math.pow(p.y, 2))
            .reduce((maxId, val, idx, array) => (val > array[maxId] ? idx : maxId), 0);

        return [
            points_rotated,
            rotPoint(
                { x: basket.x - tee_meters_x, y: basket.y - tee_meters_y },
                angle_to_rotate_rad,
            ),
            rotPoint(avg_throws, angle_to_rotate_rad),
            points_rotated[idxLargest],
        ];
    }, [holeData]);

    return (
        <>
            <ScatterChart
                style={{
                    width: "100%",
                    maxWidth: "700px",
                    height: "500px",
                    minWidth: "300px",
                }}
                responsive
                margin={{
                    top: 5,
                    right: 0,
                    left: 0,
                    bottom: 5,
                }}
            >
                <Scatter
                    activeShape={{ fill: "red" }}
                    data={scaledData}
                    fill={theme.palette.secondary.main}
                />
                <XAxis dataKey="x" type="number" name="M" />
                <YAxis
                    dataKey="y"
                    type="number"
                    width="auto"
                    axisLine={false}
                    tickLine={false}
                    name="M"
                />
                <ReferenceArea x1={-1} x2={1} y1={0} y2={3} fill="green" stroke="green" />
                <ReferenceDot {...hole_pos} r={3} fill="red" stroke="none" />
                <ReferenceDot {...throw_avg} r={3} fill="green" stroke="none" label="Avg" />
                <DistanceMarkers />
            </ScatterChart>
            <Box sx={{ display: "flex", flexDirection: "row", alignContent: " start" }}>
                <Box>
                    <SelectHole
                        course_id={course_id}
                        onSelected={setSelectedHole}
                        value={selectedHole}
                    />
                </Box>
                <InfoBox
                    title="Longest"
                    value={`${Math.sqrt(
                        Math.pow(longest_throw?.x, 2) + Math.pow(longest_throw?.y, 2),
                    ).toFixed(1)}m`}
                />
            </Box>
        </>
    );
}
