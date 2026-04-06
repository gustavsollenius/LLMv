'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import '../../style.css';
import SubscriptionForm from '@/components/SubscriptionForm';

type SubscriptionItem = [number, string, string];

export default function SubscribePage() {
  const params = useParams();
  const id = params.id as string;



  const [subscription, setSubscription] = useState<SubscriptionItem | null>(null);

  // avoiding doing this on every render.
  useEffect(() => {
    async function getSubscriptionInformation() {
      try {
        const res = await fetch(`http://localhost:8000/newsubscription/${id}`);

        if (!res.ok) {
          throw new Error(`Response status: ${res.status}`);
        }

        const data: SubscriptionItem = await res.json();
        setSubscription(data);

        
      } catch (error: unknown) {
        if (error instanceof Error) {
          console.error(error.message);
        } else {
          console.error(error);
        }
      }
    }

    if (id) {
      getSubscriptionInformation();
    }
  }, [id]);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();

    const form = e.currentTarget;

    const title_value = (form.querySelector("#title-input") as HTMLInputElement).value;
    const description_value = (form.querySelector("#description-input") as HTMLInputElement).value;

    await fetch(`http://localhost:8000/editsubscription/${id}`, {
      method: "POST", // or PUT
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        title: title_value,
        description: description_value
      }),
    });

    window.location.href = "http://localhost:3000/subscribe";
  }

  function handleReturn() {
    window.location.href = "http://localhost:3000/subscribe";
  }

  console.log("aasdd",subscription)
  return (
    
    <>
      <div className="title"> NEWS FLASHER </div>
      <div className='center-div'>
        <SubscriptionForm
          handleSubmit={handleSubmit}
          handleReturn={handleReturn}
          pageName={"Edit subscription"}
          titleValue={subscription ? subscription[1] : ""}
          aboutValue={subscription ? subscription[2] : ""}
        />
      </div>
    </>
  );
}