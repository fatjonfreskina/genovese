import { afterEach, beforeEach, expect, it, vi } from 'vitest'
import { createApp, nextTick, type App } from 'vue'
import { createMemoryHistory, createRouter } from 'vue-router'
import GroupGrowthCard from './GroupGrowthCard.vue'

let app: App | undefined
const share = vi.fn()
const copy = vi.fn()
async function flush() {
  for (let i = 0; i < 8; i++) await nextTick()
}
async function mount() {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/', component: { template: '<div />' } }],
  })
  await router.push('/')
  const container = document.createElement('div')
  document.body.append(container)
  app = createApp(GroupGrowthCard).use(router)
  app.mount(container)
  await flush()
}
async function click() {
  document.querySelector<HTMLButtonElement>('button')!.click()
  await flush()
}

beforeEach(() => {
  vi.resetAllMocks()
  window.history.replaceState({}, '', '/group/private-uuid?created=1')
  Object.defineProperty(navigator, 'share', { configurable: true, value: share })
  Object.defineProperty(navigator, 'clipboard', { configurable: true, value: { writeText: copy } })
  share.mockResolvedValue(undefined)
  copy.mockResolvedValue(undefined)
})
afterEach(() => {
  app?.unmount()
  app = undefined
  document.body.replaceChildren()
  window.history.replaceState({}, '', '/')
})

it('shares only the public homepage and offers a blank new group', async () => {
  await mount()
  await click()
  expect(share).toHaveBeenCalledTimes(1)
  expect(share.mock.calls[0]![0].url).toBe(`${window.location.origin}/`)
  expect(JSON.stringify(share.mock.calls[0])).not.toContain('private-uuid')
  const links = [...document.querySelectorAll<HTMLAnchorElement>('a')]
  expect(
    links.find((link) => link.textContent === 'Crea un nuovo gruppo')?.getAttribute('href'),
  ).toBe('/')
  expect(
    decodeURIComponent(links.find((link) => link.href.startsWith('https://wa.me'))!.href),
  ).not.toContain('/group/')
})

it('falls back to clipboard without the private URL', async () => {
  Object.defineProperty(navigator, 'share', { configurable: true, value: undefined })
  await mount()
  await click()
  expect(copy).toHaveBeenCalledTimes(1)
  expect(copy.mock.calls[0]![0]).not.toContain('private-uuid')
  expect(document.querySelector('[role=status]')?.textContent).toContain('Messaggio copiato')
})

it('does not copy anything if sharing is cancelled', async () => {
  share.mockRejectedValue({ name: 'AbortError' })
  await mount()
  await click()
  expect(copy).not.toHaveBeenCalled()
  expect(document.querySelector('[role=status]')).toBeNull()
})

it('keeps a selectable public URL if native share and clipboard fail', async () => {
  share.mockRejectedValue(new Error('unavailable'))
  copy.mockRejectedValue(new Error('denied'))
  await mount()
  await click()
  expect(document.querySelector<HTMLInputElement>('input')?.value).toBe(
    `${window.location.origin}/`,
  )
  expect(document.querySelector('[role=status]')?.textContent).toContain('manualmente')
})
