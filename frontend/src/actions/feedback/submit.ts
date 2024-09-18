"use server";

import { FeedbackRequest } from "@/types/actions/feedback/form";

import axios from "axios";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL;
const SERVICE_ENDPOINT = "api/feedback";

export async function submitFeedback(input: FeedbackRequest) {
  try {
    await axios.post(`${BACKEND_URL}/${SERVICE_ENDPOINT}`, input);
  } catch (error) {
    console.error(error);
    throw error;
  }
}
