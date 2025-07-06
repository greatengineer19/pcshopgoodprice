// "use client"

// import { createContext, useContext, useState, useEffect, type ReactNode } from "react"
// import type { UserRole, User } from "@/types/user"

// interface UserContextType {
//     user: User | null
//     role: UserRole
//     setRole: (role: UserRole) => void
//     isLoading: boolean
// }

// const UserContext = createContext<UserContextType | undefined>(undefined)

// export function UserProvider({ children}: { children: ReactNode }) {
//     const [isLoading, setIsLoading] = useState(true)
//     const [user, setUser] = useState<User | null>(null)
//     const [role, setRole] = useState<UserRole>("seller")

//     // Simulate loading user data
//     useEffect(() => {
//         const loadUser = async () => {
//             // In a real app this would be an API call
//             setTimeout(() => {
//                 setUser({
//                     id: "user-1",
//                     username: "john-doe",
//                     fullname: "John Doe",
//                     role: "seller"
//                 })
//                 setIsLoading(false)
//             }, 500)
//         }

//         loadUser()
//     }, [])

//     useEffect(() => {
//         if (typeof window !== "undefined") {
//             localStorage.setItem("userRole", role)
//         }
//     }, [role])

//     // Load role from localStorage on initial load
//     useEffect(() => {
//         if (typeof window !== "undefined") {
//             const savedRole = localStorage.getItem("userRole") as UserRole | null
//             if (savedRole && (savedRole === "seller" || savedRole === "buyer")) {
//                 setRole(savedRole)
//             }
//         }
//     }, [])

//     return <UserContext.Provider value={{ user, role, setRole, isLoading}}>{children}</UserContext.Provider>
// }

// export function userContext() {
//     const context = useContext(UserContext)
//     if (context === undefined) {
//         throw new Error("userContext must be used within a UserProvider")
//     }
//     return context
// }
