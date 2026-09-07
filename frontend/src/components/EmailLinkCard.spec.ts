import { afterEach, beforeEach, expect, it, vi } from 'vitest'
import { createApp, nextTick, type App } from 'vue'
import EmailLinkCard from './EmailLinkCard.vue'
import { groupsApi } from '../api/groups'

vi.mock('../api/groups', () => ({
  groupsApi: {
    emailLinkOptions: vi.fn(),
    requestEmailLink: vi.fn(),
    confirmEmailLink: vi.fn(),
    cancelEmailLink: vi.fn(),
  },
}))

let app: App | undefined
async function flush() {
  for (let i = 0; i < 8; i++) await nextTick()
}
async function mount() {
  const container = document.createElement('div')
  document.body.append(container)
  app = createApp(EmailLinkCard, { groupId: 'private-group' })
  app.mount(container)
  await flush()
}
async function click(label: string) {
  const button = [...document.querySelectorAll('button')].find(
    (item) => item.textContent?.trim() === label,
  )
  expect(button).toBeDefined()
  button!.click()
  await flush()
}
async function input(selector: string, value: string) {
  const element = document.querySelector<HTMLInputElement>(selector)!
  element.value = value
  element.dispatchEvent(new Event('input', { bubbles: true }))
  await flush()
}
async function submit() {
  document
    .querySelector('form')!
    .dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }))
  await flush()
}
async function requestCode() {
  await click('Conserva via email')
  await input('input[type=email]', 'anna@example.org')
  await submit()
}

beforeEach(() => {
  vi.resetAllMocks()
  localStorage.clear()
  sessionStorage.clear()
  vi.mocked(groupsApi.emailLinkOptions).mockResolvedValue({
    data: { enabled: true, privacy_url: 'https://equa.example/privacy' },
  } as never)
  vi.mocked(groupsApi.requestEmailLink).mockResolvedValue({
    data: { challenge_token: 'opaque-private-token', expires_in: 900 },
  } as never)
  vi.mocked(groupsApi.confirmEmailLink).mockResolvedValue({} as never)
  vi.mocked(groupsApi.cancelEmailLink).mockResolvedValue({} as never)
})
afterEach(() => {
  app?.unmount()
  app = undefined
  document.body.replaceChildren()
})

it('is opt-in and sends the link only after confirmation, without persistent browser data', async () => {
  await mount()
  expect(document.querySelector('form')).toBeNull()
  expect(groupsApi.requestEmailLink).not.toHaveBeenCalled()
  await requestCode()
  expect(groupsApi.requestEmailLink).toHaveBeenCalledExactlyOnceWith(
    'private-group',
    'anna@example.org',
  )
  expect(groupsApi.confirmEmailLink).not.toHaveBeenCalled()
  expect(document.activeElement).toBe(document.querySelector('input[inputmode=numeric]'))
  await input('input[inputmode=numeric]', '123456')
  await submit()
  expect(groupsApi.confirmEmailLink).toHaveBeenCalledExactlyOnceWith(
    'private-group',
    'opaque-private-token',
    '123456',
  )
  expect(document.body.textContent).toContain('Link inviato!')
  expect(document.body.textContent).not.toContain('anna@example.org')
  expect(localStorage.length).toBe(0)
  expect(sessionStorage.length).toBe(0)
})

it('can skip without subscribing or sending anything', async () => {
  await mount()
  await click('Conserva via email')
  await click('Per ora no')
  expect(document.querySelector('form')).toBeNull()
  expect(groupsApi.requestEmailLink).not.toHaveBeenCalled()
})

it('cancels pending verification when changing address', async () => {
  await mount()
  await requestCode()
  await click('Cambia email o richiedi un nuovo codice')
  expect(groupsApi.cancelEmailLink).toHaveBeenCalledExactlyOnceWith(
    'private-group',
    'opaque-private-token',
  )
  expect(document.querySelector('input[type=email]')).not.toBeNull()
})

it.each([false, 'offline'])(
  'does not block the group when email is unavailable (%s)',
  async (availability) => {
    if (availability === false)
      vi.mocked(groupsApi.emailLinkOptions).mockResolvedValue({ data: { enabled: false } } as never)
    else vi.mocked(groupsApi.emailLinkOptions).mockRejectedValue(new Error('offline'))
    await mount()
    expect(document.querySelector('section')).toBeNull()
  },
)

it('preserves the code form after a wrong code and offers a new request after expiry', async () => {
  await mount()
  await requestCode()
  await input('input[inputmode=numeric]', '123456')
  vi.mocked(groupsApi.confirmEmailLink).mockRejectedValueOnce({
    response: { status: 400, data: { detail: 'Codice non corretto.' } },
  })
  await submit()
  expect(document.querySelector('[role=alert]')?.textContent).toContain('Codice non corretto.')
  expect(document.querySelector('input[inputmode=numeric]')).not.toBeNull()
  vi.mocked(groupsApi.confirmEmailLink).mockRejectedValueOnce({
    response: { status: 410, data: { detail: 'Codice scaduto.' } },
  })
  await submit()
  expect(document.querySelector('input[type=email]')).not.toBeNull()
  expect(document.querySelector('[role=alert]')?.textContent).toContain('Codice scaduto.')
})

it('shows rate limiting and prevents duplicate requests during delivery', async () => {
  let reject!: (reason: unknown) => void
  vi.mocked(groupsApi.requestEmailLink).mockReturnValue(
    new Promise((_, fail) => {
      reject = fail
    }),
  )
  await mount()
  await requestCode()
  await submit()
  expect(groupsApi.requestEmailLink).toHaveBeenCalledTimes(1)
  reject({ response: { status: 429, data: { detail: 'Troppe richieste.' } } })
  await flush()
  expect(document.querySelector('[role=alert]')?.textContent).toContain('Troppe richieste.')
  expect(document.querySelector<HTMLButtonElement>('button[type=submit]')?.disabled).toBe(false)
})

it('cancels a request that finishes after the panel was closed', async () => {
  let resolve!: (response: never) => void
  vi.mocked(groupsApi.requestEmailLink).mockReturnValue(
    new Promise((done) => {
      resolve = done
    }),
  )
  await mount()
  await requestCode()
  app!.unmount()
  app = undefined
  resolve({ data: { challenge_token: 'late-private-token', expires_in: 900 } } as never)
  await flush()
  expect(groupsApi.cancelEmailLink).toHaveBeenCalledExactlyOnceWith(
    'private-group',
    'late-private-token',
  )
})
