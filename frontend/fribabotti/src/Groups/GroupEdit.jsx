import { StyledTextInput } from "#/components/Inputs";
import { SubmitButton } from "#/components/SubmitButton";
import { Route as GroupRoute } from "#/routes/groups/$groupId.index";

import { createGroup } from "#/utils/api";
import { CheckBox } from "@mui/icons-material";
import { Box, Checkbox, FormControlLabel, Stack, Typography } from "@mui/material";
import { useMutation } from "@tanstack/react-query";
import { useLocation, useNavigate } from "@tanstack/react-router";
import { useEffect } from "react";
import { useForm, FormProvider, Controller } from "react-hook-form";

const FORM_DEFAULTS = {
    id: "",
    name: "",
    reset_invite: false,
};

// not sure if session creation should be different from editing?
export function EditGroup({ group = null }) {
    const methods = useForm({
        defaultValues: FORM_DEFAULTS,
    });

    const { register, handleSubmit, reset } = methods;
    const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        //console.log(initialData);
        if (group) {
            if ("id" in group) {
                reset(group);
            }
        }
    }, [group]);

    const { mutate, isPending: isMutationPending } = useMutation({
        mutationFn: createGroup,
        onSuccess: async (data, variables, context) => {
            const { id: group_id } = data;
            console.log("success", data);
            const navigateTarget = {
                to: GroupRoute.to,
                from: location.pathname,
                params: { groupId: group_id },
            };
            await navigate(navigateTarget);
        },
        onError: (e) => {
            console.log("mutation failed", e);
        },
    });

    const onSubmit = (data) => {
        const out = Object.fromEntries(
            Object.entries(data).filter(([key]) => Object.keys(FORM_DEFAULTS).includes(key)),
        );
        console.log("submit called", out);

        if (out.id === "") {
            const { id, ...newGroup } = out;
            mutate({ data: newGroup });
        } else {
            mutate({ data: out, method: "PATCH" });
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
                            {group ? "Editing Group" : "Creating New Group"}
                        </Typography>
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
                        label={"Group Name"}
                        placeholder={"name"}
                        /*helperText={
                                getFieldState("description")?.description
                                    ? getFieldState("description")?.description?.message
                                    : null
                            }*/
                        sx={{ fontSize: "1.5em", width: "100%" }}
                    />
                    <Controller
                        name="reset_invite"
                        render={({ field: { value, onChange, ...field } }) => (
                            <FormControlLabel
                                label="Reset Group Invite Code"
                                control={
                                    <Checkbox
                                        {...field}
                                        checked={!!value} // Maps the form state to MUI's checked prop
                                        onChange={(e) => onChange(e.target.checked)} // Sends boolean back to RHF
                                    />
                                }
                            />
                        )}
                    />

                    <Box
                        sx={{ position: "fixed", left: 0, bottom: 62, width: "100%", pl: 1, pr: 1 }}
                    >
                        <SubmitButton
                            isSaved={isMutationPending}
                            isEditing={!group}
                            text={"Save"}
                            sx={{ width: "100%" }}
                        />
                    </Box>
                </Stack>
            </FormProvider>
        </Box>
    );
}
