export const handleApiError = async (response: Response, showErrorToast: (message: string) => void) => {
    try {
        const data = await response.json();
        let errorMessage = data.message || data.detail || 'An error occurred';
        
        switch (response.status) {
            case 400:
                errorMessage = data.detail || 'Invalid request. Please check your input.';
                break;
            case 401:
                errorMessage = 'Unauthorized. Please log in again.';
                break;
            case 403:
                errorMessage = 'You do not have permission to perform this action.';
                break;
            case 404:
                errorMessage = data.detail || 'The requested resource was not found.';
                break;
            case 409:
                errorMessage = data.detail || 'This operation conflicts with existing data.';
                break;
            case 500:
                errorMessage = 'Internal server error. Please try again later.';
                break;
            default:
                if (response.status >= 500) {
                    errorMessage = 'Server error. Please try again later.';
                } else {
                    errorMessage = data.detail || 'An unexpected error occurred.';
                }
        }
        
        showErrorToast(errorMessage);
        throw new Error(errorMessage);
    } catch (e) {
        // If we can't parse the JSON response
        const fallbackMessage = `Error (${response.status}): ${response.statusText}`;
        showErrorToast(fallbackMessage);
        throw new Error(fallbackMessage);
    }
};