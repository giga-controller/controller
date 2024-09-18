export const API_KEY_QUERY_KEY = "apiKey";
export const CHAT_HISTORY_QUERY_KEY = "chatHistoryKey";
export const INTEGRATION_AUTH_STATUS_QUERY_KEY = (name: string) => {
  return `is${name}Authenticated`;
};
