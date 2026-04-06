import FlashCard from '@/components/FlashCard';
import TopBarSubscriptions from '@/components/BottomBarAddSubscription';
import SubscribePage from './subscribe/page';
import './style.css'
import Link from 'next/link';
import Button from '@mui/material/Button';

export default function Home() {
  const flash = {
    title: 'Iran Houthis',
    time: '17:43',
    text: 'Houthi forces may expand conflict into the Red Sea, threatening major shipping routes near Bab al-Mandab. Increased risk to global trade and oil transport as tensions rise.',
    url: '/article/1',
  };

  return <> 

  <div className="title"> NEWS FLASHER </div>
  <div className='center-div'>
  <Button variant="contained" href="/subscribe"> Subscriptions </Button>
  <FlashCard flash={flash} /> 
  <FlashCard flash={flash} /> 
  </div>

  </>;
}