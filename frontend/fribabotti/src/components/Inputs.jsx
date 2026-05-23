import { Input, TextField } from "@mui/material";

export function StyledTextInput({ label, register, field, name, placeholder, sx, ...rest }) {
    return (
        <TextField
            {...register(name, field)}
            id={`${name}-input`}
            label={label}
            placeholder={placeholder}
            autoComplete="off"
            slotProps={{
                inputLabel: {
                    sx: { "&.Mui-focused": { color: "secondary.500" } },
                },
            }}
            sx={{
                bgcolor: "background.paper",
                "& .MuiOutlinedInput-root": {
                    "& fieldset": {
                        borderColor: "divider",
                    },
                    "&:hover fieldset": {
                        borderColor: "divider",
                    },
                    "&.Mui-focused fieldset": {
                        borderColor: "secondary.500",
                    },
                },
                ...sx,
            }}
            {...rest}
        ></TextField>
    );
}
