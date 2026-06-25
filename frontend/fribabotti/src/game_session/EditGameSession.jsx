import { SubmitButton } from "#/components/SubmitButton";
import { Route as GamesessionRoute } from "#/routes/gamesession_/$gameSessionId/gamesession";

import { createGameSession } from "#/utils/api";
import { Autocomplete, Box, Stack, TextField, Typography } from "@mui/material";
import { useMutation } from "@tanstack/react-query";
import { useLocation, useNavigate } from "@tanstack/react-router";
import { useEffect } from "react";
import { useForm, FormProvider, Controller, useFormContext } from "react-hook-form";
import { useCourses } from "#/hooks/GameSessionHooks";
import { useUserGroups } from "#/hooks/ProfileHooks";

const FORM_DEFAULTS = {
    id: "",
    course_id: "",
    user_group_id: "",
    participants: [],
};

function SelectCourse({ initialData }) {
    const { data: courses } = useCourses();
    const selectValues = courses.map((course) => ({ label: course.name, id: course.id }));
    const { setValue } = useFormContext();

    useEffect(() => {
        if (selectValues && initialData && Object.hasOwn(initialData, "course_id")) {
            const idx = selectValues.findIndex((val) => val.id === initialData.course_id);
            if (idx !== -1) {
                setValue("course_id", selectValues[idx]);
            }
        }
    }, [selectValues]);
    return (
        <Controller
            name="course_id"
            rules={{ required: "Please select a course" }}
            render={({ field: { onChange, value, ref } }) => (
                <Autocomplete
                    options={selectValues}
                    // Tells MUI how to display the text label for an option object
                    getOptionLabel={(option) => option.label || ""}
                    // Strict check to determine if an option matches the currently selected value
                    isOptionEqualToValue={(option, value) => option.id === value?.id}
                    value={value}
                    // Forwards updates cleanly back to React Hook Form state
                    onChange={(event, newValue) => {
                        onChange(newValue);
                    }}
                    renderInput={(params) => (
                        <TextField
                            {...params}
                            label="Select Course"
                            inputRef={ref} // Forwards the focus ref if validation fails
                        />
                    )}
                />
            )}
        />
    );
}

function SelectGroup() {
    const { data: groups } = useUserGroups();
    const selectValues = groups.map((group) => ({ label: group.name, id: group.id }));
    // todo: say to user that there are no groups and forward to group creation
    return (
        <Controller
            name="user_group_id"
            rules={{ required: "Please select a group" }}
            render={({ field: { onChange, value, ref } }) => (
                <Autocomplete
                    options={selectValues}
                    // Tells MUI how to display the text label for an option object
                    getOptionLabel={(option) => option.label || ""}
                    // Strict check to determine if an option matches the currently selected value
                    isOptionEqualToValue={(option, value) => option.id === value?.id}
                    value={value}
                    // Forwards updates cleanly back to React Hook Form state
                    onChange={(event, newValue) => {
                        onChange(newValue);
                    }}
                    renderInput={(params) => (
                        <TextField
                            {...params}
                            label="Select Group"
                            inputRef={ref} // Forwards the focus ref if validation fails
                        />
                    )}
                />
            )}
        />
    );
}

// not sure if session creation should be different from editing?
export function EditGameSession({ gameSession }) {
    const methods = useForm({
        defaultValues: FORM_DEFAULTS,
    });
    const { register, handleSubmit, reset } = methods;
    const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        //console.log(initialData);
        if (gameSession) {
            if ("id" in gameSession) {
                reset(gameSession);
            }
        }
    }, [gameSession]);

    const { mutate, isPending: isMutationPending } = useMutation({
        mutationFn: createGameSession,
        onSuccess: async (data, variables, context) => {
            const { id: gamesessionId } = data;
            console.log("success", data);
            let navigateTarget = {
                to: GamesessionRoute.to,
                from: location.pathname,
                params: { gameSessionId: gamesessionId },
            };
            await navigate(navigateTarget);
        },
        onError: (e) => {
            console.log("mutation failed", e);
        },
    });

    const onSubmit = (data) => {
        console.log("submit called", data);

        let { user_group_id, course_id, ...out } = data;
        if (data.user_group_id) {
            if (Object.hasOwn(data.user_group_id, "id")) {
                out["user_group_id"] = data.user_group_id.id;
            }
        }
        if (data.course_id) {
            if (Object.hasOwn(data.course_id, "id")) {
                out["course_id"] = data.course_id.id;
            }
        }
        console.log("submit called", out);

        if (data.id === "") {
            const { id, ...newGameSession } = out;
            mutate({ data: newGameSession });
        } else {
            mutate({ data: out, method: "PATCH" });
        }
    };

    const handleDeleteCourse = () => {
        if (gameSession) {
            mutate({ method: "DELETE", data: { id: gameSession?.id } });
        }
    };

    return (
        <Box sx={{ p: 1 }}>
            <FormProvider {...methods}>
                <Stack component="form" onSubmit={handleSubmit(onSubmit)} spacing={1} sx={{ mb: 3 }}>
                    <Box
                        sx={{
                            display: "flex",
                            flexDirection: "row",
                            width: "100%",
                            justifyContent: "space-between",
                        }}
                    >
                        <Typography variant="h5" sx={{ pb: 1 }}>
                            Creating New Game
                        </Typography>
                    </Box>
                    <input type="hidden" {...register("id")} />
                    <SelectCourse initialData={gameSession} />
                    <SelectGroup />

                    <Box sx={{ position: "fixed", left: 0, bottom: 62, width: "100%", pl: 1, pr: 1 }}>
                        <SubmitButton
                            isSaved={isMutationPending}
                            isEditing={!gameSession}
                            text={"Start game!"}
                            sx={{ width: "100%" }}
                        />
                    </Box>
                </Stack>
            </FormProvider>
        </Box>
    );
}
