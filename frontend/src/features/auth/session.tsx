"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import {
  QueryClient,
  QueryClientProvider,
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import { AuthError, getIdentity, login, logout, type Identity } from "./api";

const key = ["session"];
type SessionState =
  "checking" | "authenticated" | "anonymous" | "network-error" | "server-error";
type Session = {
  state: SessionState;
  identity: Identity | null;
  pending: boolean;
  error: Error | null;
  signIn: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
  retry: () => void;
};
const SessionContext = createContext<Session | null>(null);

export function useSession(): Session {
  const session = useContext(SessionContext);
  if (!session) throw new Error("SessionProvider is required");
  return session;
}

export function SessionProvider({ children }: { children: ReactNode }) {
  const cache = useQueryClient();
  const [changing, setChanging] = useState(false);
  const query = useQuery({
    queryKey: key,
    queryFn: ({ signal }) => getIdentity(signal),
    retry: false,
    enabled: !changing,
    refetchInterval: 60_000,
  });
  const signIn = useMutation({
    mutationFn: ({ email, password }: { email: string; password: string }) =>
      login(email, password),
    retry: false,
  });
  const signOut = useMutation({ mutationFn: logout, retry: false });

  useEffect(() => {
    if (!query.data) return;
    const timer = setTimeout(
      () => {
        void cache.invalidateQueries({ queryKey: key });
      },
      Math.max(0, Date.parse(query.data.expires_at) - Date.now()),
    );
    return () => clearTimeout(timer);
  }, [query.data, cache]);

  async function change(action: "login" | "logout", email = "", password = "") {
    setChanging(true);
    signIn.reset();
    signOut.reset();
    await cache.cancelQueries();
    try {
      const identity =
        action === "login"
          ? await signIn.mutateAsync({ email, password })
          : (await signOut.mutateAsync(), null);
      cache.clear();
      cache.setQueryData(key, identity);
    } finally {
      setChanging(false);
    }
  }

  const state: SessionState =
    changing || query.isPending
      ? "checking"
      : query.isError
        ? query.error instanceof AuthError && query.error.status === 0
          ? "network-error"
          : "server-error"
        : query.data
          ? "authenticated"
          : "anonymous";
  return (
    <SessionContext.Provider
      value={{
        state,
        identity: state === "authenticated" ? query.data! : null,
        pending: changing,
        error: signIn.error ?? signOut.error,
        signIn: (email, password) => change("login", email, password),
        signOut: () => change("logout"),
        retry: () => {
          void query.refetch();
        },
      }}
    >
      {children}
    </SessionContext.Provider>
  );
}

export function SessionRoot({ children }: { children: ReactNode }) {
  const [client] = useState(() => new QueryClient());
  return (
    <QueryClientProvider client={client}>
      <SessionProvider>{children}</SessionProvider>
    </QueryClientProvider>
  );
}
