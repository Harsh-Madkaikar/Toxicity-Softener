// IMPORTANT: after deploying the API, replace this URL with your public HTTPS API URL.
// Example: https://toxicity-softener-api.onrender.com/analyze
const API_URL = "https://REPLACE-WITH-YOUR-API.onrender.com/analyze";

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (!request || request.type !== "ANALYZE_TEXT") return false;

    const message = typeof request.message === "string" ? request.message : "";
    if (!message.trim()) {
        sendResponse({ success: false, error: "Empty message" });
        return false;
    }

    fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: message.slice(0, 5000) })
    })
    .then(async response => {
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.error || `HTTP ${response.status}`);
        sendResponse({ success: true, result: data });
    })
    .catch(error => {
        console.error("Toxicity Softener API request failed:", error);
        sendResponse({ success: false, error: error.message });
    });

    return true;
});
