import Button from "@mui/material/Button"
import Grid from "@mui/material/Grid"
import TextareaAutosize from "@mui/material/TextareaAutosize"

type SubscriptionFormProps = {
    handleSubmit : (e: React.FormEvent<HTMLFormElement>) => void
    handleReturn : () => void
    pageName : string
    titleValue : string
    aboutValue : string
    
}

export default function SubscriptionForm(props : SubscriptionFormProps){

    return (
            <div className='subscribe-form'>
            <p style={{textAlign: "center", marginBottom: "5px"}}> {props.pageName} </p>
            <form onSubmit={props.handleSubmit}>
            <Grid container rowSpacing={1}>   
                <Grid size={1.2}>
                    <p> Title </p>
                </Grid>
                <Grid size={10.8}>
                        <input id="title-input" defaultValue={props.titleValue} name="query" className='form-style' style={{width: "100%"}}/>
                </Grid>
                <Grid size={1.2}>
                    <p> About </p>
                </Grid>
                <Grid size={10.8}>
                    <TextareaAutosize id="description-input" className='form-style'
                        aria-label="minimum height"
                        minRows={3}
                        defaultValue={props.aboutValue}
                        style={{ width: "100%" }}
                        />
                </Grid>

                <Grid size={6}> <Button variant="contained" onClick={props.handleReturn}> Return </Button> </Grid>
                <Grid size={6}> <Button variant="contained" type="submit"   style={{textAlign:"right"}}> Submit </Button> </Grid>    
            </Grid>
              </form>
        </div>
        )
}