import { createTheme, ThemeProvider } from "@mui/material/styles";
import { createContext } from "react";

const primaryShades = {
    1000: "#FFFFFF",
    950: "#BFFFDA",
    900: "#92F7C3",
    800: "#75DAA8",
    700: "#59BE8E",
    600: "#3BA275",
    500: "#15885D",
    400: "#006C48",
    300: "#005235",
    200: "#003823",
    100: "#002113",
    0: "#000000",
};

const secondaryShades = {
    1000: "#FFFFFF",
    950: "#FFEDE3",
    900: "#FFDCC3",
    800: "#FFB77D",
    700: "#FF8E13",
    600: "#DA7700",
    500: "#B56200",
    400: "#904D00",
    300: "#6E3900",
    200: "#4D2600",
    100: "#2F1500",
    0: "#000000",
};

const themeOptions = {
    palette: {
        type: "dark",
        primary: {
            main: "#243b2b",
            ...primaryShades,
        },
        secondary: {
            main: "#FF8C00",
            ...secondaryShades,
        },
        background: {
            default: "#0f150f",
            paper: "#1b211b",
        },
        text: {
            primary: "#dee4da",
            secondary: "rgba(222,228,218,0.7)",
            disabled: "rgba(222,228,218,0.5)",
            hint: "rgba(222,228,218,0.5)",
        },
        divider: "#48504a",
    },
    typography: {
        fontFamily: '"Lexend Variable", sans-serif',
        fontSize: 14,
        h2: {
            fontSize: "2.2rem",
        },
        h1: {
            fontSize: "3.3rem",
        },
        h3: {
            fontSize: "1.8rem",
            lineHeight: 1.14,
        },
        h4: {
            fontSize: "1.6rem",
        },
        h5: {
            fontSize: "1.3rem",
        },
    },
};

const ColorModeContext = createContext({ toggleColorMode: () => {} });

function MuiTheme({ children }) {
    const theme = createTheme(themeOptions);

    return (
        <ColorModeContext.Provider value={null}>
            <ThemeProvider theme={theme} noSsr defaultMode="dark">
                {children}
            </ThemeProvider>
        </ColorModeContext.Provider>
    );
}

export default MuiTheme;
