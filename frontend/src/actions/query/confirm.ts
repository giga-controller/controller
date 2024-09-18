"use server";

import { ConfirmRequest } from "@/types/actions/query/confirm";
import { QueryResponse, queryResponseSchema } from "@/types/actions/query/base";

import axios from "axios";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL;
const SERVICE_ENDPOINT = "api/query/confirm";

export async function confirmExecution(
  input: ConfirmRequest,
): Promise<QueryResponse> {
  try {
    const response = await axios.post(
      `${BACKEND_URL}/${SERVICE_ENDPOINT}`,
      input,
      { timeout: 40000 },
    );
    const queryResponse = queryResponseSchema.parse(response.data);

    return queryResponse;
  } catch (error) {
    console.error("Error in query endpoint");
    throw error;
  }
}
