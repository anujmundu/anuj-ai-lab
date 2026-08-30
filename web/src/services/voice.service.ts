import { api } from "@/lib/api";

export interface TranscribeResponse {
    text: string;
    language?: string;
    duration?: number;
}

export const voiceService = {
    async synthesize(text: string, voice = "af_sarah"): Promise<Blob> {
        const response = await api.post("/voice/synthesize", {
            text,
            voice,
        }, {
            responseType: "blob",
        });
        return response.data;
    },

    async transcribe(audioFile: File): Promise<TranscribeResponse> {
        const formData = new FormData();
        formData.append("file", audioFile);
        const { data } = await api.post<TranscribeResponse>("/voice/transcribe", formData, {
            headers: {
                "Content-Type": "multipart/form-data",
            },
        });
        return data;
    },
};
