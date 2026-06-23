import { List, ListItem, ListItemAvatar, ListItemText, Skeleton } from "@mui/material";

export default function ListSkeletonLoader({ count = 5 }) {
    return (
        <List>
            {Array.from(new Array(count)).map((_, index) => (
                <ListItem key={index} disableGutters>
                    <ListItemAvatar>
                        <Skeleton animation="wave" variant="circular" width={40} height={40} />
                    </ListItemAvatar>

                    <ListItemText
                        primary={
                            <Skeleton
                                animation="wave"
                                variant="text"
                                width="60%"
                                height={20}
                                style={{ marginBottom: 6 }}
                            />
                        }
                        secondary={<Skeleton animation="wave" variant="text" width="40%" height={15} />}
                    />
                </ListItem>
            ))}
        </List>
    );
}
