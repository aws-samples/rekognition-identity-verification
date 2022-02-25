import * as React from 'react';
import AppBar from '@mui/material/AppBar';
import Grid from '@mui/material/Grid';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import RIVMenu from "./Menu";

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#1976d2',
    },
  },
});

function Header(props) {

    return (
            <ThemeProvider theme={darkTheme}>
            <AppBar color="primary" position="sticky" elevation={10} >
                <Toolbar sx={{ pt: 1, pb: 2}} >
                    <Grid container spacing={1} alignItems="center">
                        <Grid item>
                            <img width='41px' height='24px' src={'data:image/svg+xml;base64,PHN2ZyBpZD0iTGF5ZXJfMSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB4bWxuczp4bGluaz0iaHR0cDovL3d3dy53My5vcmcvMTk5OS94bGluayIgdmlld0JveD0iMCAwIDgwIDQ3Ij48c3R5bGU+LnN0MHtjbGlwLXBhdGg6dXJsKCNTVkdJRF8zXyk7fTwvc3R5bGU+PGRlZnM+PHBhdGggaWQ9IlNWR0lEXzFfIiBkPSJNNTkuMSAyMi44Yy43LjQgMS45LjkgMy4yIDEuMiAxLjMuMyAzLjUuNiA0LjkuNiAxLjQgMCAyLjYtLjIgMy44LS41IDEuMS0uMyAyLjEtLjggMy0xLjUuOC0uNiAxLjUtMS40IDEuOS0yLjMuNS0uOS43LTIuMS43LTMuMiAwLTEuNC0uNC0yLjYtMS4yLTMuNy0uOC0xLjEtMi4yLTEuOS00LjEtMi41bC0zLjgtMS4yYy0xLjQtLjUtMi40LS44LTIuOS0xLjNzLS44LTEuMS0uOC0xLjhjMC0xLjEuNC0xLjggMS4zLTIuMy44LS41IDItLjYgMy41LS42IDEuOSAwIDMuOS42IDUuNCAxLjMuNS4yLjguMyAxIC4zLjQgMCAuNi0uMy42LS44bC4xLTEuNWMwLS43LS40LTEuMy0uOS0xLjUtLjQtLjMtMS45LS44LTMuMS0xLjEtLjUtLjEtMS4xLS4yLTEuNy0uMy0uNi0uMS0xLjItLjEtMS44LS4xLTEuMiAwLTIuMy4xLTMuNC40LTEuMS4zLTIgLjgtMi44IDEuNC0uOC42LTEuNCAxLjMtMS45IDIuMi0uNS44LS43IDEuOC0uNyAyLjkgMCAxLjQuNCAyLjYgMS4zIDMuOC45IDEuMiAyLjMgMS45IDQuMyAyLjZsMy45IDEuMmMxLjMuNCAyLjIuOSAyLjcgMS40LjUuNS43IDEuMS43IDEuOCAwIDEuMS0uNSAxLjktMS40IDIuNS0uOS41LTIuMi44LTMuOS44LTEuMSAwLTQtLjQtNy4xLTEuNi0uMy0uMS0uNS0uMi0uNy0uMy0uMi0uMS0uMy0uMS0uNS0uMS0uNCAwLS42LjQtLjYuOXYxLjNjMCAuMi4xLjUuMi43LjEuNC40LjYuOC45em0tMjcuNi0uMmMuMi41LjMuOS42IDEgLjIuMi42LjMgMSAuM2gyLjNjLjUgMCAuOS0uMSAxLjEtLjMuMi0uMi40LS41LjUtMS4xbDQuMS0xNi44IDQuMSAxNi44Yy4xLjUuMy45LjUgMS4xLjIuMi42LjMgMS4xLjNoMi4zYy41IDAgLjgtLjEgMS0uMy4yLS4yLjQtLjUuNi0xbDYuNC0yMC4yYy4xLS4zLjItLjUuMi0uNnYtLjRjMC0uNC0uMi0uNi0uNy0uNmgtMi41Yy0uNSAwLS44LjEtMSAuMy0uMi4yLS40LjUtLjUgMUw0OCAxOS41IDQzLjggMmMtLjEtLjUtLjMtLjktLjUtMS0uMi0uMi0uNi0uMy0xLjEtLjNoLTIuMWMtLjUgMC0uOS4xLTEuMS4zLS4yLjItLjQuNS0uNSAxbC00LjEgMTcuM0wyOS45IDJjLS4yLS41LS4zLS45LS41LTEtLjItLjItLjYtLjMtMS0uM2gtMi42Yy0uNCAwLS43LjItLjcuNiAwIC4yLjEuNS4yIDEuMWw2LjIgMjAuMnpNMTUuMSAxMC40Yy0xLS4xLTEuOS0uMi0yLjgtLjItMi43IDAtNC45LjctNi41IDItMS42IDEuNC0yLjQgMy4yLTIuNCA1LjQgMCAyLjEuNyAzLjggMiA1IDEuMyAxLjMgMy4xIDEuOSA1LjMgMS45IDMuMSAwIDUuNy0xLjIgNy44LTMuNi4zLjYuNiAxLjEuOCAxLjUuMy40LjYuOCAxIDEuMi4yLjIuNS40LjguNC4yIDAgLjQtLjEuNy0uMmwxLjctMS4xYy4zLS4yLjUtLjUuNS0uOCAwLS4yLS4xLS40LS4yLS42LS40LS43LS43LTEuMy0uOS0xLjktLjItLjYtLjMtMS40LS4zLTIuM1Y4LjZjMC0yLjktLjctNS0yLjItNi40QzE4LjkuOCAxNi42LjEgMTMuNC4xYy0xLjUgMC0yLjguMi00LjEuNS0xLjQuMi0yLjUuNi0zLjQgMS4xLS40LjItLjYuNC0uOC41LS4xLjItLjIuNS0uMiAxdjEuM2MwIC41LjIuOC42LjguMSAwIC4yIDAgLjQtLjEuMiAwIC41LS4yLjktLjMgMS0uNCAxLjktLjcgMi45LS45IDEtLjIgMS45LS4zIDIuOS0uMyAyIDAgMy41LjQgNC4zIDEuMi44LjcgMS4zIDIuMSAxLjMgNC4xdjEuOWMtMS4xLS4yLTIuMS0uNC0zLjEtLjV6bTMuMSA0LjZjMCAuOS0uMSAxLjYtLjMgMi4zLS4yLjYtLjUgMS4yLS45IDEuNy0uNy44LTEuNiAxLjQtMi41IDEuNy0xIC4zLTEuOS41LTIuNy41LTEuMiAwLTIuMS0uMy0yLjgtLjktLjctLjYtMS0xLjUtMS0yLjggMC0xLjMuNC0yLjMgMS4zLTMgLjktLjcgMi4yLTEuMSA0LTEuMS44IDAgMS42LjEgMi41LjIuOS4xIDEuNy4zIDIuNC40djF6Ii8+PC9kZWZzPjxkZWZzPjxwYXRoIGlkPSJTVkdJRF8yXyIgZD0iTTcxIDM1LjNjLTkuOCA0LjEtMjAuNSA2LjEtMzAuMiA2LjEtMTQuNCAwLTI4LjMtMy45LTM5LjYtMTAuMy0xLS42LTEuNy40LS45IDEuMkMxMC44IDQxLjUgMjQuNiA0NyAzOS45IDQ3YzEwLjkgMCAyMy42LTMuNCAzMi40LTkuNyAxLjUtMSAuMi0yLjYtMS4zLTJ6bTguNy00LjljLTEtMS4yLTkuMi0yLjItMTQuMiAxLjMtLjguNS0uNiAxLjMuMiAxLjIgMi44LS4zIDkuMS0xLjEgMTAuMi4zIDEuMSAxLjQtMS4yIDcuMi0yLjMgOS44LS4zLjguNCAxLjEgMS4xLjUgNC43LTMuOCA2LTExLjkgNS0xMy4xeiIvPjwvZGVmcz48dXNlIHhsaW5rOmhyZWY9IiNTVkdJRF8xXyIgb3ZlcmZsb3c9InZpc2libGUiIGZpbGw9IiNGRkYiLz48dXNlIHhsaW5rOmhyZWY9IiNTVkdJRF8yXyIgb3ZlcmZsb3c9InZpc2libGUiIGZpbGw9IiNGODk5MUQiLz48Y2xpcFBhdGggaWQ9IlNWR0lEXzNfIj48dXNlIHhsaW5rOmhyZWY9IiNTVkdJRF8xXyIgb3ZlcmZsb3c9InZpc2libGUiLz48L2NsaXBQYXRoPjxjbGlwUGF0aCBpZD0iU1ZHSURfNF8iIGNsYXNzPSJzdDAiPjx1c2UgeGxpbms6aHJlZj0iI1NWR0lEXzJfIiBvdmVyZmxvdz0idmlzaWJsZSIvPjwvY2xpcFBhdGg+PC9zdmc+'} alt="recipe thumbnail" />
                        </Grid>
                        <Grid item xs >
                            <Typography color="inherit" variant="h5" component="h1">
                                Rekognition Identity Verification
                            </Typography>
                        </Grid>
                        <Grid>

                        <RIVMenu/>
                            
                        </Grid>
                    </Grid>
                </Toolbar>
            </AppBar>
            </ThemeProvider>
    );
}

export default Header;