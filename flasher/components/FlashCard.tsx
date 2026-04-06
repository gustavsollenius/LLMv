import '../app/style.css';
import FlashButton from './FlashButton';

type Flash = {
  title: string;
  time: string;
  text: string;
  url: string;
};

export default function FlashCard({ flash }: { flash: Flash }) {
  return (
  <>
  <div className="flash-card"> 
    <div className="upper-bar">
      <div className="flash-card-title">
        <p>{flash.title}</p>
      </div>
      <div className="flash-card-clock">
        <p>{flash.time}</p>
      </div>
    </div>

    <div className="center-text-box">
      <p>{flash.text}</p>
    </div>

    <div className="lower-bar">
      <div className="flash-card-title" />
      <div className="flash-card-clock">
        <FlashButton url={flash.url} />
      </div>
    </div>
    </div>
    </>
  );
}