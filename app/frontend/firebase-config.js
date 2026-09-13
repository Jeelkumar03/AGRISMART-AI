// ═══════════════════════════════════════════════════════════
//  Firebase setup — shared by login.html and index.html.
//  Web API keys are public by design; access is controlled by
//  Firebase security rules, not by hiding this file.
// ═══════════════════════════════════════════════════════════
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import { getAuth } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js";
import { getFirestore } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js";

const firebaseConfig = {
  apiKey: "AIzaSyD2s4s5xYyCmJtDq2JMIC5PezZkoF16OJQ",
  authDomain: "agrismart-ai-90171.firebaseapp.com",
  projectId: "agrismart-ai-90171",
  storageBucket: "agrismart-ai-90171.firebasestorage.app",
  messagingSenderId: "236188050336",
  appId: "1:236188050336:web:8ad9ed26bf28e2c2cefac5"
};

const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);
export const db = getFirestore(app);

/** Flask backend origin. */
export const API_BASE = `http://${window.location.hostname}:5000`;

/** Used when a location can't be resolved. */
export const FALLBACK_COORDS = { lat: 23.02, lon: 72.57, label: "Ahmedabad, Gujarat" };

/** Firebase error codes are not user-facing; translate them. */
export function authMessage(code) {
  const map = {
    "auth/invalid-credential":      "That email and password don't match. Check both and try again.",
    "auth/invalid-email":           "That email address isn't valid.",
    "auth/wrong-password":          "That password isn't right. Try again.",
    "auth/user-not-found":          "No account with that email yet. Create one instead.",
    "auth/email-already-in-use":    "This email is already registered. Log in instead.",
    "auth/weak-password":           "Use a password of at least 6 characters.",
    "auth/too-many-requests":       "Too many attempts. Wait a minute, then try again.",
    "auth/network-request-failed":  "No internet connection. Check your network and retry.",
    "auth/invalid-api-key":         "Firebase isn't configured. Check firebase-config.js.",
    "auth/operation-not-allowed":   "Enable Email/Password sign-in in the Firebase console.",
    "auth/configuration-not-found": "Enable Email/Password sign-in in the Firebase console."
  };
  return map[code] || "Something went wrong. Try again.";
}

/** Every glass panel picks up a highlight that follows the pointer. */
export function enableGlassHighlight() {
  document.addEventListener("pointermove", e => {
    const card = e.target.closest?.(".glass");
    if (!card) return;
    const r = card.getBoundingClientRect();
    card.style.setProperty("--mx", `${e.clientX - r.left}px`);
    card.style.setProperty("--my", `${e.clientY - r.top}px`);
  });
}

export const $ = id => document.getElementById(id);

export function showNotice(el, message, kind = "error") {
  el.className = `notice notice--${kind} show`;
  el.textContent = message;
}

export function hideNotice(el) { el.classList.remove("show"); }

export function setLoading(btn, loading, idleLabel) {
  const label = btn.querySelector(".btn-label");
  btn.disabled = loading;
  label.innerHTML = loading ? `<span class="spinner"></span>Working…` : idleLabel;
}
