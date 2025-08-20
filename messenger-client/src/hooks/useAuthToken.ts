import { useEffect, useState } from "react";

export function useAuthToken() {
	const [token, setToken] = useState<string | null>(() =>
		localStorage.getItem("access_token")
	);

	useEffect(() => {
		const onStorage = (e: StorageEvent) => {
			if (e.key === "access_token")
        setToken(localStorage.getItem("access_token"));
		}
		window.addEventListener("storage", onStorage);
    return () => window.removeEventListener("storage", onStorage);
	}, [])
	const save = (t: string) => {
    localStorage.setItem("access_token", t);
    setToken(t);
  };
  const clear = () => {
    localStorage.removeItem("access_token");
    setToken(null);
	};
	 return { token, save, clear };

}
