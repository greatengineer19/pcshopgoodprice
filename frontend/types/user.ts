export type UserRole = "buyer" | "seller";

export interface User {
    id: number
    fullname: string
    username: string
    role: string
}

export interface GetUserResponseAPI {
    user: User
    access_token: string
    refresh_token: string
}