import type { DefaultSession, DefaultUser } from "next-auth";
import type { DefaultJWT } from "next-auth/jwt";

// Backend FastAPI JWT (FR-01), carried through NextAuth's session/token so API calls
// can attach it as a Bearer token. See src/lib/auth-options.ts.
declare module "next-auth" {
  interface User extends DefaultUser {
    accessToken?: string;
  }

  interface Session extends DefaultSession {
    accessToken?: string;
  }
}

declare module "next-auth/jwt" {
  interface JWT extends DefaultJWT {
    accessToken?: string;
  }
}
