import http from "k6/http";
import { check } from "k6";

export const options = { vus: 50, duration: "30s" };

export default function () {
  const res = http.get("http://localhost:8080/ping", {
    headers: { "x-api-key": `user-${__VU}` },
  });
  check(res, { "ok or limited": (r) => r.status === 200 || r.status === 429 });
}