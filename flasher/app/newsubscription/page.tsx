
'use client';


import '../style.css'
import SubscriptionForm from '@/components/SubscriptionForm';

export default function SubscribePage(){


    async function handleSubmit(e: React.FormEvent<HTMLFormElement>){
        e.preventDefault();

        const form = e.currentTarget;

        const title_value = (form.querySelector("#title-input") as HTMLInputElement).value;
        const description_value = (form.querySelector("#description-input") as HTMLInputElement).value;

     
        await fetch("http://localhost:8000/newsubscription", {
        method: "POST",
        headers: {
        "Content-Type": "application/json",
        },
        body: JSON.stringify({
            title: title_value,
            description: description_value
        }),
    });
    

    window.location.href = "http://localhost:3000/subscribe"

        
    }

    function handleReturn(){
     window.location.href = "http://localhost:3000/subscribe"

    }
    
    return  (
    <> 
    
    <div className="title"> NEWS FLASHER </div>
    <div className='center-div'>
        <SubscriptionForm handleSubmit={handleSubmit} handleReturn={handleReturn} pageName={"New subscription"} titleValue='' aboutValue=''/> 
    </div>
    </>
    )

}