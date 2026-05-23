import { Box, Button } from "@mui/material";
import SaveAsIcon from "@mui/icons-material/SaveAs";
import { useFormState } from "react-hook-form";

export function SubmitButton({ isSaved, isEditing, text, sx, ...rest }) {
    const { isDirty, isValid } = useFormState();
    return (
        <Button
            type="submit"
            disabled={!(isDirty && isValid) || isSaved}
            sx={{
                bgcolor: "secondary.600",
                "&.Mui-disabled": {
                    bgcolor: "secondary.300",
                },
                ...sx,
            }}
            startIcon={<SaveAsIcon />}
            variant="contained"
            {...rest}
        >
            {text}
        </Button>
    );
}
