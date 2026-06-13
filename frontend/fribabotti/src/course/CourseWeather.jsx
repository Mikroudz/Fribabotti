import { Box, Typography } from "@mui/material";
import NorthIcon from "@mui/icons-material/North";
import { useQuery } from "@tanstack/react-query";
import { getWeather } from "#/utils/api";
import {
    WiDaySunny,
    WiDayCloudy,
    WiCloudy,
    WiDayShowers,
    WiShowers,
    WiSprinkle,
    WiRain,
    WiDaySnow,
    WiSnow,
    WiSnowWind,
    WiStormShowers,
    WiThunderstorm,
    WiDaySleet,
    WiSleet,
    WiFog,
} from "weather-icons-react";

const SYMBOLS = {
    1: WiDaySunny,
    2: WiDayCloudy,
    3: WiCloudy,
    21: WiDayShowers,
    22: WiShowers,
    23: WiRain,
    31: WiSprinkle,
    32: WiRain,
    33: WiRain,
    41: WiDaySnow,
    42: WiSnow,
    43: WiSnowWind,
    51: WiSnow,
    52: WiSnow,
    53: WiSnowWind,
    61: WiStormShowers,
    62: WiStormShowers,
    63: WiThunderstorm,
    64: WiThunderstorm,
    71: WiDaySleet,
    72: WiSleet,
    73: WiSleet,
    81: WiSleet,
    82: WiSleet,
    83: WiSleet,
    91: WiFog,
    92: WiFog,
};

export function CourseWeather({ course_id }) {
    const { data } = useQuery({
        queryKey: ["COURSE_WEATHER", course_id],
        queryFn: getWeather,
        staleTime: 60 * 60 * 1000,
        gcTime: 60 * 60 * 1000,
    });
    const WeatherIcon = SYMBOLS[data?.weather_code] || WiDaySunny;
    if (data?.temperature_c === null) return null;
    return (
        <>
            <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
                <Typography component="span" sx={{ fontSize: "28px", lineHeight: 1, mt: "-6px" }}>
                    <WeatherIcon />
                </Typography>
                <Typography component="span" sx={{ fontSize: "13px" }}>
                    {data?.temperature_c?.toFixed(1)} °C
                </Typography>
            </Box>
            <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
                <Typography component="span">
                    <NorthIcon
                        sx={{
                            fontSize: "20px",
                            transform: `rotate(${data?.wind_direction_deg}deg)`,
                        }}
                    />
                </Typography>
                <Typography component="span" sx={{ fontSize: "13px" }}>
                    {data?.wind_speed_ms?.toFixed(1)} m/s
                </Typography>
            </Box>
        </>
    );
}
