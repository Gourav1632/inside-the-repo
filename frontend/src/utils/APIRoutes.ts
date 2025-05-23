export const host = process.env.NEXT_PUBLIC_HOST || "http://127.0.0.1:8000";
export const repoAnalysisRoute = `${host}/api/analyze`
export const fileAnalysisRoute = `${host}/api/file`
export const askAssistantRoute = `${host}/api/ask`