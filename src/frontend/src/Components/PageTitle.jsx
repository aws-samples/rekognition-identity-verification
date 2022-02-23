import Typography from '@mui/material/Typography';
import Grid from '@mui/material/Grid';

const Title = ({ pagetitle, error }) => {
      return (
                <Grid item xs={12} sx={{p: 1}} >
                    <Typography variant="h4" gutterBottom component="div" fontWeight= '800' >
                        {pagetitle}
                    </Typography>
                    {error && (
                            <Typography variant="subtitle2" align='center' color="red" gutterBottom component="div">
                                {error}
                            </Typography>
                        )}
                </Grid>
                );
};

export default Title;