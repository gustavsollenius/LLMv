'use client';

import { useEffect, useState } from 'react';
import Subscription from '../../components/Subscription';
import BottomBar from './BottomBar';


type SubscriptionItem = [number, string, string];

export default function SubscribePage() {



  const [subscriptions, setSubscriptions] = useState<SubscriptionItem[]>([]);

  // render then when fetch has ococcured re render (useEffect) with the new state.
  useEffect(() => {
    async function fetchSubscriptions() {
      try {
        const res = await fetch("http://localhost:8000/newsubscription");

        if (!res.ok) {
          throw new Error(`Response status: ${res.status}`);
        }

        const result: SubscriptionItem[] = await res.json();

        setSubscriptions(result);

      } catch (error: unknown) {
        if (error instanceof Error) {
          console.error(error.message);
        } else {
          console.error(error);
        }
      }
    }

    fetchSubscriptions();
  }, []);

  async function onDelete(id: number){


          try {
        const res = await fetch(`http://localhost:8000/newsubscription/${id}`,{
          method: "DELETE"
        });

        if (!res.ok) {
          throw new Error(`Response status: ${res.status}`);
        }

      } catch (error: unknown) {
        if (error instanceof Error) {
          console.error(error.message);
        } else {
          console.error(error);
        }
      }

    setSubscriptions(prev => prev.filter(([itemId]) => itemId !== id));
}



async function onEdit(id: number){

    window.location.href=`http://localhost:3000/editsubscription/${id}`
 
}

  return (

   

    <>
      <div className="title"> NEWS FLASHER </div>
      <div className='center-div'>
        <div className='subscriptions' style={{ padding: "10px" }}>

          {subscriptions.map(([id, title, description]) => (
            <Subscription key={id} title={title} onDelete={onDelete} onEdit={onEdit} id={id} />
          ))}

          <BottomBar />
        </div>
      </div>
    </>
  );
}