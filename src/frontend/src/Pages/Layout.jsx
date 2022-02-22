import React from 'react';
import Container from '@mui/material/Container';
import routes from '../Routes';

const Features = () => {

  return (
        <Container component="section" maxWidth="lg" sx={{ p: 2}} >
              {routes}
        </Container>
  );
};

export default Features;