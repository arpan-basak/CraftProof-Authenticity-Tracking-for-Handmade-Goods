// Single source of truth for the backend base URL.
//
// Trailing slashes are stripped deliberately: a stray one turns every call
// into "...onrender.com//auth/login", which 404s — exactly what broke login,
// signup and certificate lookups on the Render deployment when VITE_API_URL
// was set with a trailing slash.
export const API = (import.meta.env.VITE_API_URL || 'http://localhost:8002').replace(/\/+$/, '')
