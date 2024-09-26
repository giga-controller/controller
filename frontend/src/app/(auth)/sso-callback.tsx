"use client";

import { useEffect } from 'react';
import { useRouter } from 'next/router';
import { useClerk } from '@clerk/nextjs';

export default function SSOCallback() {
  const router = useRouter();
  const { handleRedirectCallback } = useClerk();

  useEffect(() => {
    async function handleCallback() {
      try {
        await handleRedirectCallback({
          afterSignInUrl: '/',
          afterSignUpUrl: '/',
        });
      } catch (error) {
        console.error('Error handling SSO callback:', error);
        router.push('/error');
      }
    }

    if (router.isReady) {
      handleCallback();
    }
  }, [router.isReady, handleRedirectCallback, router]);

  return <div>Processing authentication...</div>;
};