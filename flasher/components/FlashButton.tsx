'use client';

import Button from '@mui/material/Button';
import Link from 'next/link';

export default function FlashButton({ url }: { url: string }) {
  return (
    <Button component={Link} href={url} variant="text">
      Read more
    </Button>
  );
}