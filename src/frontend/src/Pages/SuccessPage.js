import * as React from 'react';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import ListItemAvatar from '@mui/material/ListItemAvatar';
import Avatar from '@mui/material/Avatar';
import ImageIcon from '@mui/icons-material/Image';
import PersonIcon from '@mui/icons-material/Person';
import CakeIcon from '@mui/icons-material/Cake';
import BadgeIcon from '@mui/icons-material/Badge';
import Grid from '@mui/material/Grid';
import { useLocation } from 'react-router-dom'
import Paper from '@mui/material/Paper';
import Card from '@mui/material/Card';
import CardMedia from '@mui/material/CardMedia';
import Title from '../Components/PageTitle';
import StyledButton from '../Components/ButtonTheme';


const SuccessPage = () => {
    const location = useLocation()
    const { userName } = location.state
    const { imageId } = location.state
    const { label } = location.state
    const { lName } = location.state
    const { fName } = location.state
    const { age } = location.state
    const { pic } = localStorage.getItem("pic")
    console.log(location.state)

    return (
        <>
          <Title pagetitle={label}  />
                <Grid
                    container
                    direction="column"
                    justifyContent="center"
                    alignItems="center"
                >
                    <Grid>
                        <img src={localStorage.getItem('pic')} 
                        alt={imageId}
                        />
                    {pic &&
                        <Card sx={{ maxWidth: 345 }}>
                        <CardMedia
                            component="img"
                            // height="194"
                            image={pic}
                            alt={imageId}
                        />
                    </Card>
                        }
                    </Grid>

                    <Grid item xs={10} sx={{pt:2}}>
                        <div>
                    <Paper elevation={4}>
                    <List sx={{ width: '100%', maxWidth: 360, bgcolor: 'background.paper' }}>
                        {userName &&
                            <ListItem>
                                <ListItemAvatar>
                                    <Avatar>
                                        <PersonIcon />
                                    </Avatar>
                                </ListItemAvatar>
                                <ListItemText primary={userName} />
                            </ListItem>
                        }
                        {fName &&
                            <ListItem>
                                <ListItemAvatar>
                                    <Avatar>
                                        <BadgeIcon />
                                    </Avatar>
                                </ListItemAvatar>
                                <ListItemText primary={fName} />
                            </ListItem>
                        }
                        {lName &&
                            <ListItem>
                                <ListItemAvatar>
                                    <Avatar>
                                        <BadgeIcon />
                                    </Avatar>
                                </ListItemAvatar>
                                <ListItemText primary={lName} />
                            </ListItem>
                        }
                        {age &&
                            <ListItem>
                                <ListItemAvatar>
                                    <Avatar>
                                        <CakeIcon />
                                    </Avatar>
                                </ListItemAvatar>
                                <ListItemText primary={age} />
                            </ListItem>
                        }
                    </List>
                    
                    
                {userName && imageId &&
                    <Grid
                        container
                        direction="row"
                        justifyContent="center"
                        alignItems="center"
                    >
                    
                        <Grid item xs>
                            <StyledButton variant="contained" href="/login">
                                Login
                            </StyledButton>
                
                            <StyledButton variant="contained" href="/register">
                                Register
                            </StyledButton>
                        </Grid>
                    </Grid>
                }
                </Paper>
                </div>
                 </Grid>
                 </Grid>
        </>
    );
}

export default SuccessPage;