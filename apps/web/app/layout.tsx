import type { Metadata } from 'next';
import { Nunito, Inter } from 'next/font/google';

import './globals.css';
import { Providers } from './providers';

const inter = Inter({ subsets: ['latin'] });
const nunito = Nunito({ subsets: ['latin'], variable: '--font-sans' });

export const metadata: Metadata = {
  title: 'Intelligent Test Prep Platform',
  description: 'AI-Powered Test Preparation for IELTS, GRE, TOEFL',
  icons: {
    icon: '/favicon.ico',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="theme-color" content="#ffffff" />
      </head>
      <body className={`${inter.className} ${nunito.variable}`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
