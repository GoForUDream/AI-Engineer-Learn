import axios from "axios";

import { environment } from "../config/environment";
import { toApiError } from "./ApiError";


export const apiClient = axios.create({
  baseURL: environment.apiUrl,
  timeout: 15_000,

  headers: {
    Accept: "application/json",
  },
});


apiClient.interceptors.response.use(
  (response) => response,
  (error: unknown) =>
    Promise.reject(toApiError(error)),
);