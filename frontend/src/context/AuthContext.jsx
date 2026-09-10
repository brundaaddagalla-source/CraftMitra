import { createContext, useContext, useState, useCallback } from "react";
import { api } from "../api/client";

const AuthContext = createContext(null);

const TOKEN_KEY = "craftmitra_token";
const USER_KEY = "craftmitra_user";

function readStoredUser() {
  const stored = localStorage.getItem(USER_KEY);
  return stored ? JSON.parse(stored) : null;
}

export function AuthProvider({ children }) {
  const [token, setTokenState] = useState(() => localStorage.getItem(TOKEN_KEY));
  const [user, setUserState] = useState(readStoredUser);
  const [loading, setLoading] = useState(false);

  // Writes to localStorage immediately (not through a useEffect) so that
  // the very next API call in the same signup/login flow already has
  // the token available - no race condition waiting for a re-render.
  const setToken = useCallback((value) => {
    if (value) {
      localStorage.setItem(TOKEN_KEY, value);
    } else {
      localStorage.removeItem(TOKEN_KEY);
    }
    setTokenState(value);
  }, []);

  const setUser = useCallback((value) => {
    if (value) {
      localStorage.setItem(USER_KEY, JSON.stringify(value));
    } else {
      localStorage.removeItem(USER_KEY);
    }
    setUserState(value);
  }, []);

  // One-shot flow for launch: create the user, log them in, then create
  // their artisan profile - all three backend calls, one form.
  const signup = useCallback(
    async (formValues) => {
      setLoading(true);
      try {
        const {
          name,
          email,
          phone,
          password,
          location,
          state,
          district,
          craftType,
          preferredLanguage,
        } = formValues;

        const newUser = await api.post(
          "/users",
          { name, email, phone, password },
          { auth: false }
        );

        const { access_token } = await api.post(
          "/auth/login",
          { email, password },
          { auth: false }
        );
        setToken(access_token);

        const artisan = await api.post("/artisans", {
          user_id: newUser.id,
          location,
          state,
          district,
          preferred_language: preferredLanguage,
          craft_type: craftType,
        });

        // Product creation (and everything downstream of it) needs the
        // artisan's profile id, not the user id - stash it on the
        // stored user object so the rest of the app can read
        // `user.artisanId` without an extra lookup.
        const userWithArtisan = { ...newUser, artisanId: artisan.id };
        setUser(userWithArtisan);
        return userWithArtisan;
      } finally {
        setLoading(false);
      }
    },
    [setToken, setUser]
  );

  const login = useCallback(
    async (email, password) => {
      setLoading(true);
      try {
        const { access_token } = await api.post(
          "/auth/login",
          { email, password },
          { auth: false }
        );
        setToken(access_token);

        const me = await api.get("/auth/me");
        const artisan = await api.get("/artisans/me");
        const userWithArtisan = { ...me, artisanId: artisan.id };
        setUser(userWithArtisan);
        return userWithArtisan;
      } finally {
        setLoading(false);
      }
    },
    [setToken, setUser]
  );

  const logout = useCallback(() => {
    setToken(null);
    setUser(null);
  }, [setToken, setUser]);

  return (
    <AuthContext.Provider
      value={{
        token,
        user,
        loading,
        signup,
        login,
        logout,
        isAuthenticated: !!token,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside AuthProvider");
  return context;
}