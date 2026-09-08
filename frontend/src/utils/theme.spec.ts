import { afterEach, describe, expect, it, vi } from 'vitest'
import { applyTheme, prefersDarkTheme, saveTheme, THEME_STORAGE_KEY } from './theme'

describe('theme preference', () => {
  afterEach(() => {
    vi.restoreAllMocks()
    vi.unstubAllGlobals()
    localStorage.clear()
    document.documentElement.classList.remove('dark')
  })

  it('uses and applies the saved preference', () => {
    localStorage.setItem(THEME_STORAGE_KEY, 'dark')

    expect(prefersDarkTheme()).toBe(true)
    applyTheme(true)
    expect(document.documentElement.classList.contains('dark')).toBe(true)
  })

  it('falls back to the system theme when storage is denied', () => {
    vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
      throw new DOMException('Storage denied', 'SecurityError')
    })
    vi.stubGlobal(
      'matchMedia',
      vi.fn(() => ({ matches: true })),
    )

    expect(prefersDarkTheme()).toBe(true)
  })

  it('does not fail when saving is denied', () => {
    vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
      throw new DOMException('Storage denied', 'SecurityError')
    })

    expect(() => saveTheme(true)).not.toThrow()
  })
})
