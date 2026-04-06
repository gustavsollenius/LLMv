'use client'
import { useState } from 'react';
import SubscribeButton from './SubscribeButton';
import Button from '@mui/material/Button';
import Popover from '@mui/material/Popover';
import Grid from '@mui/material/Grid';

export default function BottomBarSubcribe()
{
   



    return (
        <>
            <div> 
                <Grid container mt={2}> 
                <Grid size={6}>
                 <Button variant="contained" href={"/"} > Return </Button> 
                </Grid>
                <Grid size={6} style={{textAlign: "right"}}>
                <Button variant="contained" href={"/newsubscription"} > New subscription </Button> 
                </Grid>
                </Grid>
            </div>
        </>
    )
}