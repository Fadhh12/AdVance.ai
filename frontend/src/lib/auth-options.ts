import type { AuthOptions } from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";
import GoogleProvider from "next-auth/providers/google";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type BackendUser = {
  id: string;
  email: string;
  name: string;
  plan_id: string | null;
  ai_generation_used: number;
};

type BackendTokenResponse = {
  access_token: string;
  user: BackendUser;
};

// FastAPI is the source of truth for accounts/passwords (FR-01) — NextAuth here is
// just the session/cookie layer on top. Credentials login and Google sign-in both end
// up calling a backend /auth endpoint and stashing the returned JWT in the session.
export const authOptions: AuthOptions = {
  session: { strategy: "jwt" },
  pages: {
    signIn: "/login",
  },
  providers: [
    CredentialsProvider({
      name: "Email & Password",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) return null;

        const response = await fetch(`${API_BASE_URL}/auth/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            email: credentials.email,
            password: credentials.password,
          }),
        });
        if (!response.ok) return null;

        const data: BackendTokenResponse = await response.json();
        return {
          id: data.user.id,
          email: data.user.email,
          name: data.user.name,
          accessToken: data.access_token,
        };
      },
    }),
    GoogleProvider({
      // Kosong sampai user isi .env.local — tombol "Masuk dengan Google" belum
      // fungsional tanpa ini (lihat PROGRESS.md Phase 1).
      clientId: process.env.GOOGLE_OAUTH_CLIENT_ID ?? "",
      clientSecret: process.env.GOOGLE_OAUTH_CLIENT_SECRET ?? "",
    }),
  ],
  callbacks: {
    async jwt({ token, account, user }) {
      if (account?.provider === "credentials" && user) {
        token.accessToken = user.accessToken;
      }

      if (account?.provider === "google" && account.id_token) {
        const response = await fetch(`${API_BASE_URL}/auth/oauth/google`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ id_token: account.id_token }),
        });
        if (response.ok) {
          const data: BackendTokenResponse = await response.json();
          token.accessToken = data.access_token;
          token.name = data.user.name;
          token.email = data.user.email;
        }
      }

      return token;
    },
    async session({ session, token }) {
      if (token.accessToken) {
        session.accessToken = token.accessToken;
      }
      return session;
    },
  },
};
