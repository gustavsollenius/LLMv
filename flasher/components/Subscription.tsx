import IconButton from "@mui/material/IconButton";
import DeleteIcon from "@mui/icons-material/Delete";
import EditIcon from '@mui/icons-material/Edit';

type subscriptionInfo = {
    id : number,
    title : string,
    onDelete: (id: number) => void;
    onEdit: (id: number) => void;
}




export default function Subscription({id, title, onDelete, onEdit} : subscriptionInfo){

    return(
          <div className='subscription'>  {title}
                <div className='subscription-right'> 
                      <IconButton aria-label="edit" onClick={() => onEdit(id)}>
                        <EditIcon />
                    </IconButton> 
                    <IconButton aria-label="delete" onClick={() => onDelete(id)}>
                        <DeleteIcon />
                    </IconButton> 

                </div>
            </div>
    )
}