"use client"

import { useState, useEffect, useCallback, useRef } from "react"
// import { userContext } from "@/context/user-context"
import { User, UserRole, GetUserResponseAPI } from "@/types/user"
import { fetchUser } from "@/lib/user-service";

export function useUser() {
    const [role, setRole] = useState<UserRole>("seller")
    const [user, setUser] = useState<User | undefined>(undefined);

    useEffect(() => {
        const loadInitialUser = async () => {
            if (user == undefined) {
                const response: GetUserResponseAPI = await fetchUser("seller")
                const responseUser = response.user;
                setUser(responseUser)
            }
        }

        loadInitialUser()
    }, []);

    return { role, setRole, user, setUser }
}