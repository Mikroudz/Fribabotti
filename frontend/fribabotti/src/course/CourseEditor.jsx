import { StyledTextInput } from "#/components/Inputs";
import { StyledListItem } from "#/components/List";
import { SubmitButton } from "#/components/SubmitButton";
import { IncDecButton } from "#/game_session/PlayersScores";
import { Route as CourseRoute } from "#/routes/course.$courseId.index";

import { Route as CoursesMainRoute } from "#/routes/course.index";
import DeleteIcon from "@mui/icons-material/Delete";
import { createCourse } from "#/utils/api";
import {
    Box,
    IconButton,
    List,
    ListItemIcon,
    ListItemText,
    Stack,
    TextField,
    Typography,
} from "@mui/material";
import { useMutation } from "@tanstack/react-query";
import { useLocation, useNavigate } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import {
    useForm,
    FormProvider,
    useFieldArray,
    Controller,
    useFormContext,
    useWatch,
} from "react-hook-form";
import DeleteConfirmation from "#/components/SimpleDialog";

const FORM_DEFAULTS = {
    id: "",
    name: "",
    location: "",
    tracks: [],
};

function TrackAmountInput({ onChange }) {
    const [value, setValue] = useState(18);

    const trackFieldCount = useWatch({
        name: "tracks",
        defaultValue: [],
        compute: (val) => val.length,
    });

    useEffect(() => {
        // need to update value in some cases
        if (value !== "" && value !== trackFieldCount) {
            setValue(trackFieldCount);
        }
    }, [trackFieldCount]);

    const updateValue = (newValue) => {
        // Clamp values between min and max bounds
        const clampedValue = Math.max(1, Math.min(50, newValue));
        setValue(clampedValue);
        if (onChange) onChange(clampedValue);
    };

    const handleBlur = () => {
        // Re-verify min bound if left empty on blur
        if (value === "") {
            updateValue(1);
        }
    };

    const handleInputChange = (e) => {
        const val = parseInt(e.target.value, 10);
        if (!isNaN(val)) {
            updateValue(val);
        } else if (e.target.value === "") {
            // Allow user to temporarily clear the input to type
            setValue("");
        }
    };

    return (
        <TextField
            value={value}
            onChange={handleInputChange}
            onBlur={handleBlur}
            variant="outlined"
            label="Holes"
            slotProps={{
                htmlInput: {
                    style: { textAlign: "center" },
                },
            }}
            sx={{
                width: 65,
                "& input": {
                    padding: "4px 0",
                    fontWeight: "medium",
                    // Hide native browser spinner arrows
                    MozAppearance: "textfield",
                    "&::-webkit-outer-spin-button, &::-webkit-inner-spin-button": {
                        WebkitAppearance: "none",
                        margin: 0,
                    },
                },
                "& .MuiOutlinedInput-root": {
                    "& fieldset": {
                        borderColor: "divider",
                    },
                    "&:hover fieldset": {
                        borderColor: "blue",
                    },
                    "&.Mui-focused fieldset": {
                        borderColor: "secondary.500",
                    },
                },
            }}
        ></TextField>
    );
}

function TrackInput({ index }) {
    const { getValues, setValue, register } = useFormContext();

    const handleIncOrDec = (val) => {
        const oldVal = getValues(`tracks.${index}.par`);
        if (oldVal + val > 0) {
            setValue(`tracks.${index}.par`, oldVal + val, { shouldDirty: true });
        }
    };

    useEffect(() => {
        setValue(`tracks.${index}.track_number`, index + 1, { shouldDirty: true });
    }, [index, setValue]);

    return (
        <StyledListItem>
            <input type="hidden" {...register(`tracks.${index}.track_number`)} />
            <Typography
                component="span"
                sx={{
                    width: "36px",
                    alignContent: "center",
                    textAlign: "center",
                    bgcolor: "primary.300",
                    aspectRatio: "1/1",
                    borderRadius: "7px",
                    mr: 1,
                    ml: 1,
                    mt: 1,
                    mb: 1,
                }}
            >
                {index + 1}
            </Typography>
            <ListItemText
                primary={`Hole ${index + 1}`}
                slotProps={{ primary: { sx: { fontSize: "14px" } } }}
            ></ListItemText>
            <IncDecButton
                variant="contained"
                size="small"
                sx={{ minWidth: "32px", mr: 1, lineHeight: "1.2em" }}
                onClick={() => handleIncOrDec(-1)}
            >
                -
            </IncDecButton>
            <Controller
                name={`tracks.${index}.par`}
                render={({ field: { onChange, value, ref }, fieldState: { error } }) => (
                    <TextField
                        size="small"
                        slotProps={{
                            inputLabel: {
                                shrink: true,
                                sx: { "&.Mui-focused": { color: "secondary.500" } },
                            },
                        }}
                        label={`Par`}
                        variant="outlined"
                        value={value}
                        onChange={(e) => {
                            const rawValue = e.target.value;
                            const parsedValue = parseInt(rawValue, 10);
                            if (isNaN(parsedValue)) {
                                // allow empty
                                onChange("");
                            } else {
                                // Allow only numbers between 0-50
                                const clampedValue = Math.max(1, Math.min(50, parsedValue));
                                onChange(clampedValue);
                            }
                        }}
                        inputRef={ref}
                        error={!!error}
                        helperText={error?.message}
                        sx={{
                            width: "60px",
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
                        }}
                    />
                )}
            />
            <IncDecButton
                variant="contained"
                size="small"
                sx={{ minWidth: "32px", ml: 1, lineHeight: "1.2em" }}
                onClick={() => handleIncOrDec(+1)}
            >
                +
            </IncDecButton>
        </StyledListItem>
    );
}

function TotalParCount() {
    const total_par = useWatch({
        name: "tracks",
        defaultValue: [],
        compute: (fields) => fields.reduce((acc, val) => (val.par ? val.par + acc : acc), 0),
    });

    return (
        <Typography component="span" sx={{ pl: 1, fontSize: 14 }}>
            Total par {total_par}
        </Typography>
    );
}

function TrackEditor() {
    const { fields, replace } = useFieldArray({
        name: "tracks",
        rules: {
            required: true,
            validate: (val) => {
                if (val.length === 0) {
                    return "Course has no tracks";
                }
                return true;
            },
        },
    });
    const handleTrackAmountChange = (amount) => {
        //console.log(fields, amount);

        const oldSpliced = fields.slice(0, amount);
        const newFields = [
            ...oldSpliced,
            ...Array.from({ length: amount - oldSpliced.length }, () => ({ par: 3 })),
        ];

        replace(newFields);
    };

    return (
        <>
            <Typography>Track Holes</Typography>
            <Box>
                <TrackAmountInput onChange={handleTrackAmountChange} />
                <TotalParCount />
            </Box>
            <List>
                {fields.map((field, index) => {
                    return <TrackInput index={index} key={field.id} />;
                })}
            </List>
        </>
    );
}

function DeleteCourse({ onCourseDelete }) {
    const [open, setOpen] = useState(false);
    return (
        <>
            <IconButton sx={{ pt: 0, pr: 0 }} onClick={() => setOpen(true)}>
                <DeleteIcon sx={{ color: "white" }} />
            </IconButton>
            <DeleteConfirmation
                open={open}
                onClose={() => setOpen(false)}
                title={"Delete course"}
                contentText={"Do you want to delete this course permanently?"}
                onDelete={onCourseDelete}
            />
        </>
    );
}

export function CourseEditor({ course }) {
    const methods = useForm({
        defaultValues: FORM_DEFAULTS,
    });
    const { register, handleSubmit, reset } = methods;
    const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        //console.log(initialData);
        if (course) {
            if ("id" in course) {
                reset(course);
            }
        }
    }, [course]);

    const { mutate, isPending: isMutationPending } = useMutation({
        mutationFn: createCourse,
        onSuccess: async (data, variables, context) => {
            const { id: courseId } = data;
            console.log("success", data);
            let navigateTarget = { to: CoursesMainRoute.to, from: location.pathname };
            if ("id" in data) {
                navigateTarget = {
                    to: CourseRoute.to,
                    params: { courseId: courseId },
                    from: location.pathname,
                };
            }
            await navigate(navigateTarget);
        },
        onError: (e) => {
            console.log("mutation failed", e);
        },
    });

    const onSubmit = (data) => {
        console.log("submit called", data);

        const out = data;

        if (data.id === "") {
            const { id, ...newCourse } = out;
            mutate({ data: newCourse });
        } else {
            mutate({ data: out, method: "PATCH" });
        }
    };

    const handleDeleteCourse = () => {
        if (course) {
            mutate({ method: "DELETE", data: { id: course?.id } });
        }
    };

    return (
        <Box sx={{ p: 1 }}>
            <FormProvider {...methods}>
                <Stack
                    component="form"
                    onSubmit={handleSubmit(onSubmit)}
                    spacing={1}
                    sx={{ mb: 3 }}
                >
                    <Box
                        sx={{
                            display: "flex",
                            flexDirection: "row",
                            width: "100%",
                            justifyContent: "space-between",
                        }}
                    >
                        <Typography variant="h5" sx={{ pb: 1 }}>
                            {course ? "Editing Course" : "Creating Couse"}
                        </Typography>
                        {course && <DeleteCourse onCourseDelete={handleDeleteCourse} />}
                    </Box>
                    <input type="hidden" {...register("id")} />

                    <StyledTextInput
                        variant="outlined"
                        register={register}
                        field={{
                            required: "Course name required",
                            maxLength: { value: 128, message: "Course name too long" },
                        }}
                        name="name"
                        label={"Course Name"}
                        placeholder={"name"}
                        /*helperText={
                                getFieldState("description")?.description
                                    ? getFieldState("description")?.description?.message
                                    : null
                            }*/
                        sx={{ fontSize: "1.5em", width: "100%" }}
                    />

                    <StyledTextInput
                        variant="outlined"
                        register={register}
                        field={{
                            required: "Course location required",
                            maxLength: { value: 128, message: "Course location too long" },
                        }}
                        name="location"
                        label={"Course Location"}
                        placeholder={"Location"}
                        /*helperText={
                                getFieldState("description")?.description
                                    ? getFieldState("description")?.description?.message
                                    : null
                            }*/
                        sx={{ fontSize: "1.5em", width: "100%" }}
                    />

                    <TrackEditor />
                    <Box
                        sx={{ position: "fixed", left: 0, bottom: 62, width: "100%", pl: 1, pr: 1 }}
                    >
                        <SubmitButton
                            isSaved={isMutationPending}
                            isEditing={!course}
                            text={"Save"}
                            sx={{ width: "100%" }}
                        />
                    </Box>
                </Stack>
            </FormProvider>
        </Box>
    );
}
