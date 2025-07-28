import type { GetUserResponseAPI } from "@/types/user"

export const fetchUser = async (requestRole: string, token: string): Promise<GetUserResponseAPI> => {
    let queryString = ""
    if (requestRole) {
        const query_params = { role: requestRole }
        queryString = '?' + new URLSearchParams(query_params).toString();
    }

    const response = await fetch('http://localhost:80/api/user' + queryString, {
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        }
    });

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || "Failed to fetch user service");
    }

    const responseData: GetUserResponseAPI = await response.json();

    return {
        'user': responseData.user,
        'access_token': responseData.access_token,
        'refresh_token': responseData.refresh_token }
}

export const fetchUserDefault = async (): Promise<GetUserResponseAPI> => {
    const response = await fetch('http://localhost:80/api/user/show-default', {
        headers: {
            "Content-Type": "application/json"
        }
    });

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || "Failed to fetch user default");
    }

    const responseData: GetUserResponseAPI = await response.json();

    return {
        'user': responseData.user,
        'access_token': responseData.access_token,
        'refresh_token': responseData.refresh_token }
}