
import Button from '@mui/material/Button';
import Popover from '@mui/material/Popover';
import { useState } from 'react';

type SubscribeButtonProps = {
    onSubscribe: () => void;
}

export default function SubscribeButton({onSubscribe,}:SubscribeButtonProps) {
  const [count, setCount] = useState(0);



  return (
    <Button onClick={onSubscribe} variant="outlined" href="/newsubscription">
      New subscription
    </Button>
  );
}
