export const THEME_STORAGE_KEY = 'equa-theme'

export function prefersDarkTheme(): boolean {
  try {
    const savedTheme = localStorage.getItem(THEME_STORAGE_KEY)
    if (savedTheme === 'dark' || savedTheme === 'light') return savedTheme === 'dark'
  } catch {
    // Privacy settings can make Web Storage unavailable.
  }

  return window.matchMedia?.('(prefers-color-scheme: dark)').matches ?? false
}

export function applyTheme(dark: boolean): void {
  document.documentElement.classList.toggle('dark', dark)
}

export function saveTheme(dark: boolean): void {
  try {
    localStorage.setItem(THEME_STORAGE_KEY, dark ? 'dark' : 'light')
  } catch {
    // The selected theme still applies for this page when storage is unavailable.
  }
}
