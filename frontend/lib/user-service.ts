import type { GetUserResponseAPI } from "@/types/user"

export const fetchUser = async (requestRole: string): Promise<GetUserResponseAPI> => {
    const query_params = { role: requestRole }
    const queryString = '?' + new URLSearchParams(query_params).toString();
    const response = await fetch('http://localhost:8080/api/user' + queryString);

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