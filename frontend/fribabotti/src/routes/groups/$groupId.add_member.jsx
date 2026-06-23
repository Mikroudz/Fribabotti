import { createGuestUser } from "#/utils/api";
import { Box, Stack, Typography } from "@mui/material";
import { useMutation } from "@tanstack/react-query";
import { createFileRoute, useNavigate, useParams } from "@tanstack/react-router";
import { FormProvider, useForm } from "react-hook-form";
import { Route as GroupRoute } from "#/routes/groups/$groupId.index";
import { StyledTextInput } from "#/components/Inputs";
import { SubmitButton } from "#/components/SubmitButton";

export const Route = createFileRoute("/groups/$groupId/add_member")({
    component: RouteComponent,
});

const FORM_DEFAULTS = { username: "", user_group_id: null };

function RouteComponent() {
    const params = useParams({ strict: false });
    const { groupId } = params;
    const navigate = useNavigate();
    const methods = useForm({
        defaultValues: FORM_DEFAULTS,
    });
    const { register, handleSubmit, reset } = methods;

    const { mutate, isPending: isMutationPending } = useMutation({
        mutationFn: createGuestUser,
        onSuccess: async (data, variables, context) => {
            console.log("success", data);
            const navigateTarget = {
                to: GroupRoute.to,
                from: location.pathname,
                params: { groupId },
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
        out["user_group_id"] = groupId;
        console.log("submit called", out);

        mutate({ data: out });
    };

    return (
        <Box sx={{ p: 1 }}>
            <Typography>Create dummy user to group</Typography>
            <Typography variant="caption">If you want to add existing users, use invite links.</Typography>
            <FormProvider {...methods}>
                <Stack component="form" onSubmit={handleSubmit(onSubmit)} spacing={1} sx={{ mb: 3, mt: 2 }}>
                    <input type="hidden" {...register("user_group_id")} />

                    <StyledTextInput
                        variant="outlined"
                        register={register}
                        field={{
                            required: "User name required",
                            maxLength: { value: 128, message: "User name too long" },
                        }}
                        name="username"
                        label={"Guest User Name"}
                        placeholder={"Username"}
                        sx={{ fontSize: "1.5em", width: "100%" }}
                    />

                    <Box sx={{ position: "fixed", left: 0, bottom: 62, width: "100%", pl: 1, pr: 1 }}>
                        <SubmitButton
                            isSaved={isMutationPending}
                            isEditing={false}
                            text={"Create"}
                            sx={{ width: "100%" }}
                        />
                    </Box>
                </Stack>
            </FormProvider>
            <Typography>
                Guest users can be used in place of real users in game sessions. Guest user is managed by the
                creator.
            </Typography>
        </Box>
    );
}
