"use client"

import { useState, useEffect, useCallback, useRef } from "react"
import { User, UserRole, GetUserResponseAPI } from "@/types/user"
import { fetchUser, fetchUserDefault } from "@/lib/user-service";

export function useUser() {
    const [role, setRole] = useState<UserRole>("seller")
    const [isLoadingUser, setIsLoadingUser] = useState(true)
    const [cartChanged, setCartChanged] = useState(false)
    const [user, setUser] = useState<User | undefined>(undefined);
    const SECRET_KEY_NAME = 'secret_key';
    const REFRESH_KEY_NAME = 'refresh_key';

    useEffect(() => {
        const loadInitialUser = async () => {
            if (user == undefined) {
                const token = localStorage.getItem(SECRET_KEY_NAME);
                let response: GetUserResponseAPI;
    
                if (token) {
                    response = await fetchUser("", token)
                } else {
                    response = await fetchUserDefault()                
                }

                const responseUser = response.user;
                setUser(responseUser);

                const userRole: UserRole = responseUser.role.toLowerCase() as UserRole;
                setRole(userRole);

                localStorage.setItem(SECRET_KEY_NAME, response.access_token);
                localStorage.setItem(REFRESH_KEY_NAME, response.refresh_token);

                setIsLoadingUser(false)
            }
        }

        loadInitialUser()
    }, []);

    return { role, setRole, user, setUser, cartChanged, setCartChanged, isLoadingUser }
}